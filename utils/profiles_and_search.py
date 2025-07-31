import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import get_db, get_raw_information, UserInfo, User, get_user_by_tgid
from sqlalchemy import select
from ai import MatchAi
from aiogram import types, fsm

async def get_random_form(searcher_id: int) -> UserInfo:
    async for session in get_db():
        # Получаем данные искателя
        searcher = await get_user_by_tgid(session=session, tgid=searcher_id)
        if not searcher:
            return

        searcher_info = get_raw_information(user=searcher)

        # Запрашиваем всех активных пользователей, кроме искателя
        query = select(User).where(
            User.tgid != searcher_id,
            User.is_active
        )

        model = MatchAi()
        users = (await session.execute(query)).scalars().all()

        # Сортируем пользователей по проценту совместимости
        sorted_users = sorted(
            users,
            key=lambda u: model.get_percent(
                desc1=searcher_info.description,
                desc2=get_raw_information(user=u).description,
                interest1=searcher_info.interests,
                interest2=get_raw_information(user=u).interests
            ),
            reverse=True
        )

        # Возвращаем каждого пользователя с процентом совместимости
        for user in sorted_users:
            user_info = get_raw_information(user=user)
            percent = model.get_percent(
                desc1=searcher_info.description,
                desc2=user_info.description,
                interest1=searcher_info.interests,
                interest2=user_info.interests
            )
            yield (user_info, percent)


async def pay(message: types.Message, state: fsm.context.FSMContext) -> bool:
    return True