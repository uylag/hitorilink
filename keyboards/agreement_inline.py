from aiogram import types

agree_kb = [
    [
        types.InlineKeyboardButton(
            text="Согласен",
            callback_data="agree"
        ), 
        types.InlineKeyboardButton(
            text="Не согласен",
            callback_data="disagree"
        )
    ]
]

agree_markup = types.InlineKeyboardMarkup(inline_keyboard=agree_kb)