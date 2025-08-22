from aiogram import F, Router, filters, fsm, types
from aiogram.utils.media_group import MediaGroupBuilder
from states import ProfileStates
from colorama import Fore
import typing
import logging

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data import cfg
from db import (
    get_db, get_field, create_user, Update, 
    get_user_by_tgid, delete_user, Get, User,
    beautiful_form_output
)
from ufilters import NewUserFilter, TaCFilter, IsAdminFilter
from keyboards import agree_markup

create_router = Router()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS_PATH = cfg.TERMS_PATH

@create_router.message(NewUserFilter())
async def new_user(message: types.Message):
    tgid: int = message.from_user.id

    async for session in get_db():
        user = await create_user(
            session=session, 
            tgid=tgid,
            username=message.from_user.username,
            name=message.from_user.first_name)
        
        print(f"{Fore.BLUE}{user}{Fore.RESET}")
        logging.info(f"Created user: {user}")

        name = await get_field(session, tgid, "name") 
        if not name or name == "":
            name = await get_field(session, tgid, "username")

        name = name.capitalize() if (name and len(name) > 1) else "Пользователь"

        await message.answer(f"Добро пожаловать в HitoriLink, {name}!")
        await message.answer_document(
            document=types.FSInputFile(TERMS_PATH),
            caption=f"{name}, пожалуйста, подтвердите согласие с Условиями пользования ботом HitoriLink, а также с Политикой Конфиденциальности https://uylag.github.io/policy/",
            reply_markup=agree_markup
        )

@create_router.message(filters.Command("accept"))
async def resend_terms(message: types.Message):
    TERMS_PATH = cfg.TERMS_PATH
    await message.answer_document(
        document=types.FSInputFile(TERMS_PATH),
        caption="Вот условия пользования HitoriLink. Политика конфиденциальности: https://uylag.github.io/policy/ .\nПосле прочтения нажмите кнопку согласия.",
        reply_markup=agree_markup
    )

choice_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Зарегистрировать анкету")]
    ],
    one_time_keyboard=True,
    input_field_placeholder="Начните использование",
    resize_keyboard=True
)

@create_router.callback_query(F.data == "agree")
async def agreed_cmd(callback: types.CallbackQuery):
    async for session in get_db():
        user = await get_user_by_tgid(session, callback.from_user.id)
        upd = Update(
            session=session, 
            user=user
        )
        await upd.consent_to_share(agreement=True)
        logging.info(f"User {callback.from_user.id} agreed to terms")
        await callback.answer("Согласие принято")
        await callback.message.edit_reply_markup()
        await callback.message.answer(
            text="Приятного пользования ботом!",
            reply_markup=choice_kb
        )

@create_router.callback_query(F.data == "disagree")
async def disagreed_cmd(callback: types.CallbackQuery):
    async for session in get_db():
        user = await get_user_by_tgid(session, callback.from_user.id)
        upd = Update(
            session=session, 
            user=user
        )
        await upd.consent_to_share(agreement=False)
        logging.info(f"User {callback.from_user.id} disagreed to terms")
        await callback.answer("Отказано")
        await callback.message.edit_reply_markup()
        # await callback.message.answer(
        #     text="Доступ к боту ограничен. Вам доступно только чтение анкет, но Вы не можете делиться или получать юзернеймы.",
        #     reply_markup=choice_kb
        # )

@create_router.message(F.text.casefold() == "зарегистрировать анкету")
async def create_by_text(message: types.Message, state: fsm.context.FSMContext):
    await start_profile_creation(message, state)

@create_router.message(filters.Command("create"))
async def create_by_cmd(message: types.Message, state: fsm.context.FSMContext):
    await start_profile_creation(message, state)

async def start_profile_creation(message: types.Message, state: fsm.context.FSMContext):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=message.from_user.first_name)],
            [types.KeyboardButton(text="Unknown")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Ваше имя",
        one_time_keyboard=True
    )

    await message.answer("Введите имя", reply_markup=kb)
    await state.set_state(ProfileStates.name)

@create_router.message(ProfileStates.name)
async def handle_name_state(message: types.Message, state: fsm.context.FSMContext):
    name = message.text.strip()

    if len(name) < 1 or len(name) > 50:
        await message.answer("Имя введено неверно. Должно быть более одного символа и менее пятидесяти.")
        return

    await state.update_data(name=name)
    await message.answer(f"{name}? Отличное имя.\nВведите свой настоящий возраст.")
    await state.set_state(ProfileStates.age_required)

@create_router.message(ProfileStates.age_required)
async def handle_age_required_state(message: types.Message, state: fsm.context.FSMContext):
    if not message.text.isdigit():
        await message.answer("Возраст должен быть числом.")
        return

    age_required = int(message.text)

    if age_required > 120:
        await message.answer("Возраст введен неверно. Укажите свой настоящий возраст")
        return

    if age_required < 18:
        await message.answer("Вам запрещено пользоваться ботом по условиям принятого Вами договора.")
        async for session in get_db():
            user = await get_user_by_tgid(session=session, tgid=message.from_user.id)
            if user:
                upd = Update(session=session, user=user)
                await upd.ban()
                return

    await state.update_data(age_required=age_required)
    await message.answer("Расскажите о себе. Не более 600 символов.")
    await state.set_state(ProfileStates.desc)

