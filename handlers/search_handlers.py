# handlers/search_handlers.py
from aiogram import F, types, filters, Router, fsm
import logging

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from db import get_db, beautiful_form_output_with_percent, User, get_user_by_tgid
from middlewares import UserCreatedMiddleware
from states import SearchStates
from ai import MatchAi
from utils import pay

search_router = Router()
search_router.message.outer_middleware(UserCreatedMiddleware())

reaction_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="👍"), types.KeyboardButton(text="👎")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder=""
)

# async def send_next_match(message: types.Message, state: fsm.context.FSMContext):
#     data = await state.get_data()
#     seen: list[int] = data.get("seen_results", [])

#     async for session in get_db():
#         searcher = await get_user_by_tgid(session, tgid=message.from_user.id)
#         if not searcher:
#             await message.answer("Профиль не найден")
#             return

#         ai = MatchAi()
#         stmt = select(User).where(User.tgid != searcher.tgid, User.is_active)
#         all_users = (await session.execute(stmt)).scalars().all()

#         # sort descending by compatibility
#         ranked = sorted(
#             all_users,
#             key=lambda u: ai.get_percent(
#                 desc1=searcher.description,
#                 desc2=u.description,
#                 interest1=searcher.interests or [],
#                 interest2=u.interests or []
#             ),
#             reverse=True
#         )

#         # pick the first they haven't seen yet
#         next_pair = None
#         for u in ranked:
#             if u.tgid not in seen:
#                 next_pair = (u, ai.get_percent(
#                     desc1=searcher.description,
#                     desc2=u.description,
#                     interest1=searcher.interests or [],
#                     interest2=u.interests or []
#                 ))
#                 break

#         if not next_pair:
#             logging.info(f"No more matches for {message.from_user.id}")
#             await message.answer("Анкет для показа не осталось.", reply_markup=types.ReplyKeyboardRemove())
#             return False

#         user, percent = next_pair
#         seen.append(user.tgid)
#         await state.update_data(seen_results=seen)
#         await state.update_data(current_user=user.tgid)

#         output = beautiful_form_output_with_percent(user=user, percent=percent/100)
#         if isinstance(output, list):
#             await message.answer_media_group(output)
#             return True
#         else:
#             await message.answer(output)
#             return True
#         return False # only one match per call

async def send_next_match(message: types.Message, state: fsm.context.FSMContext):
    data = await state.get_data()
    seen: list[int] = data.get("seen_results", [])

    async for session in get_db():
        searcher = await get_user_by_tgid(session, tgid=message.from_user.id)
        if not searcher:
            await message.answer("Профиль не найден")
            await state.update_data(current_user=None)  # Очищаем current_user
            return False

        ai = MatchAi()
        stmt = select(User).where(User.tgid != searcher.tgid, User.is_active)
        all_users = (await session.execute(stmt)).scalars().all()

        # sort descending by compatibility
        ranked = sorted(
            all_users,
            key=lambda u: ai.get_percent(
                desc1=searcher.description,
                desc2=u.description,
                interest1=searcher.interests or [],
                interest2=u.interests or []
            ),
            reverse=True
        )

        # pick the first they haven't seen yet
        next_pair = None
        for u in ranked:
            if u.tgid not in seen:
                next_pair = (u, ai.get_percent(
                    desc1=searcher.description,
                    desc2=u.description,
                    interest1=searcher.interests or [],
                    interest2=u.interests or []
                ))
                break

        if not next_pair:
            logging.info(f"No more matches for {message.from_user.id}")
            await message.answer("Анкет для показа не осталось.", reply_markup=types.ReplyKeyboardRemove())
            await state.update_data(current_user=None)  # Очищаем current_user
            return False

        user, percent = next_pair
        seen.append(user.tgid)
        await state.update_data(seen_results=seen)
        await state.update_data(current_user=user.tgid)

        output = beautiful_form_output_with_percent(user=user, percent=percent/100)
        if isinstance(output, list):
            await message.answer_media_group(output)
        else:
            await message.answer(output)
        return True

