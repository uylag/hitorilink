from aiogram import filters, types

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import get_db, Get, get_user_by_tgid

class IsMeBanned(filters.BaseFilter):
    '''
    Return True if banned
    False otherwise
    '''
    async def __call__(self, message: types.Message):
        tgid: int = message.from_user.id

        async for session in get_db():
            user = await get_user_by_tgid(session=session, tgid=tgid)

            if not user:
                return False

            banned_status = Get.check(user=user, param="banned")

            return bool(banned_status)