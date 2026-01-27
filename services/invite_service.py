import secrets
from datetime import datetime, timedelta, timezone
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.budget import Budget
from db.models.budget_invite import BudgetInvite
from db.models.budget_membership import BudgetMembership


class InviteServiceError(Exception):
    pass


INVITE_TTL_HOURS = 24
INVITE_MAX_USES = 1


async def create_invite_for_owner(session: AsyncSession, owner_user_id: uuid.UUID) -> BudgetInvite:
    membership = await session.execute(
        select(BudgetMembership).where(
            BudgetMembership.user_id == owner_user_id,
            BudgetMembership.role == "owner",
            BudgetMembership.is_active.is_(True),
        )
    )
    owner_membership = membership.scalar_one_or_none()
    if owner_membership is None:
        raise InviteServiceError("Приглашение может создать только владелец бюджета.")

    budget = await session.get(Budget, owner_membership.budget_id)
    if budget is None or budget.is_archived:
        raise InviteServiceError("Бюджет не найден или архивирован.")

    token = _generate_token()
    now = datetime.now(timezone.utc)
    invite = BudgetInvite(
        budget_id=budget.id,
        token=token,
        created_by_user_id=owner_user_id,
        expires_at=now + timedelta(hours=INVITE_TTL_HOURS),
        max_uses=INVITE_MAX_USES,
        used_count=0,
        is_active=True,
    )
    session.add(invite)
    await session.commit()
    return invite


async def accept_invite(session: AsyncSession, token: str, user_id: uuid.UUID) -> BudgetMembership:
    invite_result = await session.execute(
        select(BudgetInvite).where(BudgetInvite.token == token)
    )
    invite = invite_result.scalar_one_or_none()
    if invite is None or not invite.is_active:
        raise InviteServiceError("Инвайт не найден.")

    now = datetime.now(timezone.utc)
    if invite.expires_at <= now:
        raise InviteServiceError("Срок действия ссылки истёк.")
    if invite.used_count >= invite.max_uses:
        raise InviteServiceError("Ссылка уже использована.")

    existing = await session.execute(
        select(BudgetMembership).where(
            BudgetMembership.user_id == user_id,
            BudgetMembership.budget_id == invite.budget_id,
            BudgetMembership.is_active.is_(True),
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise InviteServiceError("Ты уже участник этого бюджета.")

    membership = BudgetMembership(
        budget_id=invite.budget_id,
        user_id=user_id,
        role="participant",
        is_active=True,
    )
    session.add(membership)

    invite.used_count += 1
    invite.last_used_at = now
    if invite.used_count >= invite.max_uses:
        invite.is_active = False

    await session.commit()

    return membership


def _generate_token() -> str:
    return secrets.token_urlsafe(16)
