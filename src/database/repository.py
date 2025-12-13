from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, TextTemplate


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

    async def reset_profile(self, user_id: int) -> Optional[User]:
        """Сбросить профиль пользователя (очистить все поля профиля, кроме базовых)"""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        # Очищаем все поля профиля, сохраняя базовые данные
        user.first_name = None
        user.last_name = None
        user.city = None
        user.interests = None
        user.events = None
        user.about = None

        await self.session.commit()
        await self.session.refresh(user)
        return user


class TextTemplateRepository:
    """Репозиторий для работы с текстовыми шаблонами"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_key(self, key: str) -> Optional[TextTemplate]:
        """Получить шаблон по ключу"""
        result = await self.session.execute(
            select(TextTemplate).where(TextTemplate.key == key)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[TextTemplate]:
        """Получить все шаблоны"""
        result = await self.session.execute(select(TextTemplate))
        return list(result.scalars().all())

    async def create_or_update(
        self, key: str, title: str, content: str, description: Optional[str] = None
    ) -> TextTemplate:
        """Создать или обновить шаблон"""
        template = await self.get_by_key(key)
        if template:
            template.title = title
            template.content = content
            if description is not None:
                template.description = description
        else:
            template = TextTemplate(
                key=key, title=title, content=content, description=description
            )
            self.session.add(template)

        await self.session.commit()
        await self.session.refresh(template)
        return template

    async def delete(self, key: str) -> bool:
        """Удалить шаблон"""
        template = await self.get_by_key(key)
        if not template:
            return False

        await self.session.delete(template)
        await self.session.commit()
        return True