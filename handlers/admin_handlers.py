from aiogram import types, F, Router, filters

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data import cfg
from db import delete_user, get_db, get_user_by_username, get_user_by_tgid, Update, beautiful_form_output
from ufilters import IsAdminFilter
from middlewares import AdminMiddleware

admin_router = Router()
admin_router.message.outer_middleware(AdminMiddleware())

@admin_router.message(filters.Command("delete_me")) 
async def delme_cmd(message: types.Message):
    tgid: int = message.from_user.id

    async for session in get_db():
        await delete_user(session=session, tgid=tgid)
        await message.answer(f"Admin: {tgid} deleted successfully.")

@admin_router.message(filters.Command("delete_user"))
async def delusr_cmd(message: types.Message, command: filters.command.CommandObject):
    if not command.args:
        await message.answer("Admin: invalid user id.")
        return

    arg = command.args.strip()

    async for session in get_db():
        if arg.isdigit():
            deleted = await delete_user(session=session, tgid=int(arg))
        else:
            username = arg.lstrip("@")
            deleted = await delete_user(session=session, username=username)

        if deleted:
            await message.answer(f"Admin: {arg} deleted successfully.")
        else:
            await message.answer(f"Admin: {arg} not found in DB.")
    

@admin_router.message(filters.Command("delete_users"))
async def delusrs_cmd(message: types.Message, command: filters.command.CommandObject):
    if not command.args:
        await message.answer("Admin: provide multiple user IDs separated by space")
        return

    tgids: list[int] = [int(x) for x in command.args.split() if x.isdigit()]

    if not tgids:
        await message.answer("Admin: no valid IDs found.")
        return

    deleted_count = 0
    async for session in get_db():
        for tgid in tgids:
            deleted = await delete_user(session=session, tgid=tgid)
            if deleted:
                deleted_count += 1
            else:
                await message.bot.send_message(cfg.OWNER, text=f"Admin: {tgid} can't be deleted for unknown reason.")
    
    await message.answer(f"Admin: {deleted_count}/{len(tgids)} users deleted successfully.")

@admin_router.message(filters.Command("ban"))
async def ban_cmd(message: types.Message, command: filters.command.CommandObject):
    if not command.args:
        await message.answer("Admin: step1: invalid user id or username.")
        return

    arg = command.args.strip()
    checked = False

    try:
        if arg.isdigit() and int(arg) == cfg.OWNER:
            await message.answer("Ты ахуел?")
            checked = True
    except ValueError:
        pass

    if arg.lstrip("@").casefold() == cfg.OWNER_UN.casefold():
        await message.answer("Ты ахуел?")
        checked = True

    async for session in get_db():
        user = None

        if arg.startswith('@'):
            username = arg.lstrip('@')
            user = await get_user_by_username(session=session, username=username)
        elif arg.isdigit():
            user = await get_user_by_tgid(session=session, tgid=int(arg))
        else:
            user = await get_user_by_tgid(session=session, tgid=arg)
            if not user:
                user = await get_user_by_username(session=session, username=arg)

        if not user:
            await message.answer("Admin: step2: invalid user id or username.")
            return

        if checked:
            user = await get_user_by_tgid(session=session, tgid=message.from_user.id)
            upd = Update(session=session, user=user)
        else:
            upd = Update(session=session, user=user)
        user = await upd.ban()
        
        await message.answer(f"Admin: {user} has been banned.")

@admin_router.message(filters.Command("unban"))
async def unban_cmd(message: types.Message, command: filters.command.CommandObject):
    if not command.args:
        await message.answer("Admin: invalid user id or username.")
        return

    arg = command.args.strip()

    async for session in get_db():
        user = None
        
        if arg.startswith("@"):
            username = arg.lstrip("@")
            user = await get_user_by_username(session=session, username=username)
        elif arg.isdigit():
            user = await get_user_by_tgid(session=session, tgid=int(arg))
        else:
            user = await get_user_by_tgid(session=session, tgid=arg)
            if not user:
                user = await get_user_by_username(session=session, username=arg)

        if not user:
            await message.answer("Admin: invalid user id or username.")
            return

        upd = Update(session=session, user=user)
        await upd.update(banned=False)  # Снимаем бан

        await message.answer(f"Admin: user {user.tgid} has been unbanned")

@admin_router.message(filters.Command("view_form"))
async def view_form_cmd(message: types.Message, command: filters.command.CommandObject):
    if not command.args:
        await message.answer("Admin: invalid user id or username.")
        return

    arg = command.args.strip()

    async for session in get_db():
        user = None
        
        if arg.startswith("@"):
            username = arg.lstrip("@")
            user = await get_user_by_username(session=session, username=username)
        elif arg.isdigit():
            user = await get_user_by_tgid(session=session, tgid=int(arg))
        else:
            user = await get_user_by_tgid(session=session, tgid=arg)
            if not user:
                user = await get_user_by_username(session=session, username=arg)

        if not user:
            await message.answer("Admin: invalid user id or username.")
            return

        result = beautiful_form_output(user=user)

        if isinstance(result, str):
            await message.answer(result)

        elif isinstance(result, list):
            await message.answer_media_group(result)

        else:
            await message.answer("Не удалось собрать анкету (пустая?).")