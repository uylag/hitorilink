from aiogram import BaseMiddleware, types, filters
import typing

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ufilters import IsAdminFilter

class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: typing.Callable[[types.TelegramObject, typing.Dict[str, typing.Any]], typing.Awaitable[typing.Any]],
        event: types.Message,
        data: typing.Dict[str, typing.Any]
    ) -> typing.Any:
        is_admin = await IsAdminFilter().__call__(event)

        if is_admin:
            return await handler(event, data)
        else:
            return
