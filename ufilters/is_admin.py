from aiogram import filters, types

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data import cfg

class IsAdminFilter(filters.BaseFilter):
    async def __call__(self, obj: types.TelegramObject) -> bool:
        user_id = getattr(obj.from_user, "id", None)
        return user_id in cfg.ADMINS if user_id else False
