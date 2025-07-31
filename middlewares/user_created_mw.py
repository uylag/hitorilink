from aiogram import BaseMiddleware, types
import typing

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import get_db, Get, get_user_by_tgid
import logging


class UserCreatedMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: typing.Callable[[types.TelegramObject, typing.Dict[str, typing.Any]], typing.Awaitable[typing.Any]],
        event: types.Message,
        data: typing.Dict[str, typing.Any]
    ) -> typing.Any:
        tgid = event.from_user.id

        async for session in get_db():
            user = await get_user_by_tgid(session=session, tgid=tgid)
            if not user:
                logging.info(f"User {tgid} not found → blocked middleware")
                await event.answer("Создайте анкету (/create)")
                return
            created = Get.is_profile_complete(user=user)
            logging.info(f"User {tgid} profile_complete={created}")
            if not created:
                await event.answer("Создайте анкету (/create)")
                return

        return await handler(event, data)
