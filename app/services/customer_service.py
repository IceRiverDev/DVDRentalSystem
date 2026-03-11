from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Customer
from app.services.base import BaseService


class CustomerService(BaseService[Customer]):
    model = Customer

    async def get_detail(self, customer_id: int) -> Customer:
        q = (
            select(Customer)
            .where(Customer.customer_id == customer_id)
            .options(selectinload(Customer.address_rel))
        )
        result = await self.db.execute(q)
        customer = result.scalar_one_or_none()
        if customer is None:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return customer

    async def search(
        self,
        name: str | None = None,
        email: str | None = None,
        active: bool | None = None,
        page: int = 1,
        size: int = 20,
        sort_by: str | None = None,
        order: str = "asc",
    ):
        from sqlalchemy import or_
        filters = []
        if name:
            pattern = f"%{name}%"
            filters.append(
                or_(
                    Customer.first_name.ilike(pattern),
                    Customer.last_name.ilike(pattern),
                )
            )
        if email:
            filters.append(Customer.email.ilike(f"%{email}%"))
        if active is not None:
            filters.append(Customer.activebool == active)

        return await self.list(page=page, size=size, filters=filters or None, sort_by=sort_by, order=order)

    async def get_rental_history(self, customer_id: int, page: int = 1, size: int = 20):
        from app.models import Rental
        from sqlalchemy import func
        count_q = select(func.count()).select_from(Rental).where(Rental.customer_id == customer_id)
        total = (await self.db.execute(count_q)).scalar_one()
        offset = (page - 1) * size
        rows = (
            await self.db.execute(
                select(Rental)
                .where(Rental.customer_id == customer_id)
                .order_by(Rental.rental_date.desc())
                .offset(offset)
                .limit(size)
            )
        ).scalars().all()
        return list(rows), total
