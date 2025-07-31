from aiogram import BaseMiddleware, types
import typing
import logging
from time import time

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import get_db, get_user_by_tgid
from data import cfg

TERMS_PATH = cfg.TERMS_PATH
last_warned = {}

class TACMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: typing.Callable[
            [types.TelegramObject, typing.Dict[str, typing.Any]],
            typing.Awaitable[typing.Any]
        ],
        event: types.Message,
        data: typing.Dict[str, typing.Any]
    ) -> typing.Any:

        tgid = event.from_user.id

        # Разрешаем явно /accept и /start
        if event.text and (event.text.startswith("/accept") or event.text.startswith("/start")):
            return await handler(event, data)

        # Проверяем статус consent_to_share
        async for session in get_db():
            user = await get_user_by_tgid(session=session, tgid=tgid)

            # Если юзер не создан → пропускаем (NewUserFilter обработает)
            if not user:
                return await handler(event, data)

            # Если НЕ согласился, блокируем остальные хэндлеры
            if not user.consent_to_share:
                logging.info(f"User {tgid} tried to use bot without accepting terms")

                # Не спамить Terms слишком часто
                now = time()
                if tgid not in last_warned or now - last_warned[tgid] > 60:
                    last_warned[tgid] = now
                    caption = (
                        "❗ Для продолжения использования HitoriLink нужно принять Условия пользования."
                    )
                    await event.answer_document(
                        document=types.FSInputFile(TERMS_PATH),
                        caption=caption + "\n\nПосле прочтения нажмите кнопку согласия ниже.",
                        reply_markup=types.InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    types.InlineKeyboardButton(text="✅ Согласен", callback_data="agree"),
                                    types.InlineKeyboardButton(text="❌ Не согласен", callback_data="disagree")
                                ]
                            ]
                        )
                    )
                return  # блокируем дальнейшие хэндлеры

        # Если всё норм → пускаем дальше
        return await handler(event, data)
