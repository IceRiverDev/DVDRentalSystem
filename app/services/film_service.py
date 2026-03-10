from __future__ import annotations

from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.models import Film, FilmActor, FilmCategory, Actor, Category, Language
from app.services.base import BaseService


class FilmService(BaseService[Film]):
    model = Film

    async def get_film_detail(self, film_id: int) -> Film:
        q = (
            select(Film)
            .where(Film.film_id == film_id)
            .options(
                selectinload(Film.language_rel),
                selectinload(Film.film_actors).selectinload(FilmActor.actor_rel),
                selectinload(Film.film_categories).selectinload(FilmCategory.category_rel),
            )
        )
        result = await self.db.execute(q)
        film = result.scalar_one_or_none()
        if film is None:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film not found")
        return film

    async def search(
        self,
        title: str | None = None,
        rating: str | None = None,
        language_id: int | None = None,
        category_id: int | None = None,
        page: int = 1,
        size: int = 20,
        sort_by: str | None = None,
        order: str = "asc",
    ):
        q = select(Film)
        count_q = select(__import__("sqlalchemy").func.count()).select_from(Film)

        if title:
            q = q.where(Film.title.ilike(f"%{title}%"))
            count_q = count_q.where(Film.title.ilike(f"%{title}%"))

        if rating:
            q = q.where(Film.rating == rating)
            count_q = count_q.where(Film.rating == rating)

        if language_id:
            q = q.where(Film.language_id == language_id)
            count_q = count_q.where(Film.language_id == language_id)

        if category_id:
            q = q.join(FilmCategory, Film.film_id == FilmCategory.film_id).where(
                FilmCategory.category_id == category_id
            )
            count_q = count_q.join(FilmCategory, Film.film_id == FilmCategory.film_id).where(
                FilmCategory.category_id == category_id
            )

        if sort_by:
            col = getattr(Film, sort_by, None)
            if col is not None:
                q = q.order_by(col.asc() if order == "asc" else col.desc())

        total = (await self.db.execute(count_q)).scalar_one()
        offset = (page - 1) * size
        rows = (await self.db.execute(q.offset(offset).limit(size))).scalars().all()
        return list(rows), total

    async def add_actor(self, film_id: int, actor_id: int) -> None:
        from app.models import FilmActor
        from sqlalchemy import select
        existing = await self.db.execute(
            select(FilmActor).where(
                FilmActor.film_id == film_id,
                FilmActor.actor_id == actor_id,
            )
        )
        if existing.scalar_one_or_none():
            return
        self.db.add(FilmActor(film_id=film_id, actor_id=actor_id))
        await self.db.flush()

    async def remove_actor(self, film_id: int, actor_id: int) -> None:
        from app.models import FilmActor
        obj = (await self.db.execute(
            select(FilmActor).where(
                FilmActor.film_id == film_id,
                FilmActor.actor_id == actor_id,
            )
        )).scalar_one_or_none()
        if obj:
            await self.db.delete(obj)
            await self.db.flush()

    async def add_category(self, film_id: int, category_id: int) -> None:
        from app.models import FilmCategory
        existing = await self.db.execute(
            select(FilmCategory).where(
                FilmCategory.film_id == film_id,
                FilmCategory.category_id == category_id,
            )
        )
        if existing.scalar_one_or_none():
            return
        self.db.add(FilmCategory(film_id=film_id, category_id=category_id))
        await self.db.flush()
