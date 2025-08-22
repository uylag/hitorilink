from aiogram import BaseMiddleware, types
import typing
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ufilters import UserCreated
import logging

class UserCreatedMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: typing.Callable[[types.TelegramObject, typing.Dict[str, typing.Any]], typing.Awaitable[typing.Any]],
        event: types.Message,
        data: typing.Dict[str, typing.Any]
    ) -> typing.Any:
        user_created_filter = UserCreated()
        
        is_profile_complete = await user_created_filter.__call__(event)
        
        if not is_profile_complete:
            logging.info(f"User {event.from_user.id} blocked by UserCreatedMiddleware (profile incomplete/not found)")
            await event.answer("Создайте профиль (/create)")
            return 
        
        return await handler(event, data)