# @create_router.message(ProfileStates.age_range)
# async def handle_age_range_state(message: types.Message, state: fsm.context.FSMContext):
#     if not message.text or not message.text.isdigit():
#         await message.answer("Введите число диапазона")
#         return

#     kb = types.InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 types.InlineKeyboardButton(text="Парень", callback_data="male"),
#                 types.InlineKeyboardButton(text="Девушка", callback_data="female")
#             ]
#         ]
#     )

#     age_range = int(message.text)
#     age_required = await state.get_value("age_required")
    
#     normal_range = age_range

#     if age_required >= 18:
#         while age_required - normal_range < 18:
#             normal_range -= 1

#     if normal_range != age_range:
#         message.answer(f"Вы установили неправомерный диапазон {age_range}. Мы скорректировали его под нормальный диапазон {normal_range}.")
#         age_range = normal_range

#     await state.update_data(age_range=age_range)
#     await message.answer(
#         "Укажите Ваш пол",
#         reply_markup=kb
#     )
#     await state.set_state(ProfileStates.gender_actual)

# @create_router.callback_query(ProfileStates.gender_actual)
# async def handle_gender_actual_state(callback: types.CallbackQuery, state: fsm.context.FSMContext):
#     gender: str = callback.data

#     kb = types.InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 types.InlineKeyboardButton(text="Парень", callback_data="male"),
#                 types.InlineKeyboardButton(text="Девушка", callback_data="female")
#             ],
#             [
#                 types.InlineKeyboardButton(text="Неважно", callback_data="dm"),
#             ]
#         ]
#     )

#     if gender == "male":
#         await state.update_data(gender_actual=True)
#     elif gender == "female":
#         await state.update_data(gender_actual=False)
#     else:
#         return

#     await callback.message.edit_reply_markup()
#     await callback.message.answer("Укажите какой пол ищете", reply_markup=kb)
#     await state.set_state(ProfileStates.gender_search)

# @create_router.callback_query(ProfileStates.gender_search)
# async def handle_gender_search_state(callback: types.CallbackQuery, state: fsm.context.FSMContext):
#     gender: str = callback.data

#     if gender == "male":
#         await state.update_data(gender_search=1)
#     elif gender == "female":
#         await state.update_data(gender_search=2)
#     elif gender == "dm":
#         await state.update_data(gender_search=3)
#     else:
#         return

#     await callback.message.edit_reply_markup()
#     await callback.message.answer("Расскажите о себе. Не более 600 символов.")
#     await state.set_state(ProfileStates.desc)

@create_router.message(ProfileStates.desc)
async def handle_desc_state(message: types.Message, state: fsm.context.FSMContext):
    if len(message.text) > 600:
        await message.answer("Анкета не должна быть длиннее 600 символов.")
        return

    await state.update_data(description=message.text)

    # await state.set_state(ProfileStates.interests)
    # await message.answer("Нажмите кнопку чтобы продолжить.", reply_markup=types.ReplyKeyboardMarkup(
    #     keyboard=[
    #         [types.KeyboardButton(text="Продолжить")]
    #     ], one_time_keyboard=True
    # ))

    await state.set_state(ProfileStates.interests)
    from handlers.interest_handlers import show_interests_page
    await show_interests_page(message, state)

done_kb = types.ReplyKeyboardMarkup(
    keyboard=[[types.KeyboardButton(text="Done")]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Отправьте медиа или нажмите Done"
)

async def send_summary(message: types.Message, state: fsm.context.FSMContext):
    data = await state.get_data()
    
    name = data.get("name", "Не указано")
    age_required = data.get("age_required", "Не указано")
    # age_range = data.get("age_range", "Не указано")
    # gender_actual = data.get("gender_actual")
    # gender_search = data.get("gender_search")
    description = data.get("description", "Не указано")
    interests = data.get("interests", [])
    media = data.get("media", [])

    # gender_actual_text = "Парень" if gender_actual else "Девушка"
    # if gender_search == 1:
    #     gender_search_text = "Парней"
    # elif gender_search == 2:
    #     gender_search_text = "Девушек"
    # elif gender_search == 3:
    #     gender_search_text = "Любой пол"
    # else:
    #     gender_search_text = "Не указан"

    # Подсчитываем количество медиа
    photos = sum(1 for m in media if m["type"] == "photo")
    videos = sum(1 for m in media if m["type"] == "video")

    # Формируем резюме анкеты
    summary = (
        f"Ваша анкета:\n"
        f"{name}, "
        f"{age_required}\n"
        # f"±{age_range}\n"
        f"{description}\n\n"
        f"Интересы: {', '.join(interests) if interests else 'Не указаны'}\n\n"
    )

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ Сохранить", callback_data="confirm_save"),
                types.InlineKeyboardButton(text="❌ Отменить", callback_data="confirm_cancel")
            ]
        ]
    )

    from aiogram.utils.media_group import MediaGroupBuilder
    media_group = MediaGroupBuilder(caption=summary)
    for _file in media:
        if _file["type"] == "photo":
            media_group.add_photo(media=_file["file_id"])
        elif _file["type"] == "video":
            media_group.add_video(media=_file["file_id"])

    if media:
        await message.answer_media_group(media=media_group.build())
        await message.answer("Хотите сохранить анкету?", reply_markup=kb)
    else:
        await message.answer("Хотите сохранить анкету?", reply_markup=kb)


