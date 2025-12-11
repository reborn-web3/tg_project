from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User


class UserRepository:
    """Репозиторий для работы с пользователями"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name_tg: Optional[str] = None,
    ) -> User:
        """Создать нового пользователя"""
        user = User(id=user_id, username=username, first_name_tg=first_name_tg)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Обновить данные пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name_tg: Optional[str] = None,
    ) -> tuple[User, bool]:
        """Получить или создать пользователя. Возвращает (user, created)"""
        user = await self.get_by_id(user_id)
        if user:
            return user, False

        user = await self.create(user_id, username, first_name_tg)
        return user, True
