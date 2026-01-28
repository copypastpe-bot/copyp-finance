import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.budget import Budget
from db.models.budget_membership import BudgetMembership
from db.models.user import User


class ActiveBudgetServiceError(Exception):
    pass


async def list_user_budgets(session: AsyncSession, user_id: uuid.UUID) -> list[dict[str, str]]:
    result = await session.execute(
        select(Budget, BudgetMembership)
        .join(BudgetMembership, BudgetMembership.budget_id == Budget.id)
        .where(
            BudgetMembership.user_id == user_id,
            BudgetMembership.is_active.is_(True),
            Budget.is_archived.is_(False),
        )
        .order_by(Budget.created_at.asc())
    )
    items: list[dict[str, str]] = []
    for budget, membership in result.all():
        items.append(
            {
                "budget_id": str(budget.id),
                "name": budget.name,
                "role": membership.role,
            }
        )
    return items


async def set_active_budget(
    session: AsyncSession, user_id: uuid.UUID, budget_id: uuid.UUID
) -> Budget:
    membership = await session.execute(
        select(BudgetMembership).where(
            BudgetMembership.user_id == user_id,
            BudgetMembership.budget_id == budget_id,
            BudgetMembership.is_active.is_(True),
        )
    )
    if membership.scalar_one_or_none() is None:
        raise ActiveBudgetServiceError("Ты не участник этого бюджета.")

    budget = await session.get(Budget, budget_id)
    if budget is None or budget.is_archived:
        raise ActiveBudgetServiceError("Бюджет не найден или архивирован.")

    user = await session.get(User, user_id)
    if user is None:
        raise ActiveBudgetServiceError("Пользователь не найден.")

    user.active_budget_id = budget.id
    await session.commit()
    return budget


async def get_active_budget_name(session: AsyncSession, user_id: uuid.UUID) -> str | None:
    result = await session.execute(
        select(Budget.name)
        .join(User, User.active_budget_id == Budget.id)
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()
