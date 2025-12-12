import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from .models import Base

# SQLite по умолчанию в /tmp — в Functions корень read-only.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:////tmp/bot.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    # Таймаут для ожидания разблокировки БД (критично для 120+ пользователей)
    connect_args={"check_same_thread": False, "timeout": 20},
)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """Создание всех таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Получение сессии БД"""
    async with async_session_maker() as session:
        yield session