# @search_router.message(filters.Command("search"))
# async def cmd_start_search(message: types.Message, state: fsm.context.FSMContext):
#     await state.update_data(seen_results=[])
#     await state.set_state(SearchStates.in_search)
#     logging.info(f"/search by {message.from_user.id}")
#     await message.answer("Поиск лучшей анкеты может занять время. Подождите пожалуйста, бот не завис.")
#     match_exist = await send_next_match(message, state)
#     if match_exist:
#         await message.answer("Выберите действие на клавиатуре:", reply_markup=reaction_kb)
#     else:
#         await message.answer("Вы можете начать поиск заново с помощью /search !", reply_markup=types.ReplyKeyboardRemove())

@search_router.message(filters.Command("search"))
async def cmd_start_search(message: types.Message, state: fsm.context.FSMContext):
    await state.update_data(seen_results=[], current_user=None)  # Очищаем seen_results и current_user
    await state.set_state(SearchStates.in_search)
    logging.info(f"/search by {message.from_user.id}")
    await message.answer("Поиск лучшей анкеты может занять время. Подождите пожалуйста, бот не завис.")
    match_exist = await send_next_match(message, state)
    if match_exist:
        await message.answer("Выберите действие на клавиатуре:", reply_markup=reaction_kb)
    else:
        await message.answer("Вы можете начать поиск заново с помощью /search !", reply_markup=types.ReplyKeyboardRemove())

@search_router.message(SearchStates.in_search, filters.Command("exit_search"))
async def cmd_exit_search(message: types.Message, state: fsm.context.FSMContext):
    await state.clear()
    logging.info(f"/exit_search by {message.from_user.id}")
    await message.answer("Поиск завершен. Чтобы снова начать, нажмите /search")


@search_router.message(SearchStates.in_search, F.text == "👎")
async def cmd_next_search(message: types.Message, state: fsm.context.FSMContext):
    logging.info(f"Next match request by {message.from_user.id}")
    await message.answer("Поиск лучшей анкеты может занять время. Подождите пожалуйста, бот не завис.")
    match_exist = await send_next_match(message, state)
    if match_exist:
        await message.answer("Выберите действие на клавиатуре:", reply_markup=reaction_kb)
    else:
        await message.answer("Вы можете начать поиск заново с помощью /search !", reply_markup=types.ReplyKeyboardRemove())


@search_router.message(SearchStates.in_search, F.text == "👍")
async def like_handler(message: types.Message, state: fsm.context.FSMContext):
    user_id = await state.get_value("current_user")
    if not user_id:
        logging.warning(f"No current_user_id in state for {message.from_user.id}")
        await message.answer("Ошибка: не удалось найти текущую анкету. Попробуйте снова /search", reply_markup=types.ReplyKeyboardRemove())
        return

    async for session in get_db():
        user = await get_user_by_tgid(session=session, tgid=user_id)
        if not user:
            logging.error(f"User {user_id} disappeared from DB")
            await message.answer("Эта анкета больше недоступна. Пробуем другую...")
            match_exist = await send_next_match(message, state)
            if match_exist:
                await message.answer("Выберите действие на клавиатуре:", reply_markup=reaction_kb)
            else:
                await message.answer("Вы можете начать поиск заново с помощью /search !", reply_markup=types.ReplyKeyboardRemove())
            return

        ok = await pay(message, state)
        if ok:
            logging.info(f"Оплата успешна: {message.from_user.id} купил контакт @{user.username}")
            await message.answer(f"Спасибо за приобретение. Приятного общения!\n@{user.username}", reply_markup=types.ReplyKeyboardRemove())
        else:
            logging.error(f"Оплата провалилась. Покупатель @{message.from_user.username}, контакт @{user.username}")
            await message.answer("Оплата не прошла. Если произошла ошибка, сделайте /report и опишите проблему", reply_markup=types.ReplyKeyboardRemove())

