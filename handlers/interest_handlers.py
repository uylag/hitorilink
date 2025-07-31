from aiogram import types, F, Router, fsm
from aiogram.filters import StateFilter

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from states import ProfileStates
from data import cfg

INTERESTS = cfg.INTERESTS

ITEMS_PER_PAGE = 9
ROWS = 3
interest_router = Router()

def build_interests_page(page: int, selected: list[str]) -> types.InlineKeyboardMarkup:
    total_pages = (len(INTERESTS) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    current_items = INTERESTS[start:end]

    while len(current_items) < ITEMS_PER_PAGE:
        current_items.append("❌")

    rows = []
    for i in range(ROWS):
        row = []
        for j in range(3):
            name = current_items[i*3 + j]
            if name == "❌":
                row.append(types.InlineKeyboardButton(text="❌", callback_data="noop"))
            else:
                # Добавляем отметку выбранного
                label = f"✅ {name}" if name in selected else name
                # row.append(types.InlineKeyboardButton(text=label, callback_data=f"interest:{name}"))
                row.append(types.InlineKeyboardButton(
                   text=label,
                   callback_data=f"interest:{name}:{page}"
                ))
        rows.append(row)

    # Нижняя панель управления
    nav_row = []
    if page > 0:
        nav_row.append(types.InlineKeyboardButton(text="⬅️", callback_data=f"page:{page-1}"))
    else:
        nav_row.append(types.InlineKeyboardButton(text="❌", callback_data="noop"))

    nav_row.append(types.InlineKeyboardButton(text="✅ Готово", callback_data="done_interests"))

    if page < total_pages - 1:
        nav_row.append(types.InlineKeyboardButton(text="➡️", callback_data=f"page:{page+1}"))
    else:
        nav_row.append(types.InlineKeyboardButton(text="❌", callback_data="noop"))

    rows.append(nav_row)

    return types.InlineKeyboardMarkup(inline_keyboard=rows)

@interest_router.message(ProfileStates.interests)
async def show_interests_page(message: types.Message, state: fsm.context.FSMContext):
    await state.update_data(selected_interests=[])
    markup = build_interests_page(page=0, selected=[])
    await message.answer("Выберите интересы кнопками ниже:", reply_markup=markup)

@interest_router.callback_query(StateFilter(ProfileStates.interests), F.data.startswith("page:"))
async def paginate_interests(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    data = await state.get_data()
    selected = data.get("selected_interests", [])
    page = int(callback.data.split(":")[1])
    await callback.message.edit_reply_markup(reply_markup=build_interests_page(page, selected))
    await callback.answer()

@interest_router.callback_query(StateFilter(ProfileStates.interests), F.data.startswith("interest:"))
async def toggle_interest(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    # interest = callback.data.split(":")[1]
    # data = await state.get_data()
    # selected = data.get("selected_interests", [])
    _, interest, page_str = callback.data.split(":", 2)
    page = int(page_str)
    data = await state.get_data()
    selected = data.get("selected_interests", [])

    if interest in selected:
        selected.remove(interest)
    else:
        selected.append(interest)
    await state.update_data(selected_interests=selected)

    # # Остаёмся на той же странице
    # current_text = callback.message.reply_markup.inline_keyboard[-1][1].callback_data
    # # page:X или done_interests
    # if current_text.startswith("page:"):
    #     page = int(current_text.split(":")[1])
    # else:
    #     page = 0

    await callback.message.edit_reply_markup(
        reply_markup=build_interests_page(page, selected)
    )

    # await callback.message.edit_reply_markup(reply_markup=build_interests_page(page, selected))
    await callback.answer()

@interest_router.callback_query(StateFilter(ProfileStates.interests), F.data == "done_interests")
async def done_selecting_interests(callback: types.CallbackQuery, state: fsm.context.FSMContext):
    data = await state.get_data()
    selected = data.get("selected_interests", [])
    if not selected:
        await callback.answer("❗ Выберите хотя бы один интерес!", show_alert=True)
        return

    await state.update_data(interests=selected)
    await callback.message.answer(
        f"✅ Интересы сохранены: {', '.join(selected)}\n"
        "Теперь пришлите минимум одно фото, можно добавить до 2 фото и 1 видео.\n"
        "После загрузки нажмите Done для завершения."
    )
    await state.set_state(ProfileStates.media)
    await callback.answer()
