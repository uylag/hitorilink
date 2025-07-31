# import os
# import asyncio
# import logging
# from data import cfg
# from aiogram import Bot, Dispatcher, F
# # from aiogram.filters import CommandStart, Command
# # from aiogram.types import Message
# from handlers import create_router, admin_router, interest_router
# from middlewares import BannedOutMiddleware

# bot = Bot(token=cfg.BOT_API_KEY)
# dp = Dispatcher()

# async def main():
#     dp.message.outer_middleware(BannedOutMiddleware())

#     dp.include_routers(
#         create_router,
#         admin_router,
#         interest_router
#     )
#     await bot.delete_webhook(drop_pending_updates=cfg.DROP_PENDING_UPDATES)
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     try:
#         logging.basicConfig(level=cfg.LOGGING_LEVEL)
#         asyncio.run(main=main())
#     except KeyboardInterrupt:
#         print("Exit")

import os
import asyncio
import logging
from data import cfg
from aiogram import Bot, Dispatcher, types
from handlers import (
    create_router, admin_router, 
    interest_router, search_router,
    edit_router
)
from middlewares import BannedOutMiddleware, TACMiddleware
from db import get_db, exist_user

LOG_FILE = "/home/kiyoshima/All_Work_Folders/Projects/PythonProjects/Bots/HitoriLink/log.log"
logging.basicConfig(
    level=cfg.LOGGING_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

bot = Bot(token=cfg.BOT_API_KEY)
dp = Dispatcher()

async def setup_bot_commands():
    await bot.set_my_commands([
        types.BotCommand(command="profile", description="👤Профиль"),
        types.BotCommand(command="search", description="🔍 Поиск анкет"),
        types.BotCommand(command="edit", description="✏️ Редактировать анкету"),
        types.BotCommand(command="accept", description="📝Вывести условия пользования"),
    ])

async def main():
    await setup_bot_commands()

    dp.message.outer_middleware(BannedOutMiddleware())    
    dp.message.outer_middleware(TACMiddleware())
        
    dp.include_routers(
        create_router,
        admin_router,
        interest_router,
        search_router,
        edit_router
    )
    await bot.delete_webhook(drop_pending_updates=cfg.DROP_PENDING_UPDATES)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main=main())
    except KeyboardInterrupt:
        logging.info("Exit")
