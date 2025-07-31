from aiogram import Router, types, F, filters, fsm
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import get_db, get_user_by_tgid, Update
from data import cfg
from handlers.create_handlers import start_profile_creation, done_kb
from handlers.interest_handlers import build_interests_page
from states.edit import EditStates

edit_router = Router()

INTERESTS = cfg.INTERESTS

edit_kb = types.InlineKeyboardMarkup(inline_keyboard=[
    [
        types.InlineKeyboardButton(text="Изменить имя", callback_data="edit_name"),
        types.InlineKeyboardButton(text="Изменить возраст", callback_data="edit_age")
    ],
    [
        types.InlineKeyboardButton(text="Изменить описание", callback_data="edit_desc")
    ],
    [
        types.InlineKeyboardButton(text="Изменить интересы", callback_data="edit_interests"),
        types.InlineKeyboardButton(text="Изменить медиа", callback_data="edit_media")
    ],
    [
        types.InlineKeyboardButton(text="Активность профиля", callback_data="edit_toggle_active"),
        types.InlineKeyboardButton(text="Редактировать всю анкету", callback_data="edit_full")
    ],
    [
        types.InlineKeyboardButton(text="Отменить", callback_data="edit_cancel")
    ]
])

@edit_router.message(filters.Command("edit"))
async def cmd_edit_start(message: types.Message):
    await message.answer("Выберите, что хотите изменить:", reply_markup=edit_kb)