@create_router.message(ProfileStates.media, F.photo | F.video)
async def handle_media(message: types.Message, state: fsm.context.FSMContext):
    data = await state.get_data()
    collected = data.get("media", [])

    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        media_type = "video"
    else:
        await message.answer("Пришлите фото или видео.")
        return

    collected.append({"type": media_type, "file_id": file_id})
    await state.update_data(media=collected)

    photos = sum(1 for m in collected if m["type"] == "photo")
    videos = sum(1 for m in collected if m["type"] == "video")

    # ❌ Больше одного видео нельзя
    if videos > 1:
        collected.pop()
        await state.update_data(media=collected)
        await message.answer("Можно прикрепить не более одного видео!")
        return

    if photos >= 3:
        await message.answer(
            f"✅ Загружено {photos} фото. Этого достаточно! Переходим к следующему шагу.\n",
            reply_markup=types.ReplyKeyboardRemove()
        )
        # await state.set_state(ProfileStates.confirm)
        # return
        await state.set_state(ProfileStates.confirm)
        await send_summary(message, state)
        return

    if photos >= 2 and videos == 1:
        await message.answer(
            f"✅ Загружено {photos} фото и {videos} видео. Этого достаточно! Переходим к следующему шагу.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        # await state.set_state(ProfileStates.confirm)
        # return
        await state.set_state(ProfileStates.confirm)
        await send_summary(message, state)
        return

    await message.answer(
        f"Сейчас загружено: {photos} фото, {videos} видео.\n"
        "Можете добавить ещё.\n"
        "Условия: 3 фото ИЛИ 2 фото + 1 видео. Либо нажмите Done чтобы закончить сейчас.",
        reply_markup=done_kb
    )

@create_router.message(ProfileStates.media, F.text.casefold() == "done")
async def finish_media(message: types.Message, state: fsm.context.FSMContext):
    data = await state.get_data()
    collected = data.get("media", [])

    photos = sum(1 for m in collected if m["type"] == "photo")
    videos = sum(1 for m in collected if m["type"] == "video")

    if photos >= 1 or videos >= 1:
        await message.answer("Медиа сохранены! Переходим к следующему шагу.", reply_markup=types.ReplyKeyboardRemove())
        await send_summary(message, state)
        await state.set_state(ProfileStates.confirm)
        # await message.answer("Нажмите кнопку чтобы продолжить.", reply_markup=types.ReplyKeyboardMarkup(
        # keyboard=[
        #     [types.KeyboardButton(text="Продолжить")]
        # ], one_time_keyboard=True
        # ))
    else:
        await message.answer("Нужно загрузить хотя бы одно фото или одно видео.", reply_markup=done_kb)

# @create_router.message(ProfileStates.confirm)
# async def confirm_form(message: types.Message, state: fsm.context.FSMContext):
#     data = await state.get_data()

    

@create_router.callback_query(ProfileStates.confirm, F.data == "confirm_cancel")
async def confirm_cancel_form(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup()
    await callback.message.answer("Вы отменили создание анкеты. Вы всегда можете ее создать нажав на /create .")

@create_router.callback_query(ProfileStates.confirm, F.data == "confirm_save")
async def confirm_save_form(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    data = await state.get_data()

    name = data.get("name", "Не указано")
    age_required = data.get("age_required", "Не указано")
    # age_range = data.get("age_range", "Не указано")
    # gender_actual = data.get("gender_actual")
    # gender_search = data.get("gender_search")
    description = data.get("description", "Не указано")
    interests = data.get("interests", [])
    media = data.get("media", [])

    async for session in get_db():
        user = await get_user_by_tgid(session=session, tgid=callback.from_user.id)
        upd = Update(session=session, user=user)
        await upd.update(
            name=name,
            age_required=age_required,
            # age_range=age_range,
            # gender_actual=gender_actual,
            # gender_search=gender_search,
            description=description,
            interests=interests,
            media=media
        )

    await callback.answer("Сохранено")
    await state.clear()
    await callback.message.edit_reply_markup()
    await callback.message.answer("Анкета успешно сохранена")

@create_router.message(filters.Command("profile"))
async def profile_cmd(message: types.Message):
    tgid: int = message.from_user.id

    async for session in get_db():
        user: User = await get_user_by_tgid(session=session, tgid=tgid)
        if Get.is_profile_complete(user=user):
            output = beautiful_form_output(user)
            if isinstance(output, list):
                await message.answer_media_group(output)
            else:
                await message.answer(output)
        else:
            await message.answer("Создайте профиль с помощью команды /create")
