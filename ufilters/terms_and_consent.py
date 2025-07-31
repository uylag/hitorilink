from aiogram import filters, types

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import get_db, get_field

class TaCFilter(filters.BaseFilter):
    """
    True if accepted terms & consent (consent_to_share=True)
    False otherwise
    """
    async def __call__(self, message: types.Message):
        tgid = message.from_user.id
        async for session in get_db():
            accepted = await get_field(session=session, tgid=tgid, field="consent_to_share")
            return bool(accepted)