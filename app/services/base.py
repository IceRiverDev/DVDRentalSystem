from __future__ import annotations

from typing import Any, Generic, TypeVar
from math import ceil

from fastapi import HTTPException, status
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseService(Generic[ModelT]):
    """Generic async CRUD service for any SQLAlchemy model."""

    model: type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, pk: int) -> ModelT:
        obj = await self.db.get(self.model, pk)
        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__tablename__} not found",
            )
        return obj

    async def list(
        self,
        page: int = 1,
        size: int = 20,
        *,
        order_by: Any = None,
        sort_by: str | None = None,
        order: str = "asc",
        filters: list[Any] | None = None,
        options: list[Any] | None = None,
    ) -> tuple[list[ModelT], int]:
        count_q = select(func.count()).select_from(self.model)
        data_q = select(self.model)

        if filters:
            for f in filters:
                count_q = count_q.where(f)
                data_q = data_q.where(f)

        if options:
            for opt in options:
                data_q = data_q.options(opt)

        if sort_by:
            col = getattr(self.model, sort_by, None)
            if col is not None:
                data_q = data_q.order_by(col.asc() if order == "asc" else col.desc())
        elif order_by is not None:
            data_q = data_q.order_by(order_by)

        total = (await self.db.execute(count_q)).scalar_one()
        offset = (page - 1) * size
        rows = (await self.db.execute(data_q.offset(offset).limit(size))).scalars().all()
        return list(rows), total

    async def create(self, data: dict[str, Any]) -> ModelT:
        obj = self.model(**data)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, pk: int, data: dict[str, Any]) -> ModelT:
        obj = await self.get_by_id(pk)
        for k, v in data.items():
            setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, pk: int) -> None:
        obj = await self.get_by_id(pk)
        await self.db.delete(obj)
        await self.db.flush()
