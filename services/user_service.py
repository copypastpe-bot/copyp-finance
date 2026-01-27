from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import User


async def ensure_user(
    session: AsyncSession,
    telegram_user_id: int,
    telegram_username: str | None,
    first_name: str | None,
    last_name: str | None,
) -> User:
    result = await session.execute(
        select(User).where(User.telegram_user_id == telegram_user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
            first_name=first_name,
            last_name=last_name,
        )
        session.add(user)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            result = await session.execute(
                select(User).where(User.telegram_user_id == telegram_user_id)
            )
            return result.scalar_one()
        return user

    changed = False
    if user.telegram_username != telegram_username:
        user.telegram_username = telegram_username
        changed = True
    if user.first_name != first_name:
        user.first_name = first_name
        changed = True
    if user.last_name != last_name:
        user.last_name = last_name
        changed = True

    if changed:
        await session.commit()

    return user
