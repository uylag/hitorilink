from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete
from aiogram.utils.media_group import MediaGroupBuilder
from typing import Optional

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import User

async def create_user(
    session: AsyncSession,
    tgid: int,
    username: Optional[str] = None,
    name: Optional[str] = None
) -> User:
    new_user = User(
        tgid=tgid,
        username=username,
        name=name
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

async def get_user_by_tgid(session: AsyncSession, tgid: int) -> User | None:
    orm_query = select(User).where(User.tgid == tgid)
    res = await session.execute(orm_query)
    return res.scalar_one_or_none()

async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    orm_query = select(User).where(User.username == username)
    res = await session.execute(orm_query)
    return res.scalar_one_or_none()

async def delete_user(session: AsyncSession, tgid: int | None = None, username: str | None = None) -> bool:
    """
    Deletes user from database through tgid or username.
    Returns True, if deleted at least one user.
    """
    if not tgid and not username:
        raise ValueError("tgid or username must be selected")

    if username and not tgid:
        query = select(User.tgid).where(User.username == username)
        res = await session.execute(query)
        tgid = res.scalar_one_or_none()

        if not tgid: 
            return False

    stmt = delete(User).where(User.tgid == tgid)
    res = await session.execute(stmt)
    await session.commit()
    return res.rowcount > 0

async def get_field(session: AsyncSession, tgid: int, field: str) -> Optional[object]:
    orm_query = select(getattr(User, field)).where(User.tgid == tgid)
    res = await session.execute(orm_query)
    return res.scalar_one_or_none()

from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class UserInfo:
    tgid: int
    username: str
    name: str
    age: int
    # age_range: int
    # min_max_age: tuple[int, int]
    # gender_actual: bool | None
    # gender_search: int | None
    description: str
    interests: list[str]
    media: list[dict[str, Any]]
    is_active: bool
    rating: int | None
    consent_to_share: bool
    referrals: list[int]
    created_at: datetime | None
    updated_at: datetime | None
    banned: bool

def get_raw_information(user: User) -> UserInfo:
    age = Get.check(user, "age_required") or 40
    # age_range = Get.check(user, "age_range") or 0
    
    return UserInfo(
        tgid=Get.check(user, "tgid"),
        username=Get.check(user, "username"),
        name=Get.check(user, "name") or "Unknown",
        age=age,
        # age_range=age_range,
        # min_max_age=(age - age_range, age + age_range),
        # gender_actual=Get.check(user, "gender_actual"),
        # gender_search=Get.check(user, "gender_search"),
        description=Get.check(user, "description") or "",
        interests=Get.check(user, "interests") or [],
        media=Get.check(user, "media") or [],
        is_active=Get.check(user, "is_active"),
        rating=Get.check(user, "rating"),
        consent_to_share=Get.check(user, "consent_to_share"),
        referrals=Get.check(user, "referrals"),
        created_at=Get.check(user, "created_at"),
        updated_at=Get.check(user, "updated_at"),
        banned=Get.check(user, "banned"),
    )

def beautiful_form_output(user: User | UserInfo) -> list | str:
    name = Get.check(user, "name") or "Unknown"
    age = Get.check(user, "age_required") or 40
    desc = Get.check(user, "description") or ""
    interests = Get.check(user, "interests") or []

    if isinstance(user, User):
        media = Get.check(user, "media") or []

        caption = (
            f"Ваша анкета: \n\n"
            f"{name}\t;\t{age}\n"
            f"{desc}\n\n"
            f"Интересы: {interests}"
        )
    elif isinstance(user, UserInfo):
        caption = (
            f"Ваша анкета: \n\n"
            f"{user.name}\t;\t{user.age}\n"
            f"{user.description}\n\n"
            f"Интересы: {user.interests}"
        )
        media = user.media or []

    if media:
        media_group = MediaGroupBuilder(caption=caption)
        for _file in media:
            if _file["type"] == "photo":
                media_group.add_photo(_file["file_id"])
            elif _file["type"] == "video":
                media_group.add_video(_file["file_id"])
        return media_group.build()
    else:
        return caption

def beautiful_form_output_with_percent(user: User | UserInfo, percent: float) -> list | str:
    name = Get.check(user, "name") or "Unknown"
    age = Get.check(user, "age_required") or 40
    desc = Get.check(user, "description") or ""
    interests = Get.check(user, "interests") or []

    if isinstance(user, User):
        media = Get.check(user, "media") or []

        caption = (
            f"Ваша анкета:\nПроцент сходства: {percent * 100}% \n\n"
            f"{name}\t;\t{age}\n"
            f"{desc}\n\n"
            f"Интересы: {interests}"
        )
    elif isinstance(user, UserInfo):
        caption = (
            f"Ваша анкета:\nПроцент сходства: {percent * 100}%  \n\n"
            f"{user.name}\t;\t{user.age}\n"
            f"{user.description}\n\n"
            f"Интересы: {user.interests}"
        )
        media = user.media or []

    if media:
        media_group = MediaGroupBuilder(caption=caption)
        for _file in media:
            if _file["type"] == "photo":
                media_group.add_photo(_file["file_id"])
            elif _file["type"] == "video":
                media_group.add_video(_file["file_id"])
        return media_group.build()
    else:
        return caption

async def exist_user(session: AsyncSession, tgid: int) -> bool:
    """
    `True` if user exist in current database, `False` otherwise
    """
    return (await get_user_by_tgid(session=session, tgid=tgid)) is not None

class Get:
    @staticmethod
    def check(user: User, param: str) -> Optional[str | int | bool]:
        return getattr(user, param, None)

    @staticmethod
    def is_profile_complete(user: User) -> bool:
        required_fields = ["name", "age_required", "description", "media"]
        return all(getattr(user, f) for f in required_fields)

class Update:
    def __init__(self, session: AsyncSession, user: User) -> None:
        self.user = user
        self.session = session
    
    async def crr(self) -> User:
        """Commit -> Refresh -> Return updated user"""
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Invalid data: {str(e)}")
        await self.session.refresh(self.user)
        return self.user

    async def update(self, **kwargs) -> User:
        for key, value in kwargs.items():
            if hasattr(self.user, key):
                setattr(self.user, key, value)

        return await self.crr()

    async def name(self, name: str | None) -> User:
        return await self.update(name=name)

    async def username(self, username: str | None) -> User:
        return await self.update(username=username)

    async def age(self, age: int) -> User:
        return await self.update(age_required=age)

    # async def age_range(self, age_range: int) -> User:
    #     return await self.update(age_range=age_range)

    # async def age_and_age_range(self, age: int, age_range: int) -> User:
    #     return await self.update(age_required=age, age_range=age_range)

    # async def gender_actual_and_search(self, gender_actual: bool, gender_search: int) -> User:
    #     return await self.update(gender_actual=gender_actual, gender_search=gender_search)

    async def desc(self, desc: str | None):
        return await self.update(description=desc)

    async def interests(self, interests: list[str] | None) -> User:
        return await self.update(interests=interests)

    async def media(self, media: list[str] | None) -> User:
        return await self.update(media=media)

    async def turn_active(self) -> User:
        current_status = Get.check(self.user, param="is_active")
        return await self.update(is_active=not current_status)

    async def rating(self, rating: float) -> User:
        return await self.update(rating=rating)

    async def consent_to_share(self, agreement: bool) -> User:
        return await self.update(consent_to_share=agreement)

    async def add_referral(self, tgid: int) -> User:
        ref_list: list = Get.check(self.user, param="referrals") or []
        ref_list.append(str(tgid))
        return await self.update(referrals=ref_list)

    async def del_referral(self, tgid: int) -> User:
        ref_list: list[str] = Get.check(self.user, param="referrals") or []
        str_id = str(tgid)
        if str_id in ref_list:
            ref_list.remove(str_id)
        return await self.update(referrals=ref_list)
            
    async def deactivate(self) -> User:
        return await self.update(is_active=False)

    async def activate(self) -> User:
        return await self.update(is_active=True)

    async def ban(self) -> User:
        return await self.update(banned=True)

    async def unban(self) -> User:
        return await self.update(banned=False)

    async def full_profile_update(
        self,
        name: str,
        age: int,
        # age_range: int,
        # gender_actual: bool,
        # gender_search: int,
        desc: str,
        interests: list[str],
        media: list[str]
    ) -> User:
        return await self.update(
            name=name,
            age_required=age,
            # age_range=age_range,
            # gender_actual=gender_actual,
            # gender_search=gender_search,
            description=desc,
            interests=interests,
            media=media,
        )