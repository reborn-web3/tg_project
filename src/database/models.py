from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""

    pass


class User(Base):
    """Модель пользователя"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, comment="Telegram user ID"
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, index=True, comment="Telegram username"
    )
    first_name_tg: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="Имя из Telegram"
    )
    first_name: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="Имя пользователя"
    )
    last_name: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="Фамилия пользователя"
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="Город пользователя"
    )
    interests: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Интересы пользователя"
    )
    events: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="События пользователя"
    )
    about: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="О себе")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="Дата создания записи"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Дата обновления записи",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username})"


class TextTemplate(Base):
    """Модель для хранения текстовых шаблонов бота"""

    __tablename__ = "text_templates"

    key: Mapped[str] = mapped_column(
        String(100), primary_key=True, comment="Уникальный ключ шаблона"
    )
    title: Mapped[str] = mapped_column(
        String(200), comment="Название шаблона для админки"
    )
    content: Mapped[str] = mapped_column(
        Text, comment="Содержимое шаблона (HTML поддерживается)"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Описание шаблона"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, comment="Дата создания"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Дата обновления",
    )

    def __repr__(self) -> str:
        return f"TextTemplate(key={self.key}, title={self.title})"