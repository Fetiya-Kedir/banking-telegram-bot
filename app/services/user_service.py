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