@edit_router.callback_query(F.data == "edit_name")
async def callback_edit_name(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    await callback.message.edit_reply_markup()
    await callback.message.answer("Введите новое имя:")
    await state.set_state(EditStates.name)

@edit_router.message(EditStates.name)
async def process_edit_name(message: types.Message, state: fsm.context.FSMContext):
    name = message.text.strip()
    async for session in get_db():
        user = await get_user_by_tgid(session=session, tgid=message.from_user.id)
        upd = Update(session=session, user=user)
        await upd.name(name)
    await message.answer(f"Имя обновлено: {name}")
    await state.clear()

@edit_router.callback_query(F.data == "edit_age")
async def callback_edit_age(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    await callback.message.edit_reply_markup()
    await callback.message.answer("Введите новый возраст:")
    await state.set_state(EditStates.age_required)

@edit_router.message(EditStates.age_required)
async def process_edit_age_required(message: types.Message, state: fsm.context.FSMContext):
    if not message.text.isdigit():
        await message.answer("Возраст должен быть числом.")
        return

    age = int(message.text)
    if not (18 <= age <= 120):
        await message.answer("Возраст обязан быть в диапазоне от 18 до 120")
        return

    async for session in get_db():
        user = await get_user_by_tgid(session=session, tgid=message.from_user.id)
        upd = Update(session=session, user=user)
        await upd.age(age=age)
    await message.answer(f"Возраст обновлен: {age}")
    await state.clear()

# @edit_router.message(EditStates.age_range)
# async def process_edit_age_range(message: types.Message, state: fsm.context.FSMContext):
#     if not message.text.isdigit():
#         await message.answer("Диапазон должен быть числом.")
#         return
    

# @edit_router.callback_query(F.data == "edit_gender")
# async def callback_edit_gender(callback: types.CallbackQuery, state: fsm.context.FSMContext):
#     await callback.message.edit_reply_markup()
#     kb = types.InlineKeyboardMarkup(inline_keyboard=[
#         [types.InlineKeyboardButton(text="Парень", callback_data="gender_actual_male"),
#          types.InlineKeyboardButton(text="Девушка", callback_data="gender_actual_female")]
#     ])
#     await callback.message.answer("Выберите ваш пол:", reply_markup=kb)
#     await state.set_state(EditStates.gender_actual)

# @edit_router.callback_query(F.data.startswith("gender_actual_"))
# async def process_edit_gender_actual(callback: types.CallbackQuery, state: fsm.context.FSMContext):
#     actual = callback.data.split("_")[-1] == "male"
#     await state.update_data(gender_actual=actual)
#     await callback.message.edit_reply_markup()
#     kb = types.InlineKeyboardMarkup(inline_keyboard=[
#         [types.InlineKeyboardButton(text="Парней", callback_data="gender_search_male"),
#          types.InlineKeyboardButton(text="Девушек", callback_data="gender_search_female")],
#         [types.InlineKeyboardButton(text="Неважно", callback_data="gender_search_any")]
#     ])
#     await callback.message.answer("Укажите кого ищете:", reply_markup=kb)
#     await state.set_state(EditStates.gender_search)

# @edit_router.callback_query(F.data.startswith("gender_search_"))
# async def process_edit_gender_search(callback: types.CallbackQuery, state: fsm.context.FSMContext):
#     code = callback.data.split("_")[-1]
#     mapping = {"male": 1, "female": 2, "any": 3}
#     search_code = mapping.get(code, 3)
#     data = await state.get_data()
#     actual = data.get("gender_actual")
#     async for session in get_db():
#         user = await get_user_by_tgid(session=session, tgid=callback.from_user.id)
#         upd = Update(session=session, user=user)
#         await upd.gender_actual_and_search(actual, search_code)
#     await callback.message.edit_reply_markup()
#     await callback.message.answer("Пол и предпочтения поиска обновлены.")
#     await state.clear()

@edit_router.callback_query(F.data == "edit_desc")
async def callback_edit_desc(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    await callback.message.edit_reply_markup()
    await callback.message.answer("Введите новое описание:")
    await state.set_state(EditStates.desc)

@edit_router.message(EditStates.desc)
async def process_edit_desc(message: types.Message, state: fsm.context.FSMContext):
    text = message.text.strip()
    async for session in get_db():
        user = await get_user_by_tgid(session=session, tgid=message.from_user.id)
        upd = Update(session=session, user=user)
        await upd.desc(text)
    await message.answer("Описание обновлено.")
    await state.clear()

@edit_router.callback_query(F.data == "edit_interests")
async def callback_edit_interests(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    async for session in get_db():
        user = await get_user_by_tgid(session=session, tgid=callback.from_user.id)
        current = user.interests or []
    await state.update_data(selected_interests=current)
    markup = build_interests_page(page=0, selected=current)
    await callback.message.answer("Выберите интересы:", reply_markup=markup)
    await state.set_state(EditStates.interests)

@edit_router.callback_query(StateFilter(EditStates.interests), F.data.startswith("page:"))
async def paginate_edit_interests(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    data = await state.get_data()
    sel = data.get("selected_interests", [])
    page = int(callback.data.split(":")[1])
    markup = build_interests_page(page=page, selected=sel)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer()

@edit_router.callback_query(StateFilter(EditStates.interests), F.data.startswith("interest:"))
async def toggle_edit_interest(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    _, interest, page_str = callback.data.split(":", 2)
    page = int(page_str)
    data = await state.get_data()
    sel: list[str] = data.get("selected_interests", [])
    if interest in sel:
        sel.remove(interest)
    else:
        sel.append(interest)
    await state.update_data(selected_interests=sel)
    markup = build_interests_page(page=page, selected=sel)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer()

@edit_router.callback_query(StateFilter(EditStates.interests), F.data == "done_interests")
async def done_edit_interests(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    data = await state.get_data()
    sel: list[str] = data.get("selected_interests", [])
    if not sel:
        await callback.answer("❗ Выберите хотя бы один интерес!", show_alert=True)
        return
    async for session in get_db():
        user = await get_user_by_tgid(session=session, tgid=callback.from_user.id)
        upd = Update(session=session, user=user)
        await upd.interests(sel)
    await callback.message.answer(f"✅ Интересы обновлены: {', '.join(sel)}")
    await callback.answer()
    await state.clear()

@edit_router.callback_query(F.data == "edit_media")
async def callback_edit_media(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "Пришлите медиа (>=1 фото, до 2 фото и 1 видео). Нажмите Done для завершения.",
        reply_markup=done_kb
    )
    await state.set_state(EditStates.media)

@edit_router.message(EditStates.media, F.photo | F.video)
async def process_edit_media(message: types.Message, state: fsm.context.FSMContext):
    data = await state.get_data()
    coll = data.get("media", [])
    if message.photo:
        coll.append({"type": "photo", "file_id": message.photo[-1].file_id})
    elif message.video:
        coll.append({"type": "video", "file_id": message.video.file_id})
    photos = sum(1 for m in coll if m["type"] == "photo")
    videos = sum(1 for m in coll if m["type"] == "video")
    if videos > 1:
        coll.pop()
        await message.answer("Можно не более одного видео!")
    else:
        await state.update_data(media=coll)
        if photos >= 3 or (photos >= 2 and videos == 1):
            await message.answer("Медиа собрано.", reply_markup=types.ReplyKeyboardRemove())
            async for session in get_db():
                user = await get_user_by_tgid(session=session, tgid=message.from_user.id)
                upd = Update(session=session, user=user)
                await upd.media(coll)
            await state.clear()
        else:
            await message.answer(f"Сейчас: {photos} фото, {videos} видео.")

@edit_router.message(EditStates.media, F.text.casefold() == "done")
async def finish_edit_media(message: types.Message, state: fsm.context.FSMContext):
    data = await state.get_data()
    coll = data.get("media", [])
    if coll:
        async for session in get_db():
            user = await get_user_by_tgid(session=session, tgid=message.from_user.id)
            upd = Update(session=session, user=user)
            await upd.media(coll)
        await message.answer("Медиа обновлены.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer("Нужно хоть одно медиа.")

@edit_router.callback_query(F.data == "edit_toggle_active")
async def callback_toggle_active(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup()
    async for session in get_db():
        user = await get_user_by_tgid(session=session, tgid=callback.from_user.id)
        upd = Update(session=session, user=user)
        new = await upd.turn_active()
    status = "активен" if new.is_active else "неактивен"
    await callback.answer(f"Статус активности: {status}")

@edit_router.callback_query(F.data == "edit_full")
async def callback_edit_full(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    await callback.message.edit_reply_markup()
    await start_profile_creation(callback.message, state)

@edit_router.callback_query(F.data == "edit_cancel")
async def callback_edit_cancel(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup()
    await callback.message.answer("Редактирование отменено.")
