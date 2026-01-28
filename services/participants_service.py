import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.budget_membership import BudgetMembership
from db.models.user import User


class ParticipantsServiceError(Exception):
    pass


async def list_active_participants(
    session: AsyncSession, owner_user_id: uuid.UUID
) -> list[dict[str, str]]:
    budget_id = await _get_owner_budget_id(session, owner_user_id)
    result = await session.execute(
        select(BudgetMembership, User)
        .join(User, User.id == BudgetMembership.user_id)
        .where(
            BudgetMembership.budget_id == budget_id,
            BudgetMembership.is_active.is_(True),
        )
        .order_by(BudgetMembership.role.desc(), User.created_at.asc())
    )
    items: list[dict[str, str]] = []
    for membership, user in result.all():
        username = f"@{user.telegram_username}" if user.telegram_username else "без username"
        name = " ".join([part for part in [user.first_name, user.last_name] if part]) or "Без имени"
        role = "владелец" if membership.role == "owner" else "участник"
        items.append(
            {
                "user_id": str(user.id),
                "username": username,
                "name": name,
                "role": role,
            }
        )
    return items


async def list_active_participants_for_budget(
    session: AsyncSession, owner_user_id: uuid.UUID, budget_id: uuid.UUID | str
) -> list[dict[str, str]]:
    if isinstance(budget_id, str):
        budget_id = uuid.UUID(budget_id)
    await _ensure_owner_for_budget(session, owner_user_id, budget_id)
    result = await session.execute(
        select(BudgetMembership, User)
        .join(User, User.id == BudgetMembership.user_id)
        .where(
            BudgetMembership.budget_id == budget_id,
            BudgetMembership.is_active.is_(True),
        )
        .order_by(BudgetMembership.role.desc(), User.created_at.asc())
    )
    items: list[dict[str, str]] = []
    for membership, user in result.all():
        username = f"@{user.telegram_username}" if user.telegram_username else "без username"
        name = " ".join([part for part in [user.first_name, user.last_name] if part]) or "Без имени"
        role = "владелец" if membership.role == "owner" else "участник"
        items.append(
            {
                "user_id": str(user.id),
                "username": username,
                "name": name,
                "role": role,
            }
        )
    return items


async def remove_participant(
    session: AsyncSession, owner_user_id: uuid.UUID, participant_user_id: uuid.UUID
) -> None:
    budget_id = await _get_owner_budget_id(session, owner_user_id)
    membership_result = await session.execute(
        select(BudgetMembership).where(
            BudgetMembership.budget_id == budget_id,
            BudgetMembership.user_id == participant_user_id,
            BudgetMembership.is_active.is_(True),
        )
    )
    membership = membership_result.scalar_one_or_none()
    if membership is None:
        raise ParticipantsServiceError("Участник не найден.")
    if membership.role == "owner":
        raise ParticipantsServiceError("Нельзя удалить владельца бюджета.")

    membership.is_active = False

    user = await session.get(User, participant_user_id)
    if user is not None and user.active_budget_id == budget_id:
        user.active_budget_id = None
    await session.commit()


async def remove_participant_from_budget(
    session: AsyncSession,
    owner_user_id: uuid.UUID,
    budget_id: uuid.UUID,
    participant_user_id: uuid.UUID,
) -> None:
    await _ensure_owner_for_budget(session, owner_user_id, budget_id)
    membership_result = await session.execute(
        select(BudgetMembership).where(
            BudgetMembership.budget_id == budget_id,
            BudgetMembership.user_id == participant_user_id,
            BudgetMembership.is_active.is_(True),
        )
    )
    membership = membership_result.scalar_one_or_none()
    if membership is None:
        raise ParticipantsServiceError("Участник не найден.")
    if membership.role == "owner":
        raise ParticipantsServiceError("Нельзя удалить владельца бюджета.")

    membership.is_active = False
    user = await session.get(User, participant_user_id)
    if user is not None and user.active_budget_id == budget_id:
        user.active_budget_id = None
    await session.commit()


async def get_participant_display(
    session: AsyncSession, owner_user_id: uuid.UUID, participant_user_id: uuid.UUID
) -> str:
    budget_id = await _get_owner_budget_id(session, owner_user_id)
    result = await session.execute(
        select(BudgetMembership, User)
        .join(User, User.id == BudgetMembership.user_id)
        .where(
            BudgetMembership.budget_id == budget_id,
            BudgetMembership.user_id == participant_user_id,
            BudgetMembership.is_active.is_(True),
        )
    )
    row = result.first()
    if row is None:
        raise ParticipantsServiceError("Участник не найден.")
    membership, user = row
    username = f"@{user.telegram_username}" if user.telegram_username else "без username"
    name = " ".join([part for part in [user.first_name, user.last_name] if part]) or "Без имени"
    role = "владелец" if membership.role == "owner" else "участник"
    return f"{username} — {name} ({role})"


async def _get_owner_budget_id(session: AsyncSession, owner_user_id: uuid.UUID) -> uuid.UUID:
    membership = await session.execute(
        select(BudgetMembership).where(
            BudgetMembership.user_id == owner_user_id,
            BudgetMembership.role == "owner",
            BudgetMembership.is_active.is_(True),
        )
    )
    owner_membership = membership.scalar_one_or_none()
    if owner_membership is None:
        raise ParticipantsServiceError("Только владелец может управлять участниками.")
    return owner_membership.budget_id


async def _ensure_owner_for_budget(
    session: AsyncSession, owner_user_id: uuid.UUID, budget_id: uuid.UUID
) -> None:
    membership = await session.execute(
        select(BudgetMembership).where(
            BudgetMembership.user_id == owner_user_id,
            BudgetMembership.budget_id == budget_id,
            BudgetMembership.role == "owner",
            BudgetMembership.is_active.is_(True),
        )
    )
    owner_membership = membership.scalar_one_or_none()
    if owner_membership is None:
        raise ParticipantsServiceError("Только владелец может управлять участниками.")
