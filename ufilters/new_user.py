from aiogram import filters, types
from sqlalchemy.ext.asyncio import AsyncSession

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import get_db, exist_user

class NewUserFilter(filters.BaseFilter):  
    """
    True if user is NOT in the database
    False otherwise
    """  
    async def __call__(self, message: types.Message):
        tgid = message.from_user.id
        async for session in get_db():
            is_exist = await exist_user(session=session, tgid=tgid)
            return not is_exist
