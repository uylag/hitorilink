from aiogram import BaseMiddleware, types
import typing

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ufilters import IsMeBanned

class BannedOutMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: typing.Callable[[types.TelegramObject, typing.Dict[str, typing.Any]], typing.Awaitable[typing.Any]],
        event: types.Message,
        data: typing.Dict[str, typing.Any]
    ) -> typing.Any:
        is_banned = await IsMeBanned().__call__(event)

        if is_banned:
            await event.answer("You are banned.")
            return
        
        return await handler(event, data)