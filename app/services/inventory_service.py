from __future__ import annotations

from sqlalchemy import func, select

from app.models import Inventory, Rental
from app.services.base import BaseService


class InventoryService(BaseService[Inventory]):
    model = Inventory

    async def get_available_inventory(
        self, film_id: int, store_id: int | None = None, page: int = 1, size: int = 20
    ):
        """Return inventory items not currently rented out."""
        rented_subq = (
            select(Rental.inventory_id)
            .where(Rental.return_date.is_(None))
            .scalar_subquery()
        )
        q = select(Inventory).where(
            Inventory.film_id == film_id,
            Inventory.inventory_id.not_in(rented_subq),
        )
        count_q = (
            select(func.count())
            .select_from(Inventory)
            .where(
                Inventory.film_id == film_id,
                Inventory.inventory_id.not_in(rented_subq),
            )
        )
        if store_id:
            q = q.where(Inventory.store_id == store_id)
            count_q = count_q.where(Inventory.store_id == store_id)

        total = (await self.db.execute(count_q)).scalar_one()
        offset = (page - 1) * size
        rows = (await self.db.execute(q.offset(offset).limit(size))).scalars().all()
        return list(rows), total

    async def get_store_inventory(
        self,
        store_id: int,
        page: int = 1,
        size: int = 20,
        sort_by: str | None = None,
        order: str = "asc",
    ):
        return await self.list(
            page=page,
            size=size,
            filters=[Inventory.store_id == store_id],
            sort_by=sort_by,
            order=order,
        )
