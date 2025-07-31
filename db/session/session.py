from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data import cfg
from db import DBBase

'''
Core connection manager for SQLAlchemy
Doesn't execute directly queries, but manages the connection pool
All `sessionmaker` instances get their connections from this engine 
'''
engine = create_async_engine(
    url=cfg.PG_LINK,              # database connection url; postgresql+asyncpg tells SQLAlchemy to use the asyncpg driver.
    echo=cfg.LOGGING_LEVEL == 10, # True - prints every SQL statement being executed
    pool_size=10,                 # The number of persistent connections kept open in the pool. If all are in use, SQLAlchemy will allocate from max_overflow.
    max_overflow=20               # The additional number of connections allowed beyond pool_size. So here, the maximum connections would be 10 + 20 = 30 at peak load.
)

AsyncSessionLocal = sessionmaker(
    bind=engine,           # every session created will pull a connection from that engine’s pool
    class_=AsyncSession,   # tells SQLAlchemy to create asynchronous sessions.
    expire_on_commit=False # disable it, meaning the ORM objects remain usable after commit without a re-fetch.
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(DBBase.metadata.create_all)


async def close_engine():
    await engine.dispose()

async def reset_db():
    """
    ⚠ Полностью удаляет все таблицы и создаёт заново.
    Использовать только в dev/test окружении!
    """
    async with engine.begin() as conn:
        print("⚠ Dropping all tables...")
        await conn.run_sync(DBBase.metadata.drop_all)
        print("✅ Creating all tables...")
        await conn.run_sync(DBBase.metadata.create_all)
    print("✅ Database reset completed!")
