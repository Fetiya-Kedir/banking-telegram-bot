from __future__ import annotations

from telegram import User as TelegramUser
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.repositories.user_repo import UserRepository


async def upsert_telegram_user(
    session: AsyncSession,
    telegram_user: TelegramUser,
    default_language: str,
) -> User:
    repo = UserRepository(session)

    existing_user = await repo.get_by_telegram_user_id(telegram_user.id)

    if existing_user is None:
        return await repo.create(
            telegram_user_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            language_code_selected=default_language,
        )

    return await repo.update_basic_info(
        user=existing_user,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
    )


async def set_user_language(
    session: AsyncSession,
    telegram_user_id: int,
    language_code_selected: str,
) -> User | None:
    repo = UserRepository(session)
    user = await repo.get_by_telegram_user_id(telegram_user_id)

    if user is None:
        return None

    return await repo.update_language(
        user=user,
        language_code_selected=language_code_selected,
    )


async def get_user_language(
    session: AsyncSession,
    telegram_user_id: int,
    default_language: str,
) -> str:
    repo = UserRepository(session)
    user = await repo.get_by_telegram_user_id(telegram_user_id)

    if user is None:
        return default_language

    return user.language_code_selected