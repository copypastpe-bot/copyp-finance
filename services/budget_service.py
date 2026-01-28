import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.budget import Budget
from db.models.budget_counter import BudgetCounter
from db.models.budget_membership import BudgetMembership
from db.models.user import User
from services.dto.budget import CreateBudgetDTO


class BudgetServiceError(Exception):
    pass


async def create_first_budget(
    session: AsyncSession,
    owner_user_id: uuid.UUID,
    payload: CreateBudgetDTO,
) -> Budget:
    currencies = [
        payload.base_currency,
        payload.aux_currency_1,
        payload.aux_currency_2,
    ]
    normalized = [currency for currency in currencies if currency is not None]
    if len(normalized) != len(set(normalized)):
        raise BudgetServiceError("Валюты должны быть разными внутри бюджета.")

    async with session.begin():
        owner = await session.get(User, owner_user_id)
        existing = await session.execute(
            select(BudgetMembership).where(
                BudgetMembership.user_id == owner_user_id,
                BudgetMembership.is_active.is_(True),
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise BudgetServiceError("У тебя уже есть активный бюджет.")

        budget = Budget(
            name=payload.name.strip(),
            base_currency=payload.base_currency,
            aux_currency_1=payload.aux_currency_1,
            aux_currency_2=payload.aux_currency_2,
            timezone=payload.timezone.strip(),
            created_by_user_id=owner_user_id,
        )
        session.add(budget)
        await session.flush()

        membership = BudgetMembership(
            budget_id=budget.id,
            user_id=owner_user_id,
            role="owner",
            is_active=True,
        )
        session.add(membership)

        counter = BudgetCounter(
            budget_id=budget.id,
            next_seq_no=1,
        )
        session.add(counter)

        if owner is not None and owner.active_budget_id is None:
            owner.active_budget_id = budget.id

    return budget
