from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select

from app.models import Payment, Rental
from app.services.base import BaseService


class RentalService(BaseService[Rental]):
    model = Rental

    async def create_rental(
        self,
        inventory_id: int,
        customer_id: int,
        staff_id: int,
    ) -> Rental:
        # Check inventory is not currently rented out
        active_rental = (
            await self.db.execute(
                select(Rental).where(
                    Rental.inventory_id == inventory_id,
                    Rental.return_date.is_(None),
                )
            )
        ).scalar_one_or_none()
        if active_rental:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This inventory item is already rented out",
            )

        rental = Rental(
            inventory_id=inventory_id,
            customer_id=customer_id,
            staff_id=staff_id,
            rental_date=datetime.now(UTC).replace(tzinfo=None),
        )
        self.db.add(rental)
        await self.db.flush()
        await self.db.refresh(rental)
        return rental

    async def return_rental(self, rental_id: int, return_date: datetime | None = None) -> Rental:
        rental = await self.get_by_id(rental_id)
        if rental.return_date is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This rental has already been returned",
            )
        rental.return_date = return_date or datetime.now(UTC).replace(tzinfo=None)
        await self.db.flush()
        await self.db.refresh(rental)
        return rental

    async def get_overdue_rentals(self, page: int = 1, size: int = 20):
        # Overdue = not returned and rental_date older than film's rental_duration days
        # Simplified: return_date is None
        q = select(Rental).where(Rental.return_date.is_(None)).order_by(Rental.rental_date.asc())
        count_q = select(func.count()).select_from(Rental).where(Rental.return_date.is_(None))
        total = (await self.db.execute(count_q)).scalar_one()
        offset = (page - 1) * size
        rows = (await self.db.execute(q.offset(offset).limit(size))).scalars().all()
        return list(rows), total


class PaymentService(BaseService[Payment]):
    model = Payment

    async def get_customer_payments(
        self,
        customer_id: int,
        page: int = 1,
        size: int = 20,
        sort_by: str | None = None,
        order: str = "asc",
    ):
        filters = [Payment.customer_id == customer_id]
        if sort_by:
            return await self.list(
                page=page, size=size, filters=filters, sort_by=sort_by, order=order
            )
        return await self.list(
            page=page, size=size, filters=filters, order_by=Payment.payment_date.desc()
        )

    async def get_revenue_summary(self) -> dict:
        result = await self.db.execute(
            select(
                func.count(Payment.payment_id).label("total_payments"),
                func.sum(Payment.amount).label("total_revenue"),
                func.avg(Payment.amount).label("avg_payment"),
            )
        )
        row = result.one()
        return {
            "total_payments": row.total_payments,
            "total_revenue": float(row.total_revenue or 0),
            "avg_payment": float(row.avg_payment or 0),
        }
