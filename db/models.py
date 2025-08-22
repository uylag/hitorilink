from sqlalchemy import Integer, String, Boolean, DateTime, Float, BigInteger, SmallInteger, Numeric
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import DBBase

class User(DBBase):
    __tablename__="users"
    __table_args__ = (
        # CheckConstraint("age_range >= 0 AND age_range <= 50 AND age_required - age_range >= 18", name="check_age_range_valid"),
        CheckConstraint("age_required >= 18 AND age_required <= 120", name="check_age_valid"),
        # CheckConstraint("gender_search IN (1, 2, 3)", name="check_gender_search"),
        CheckConstraint("rating >= 0 AND rating <= 10", name="check_rating_range"),
        CheckConstraint("char_length(name) >= 1", name="name_is_valid"),
    )

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
    )
    tgid: Mapped[int] = mapped_column(
        BigInteger, 
        unique=True, 
        index=True
    )
    username: Mapped[str] = mapped_column(
        String(33), 
        nullable=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    age_required: Mapped[int] = mapped_column(Integer, nullable=True)
    # age_range: Mapped[int] = mapped_column(Integer, nullable=True)
    # gender_actual: Mapped[bool] = mapped_column(Boolean, default=True) # True = Male; False = Female
    # gender_search: Mapped[int] = mapped_column(SmallInteger, nullable=True) # 1 = Male, 2 = Female, 3 = No matter
    description: Mapped[str] = mapped_column(String(600), nullable=True)
    interests: Mapped[list[str]] = mapped_column(JSONB, nullable=True)
    media: Mapped[list[str]] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=1.0)
    consent_to_share: Mapped[bool] = mapped_column(Boolean, default=False)
    referrals: Mapped[list[str]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    banned: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return (
               f"<Created (updated) profile:\n"
               f"Name: {self.name}\tAge: {self.age_required}\n"
            #    f"Age range: {age_range_text}\n"
            #    f"Gender: {gender_text}\tSearch: {search_text}\n"
               f"Bio: {self.description}\n\n"
               f"Interests: {list(self.interests) if self.interests else []}\n"
               f"Rating: {self.rating} points\n"
               f"Created: {self.created_at}\n"
               f"Updated: {self.updated_at}\n>"
        )