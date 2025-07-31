from aiogram import filters, types

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import get_db, Get, get_user_by_tgid
import logging

class UserCreated(filters.BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        tgid = message.from_user.id
        async for session in get_db():
            user = await get_user_by_tgid(session=session, tgid=tgid)
            if not user:
                logging.info(f"User {tgid} not found in database")
                return False
            created = Get.is_profile_complete(user=user)
            logging.info(f"User {tgid} profile complete: {created}")
            return bool(created)
