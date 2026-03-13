from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Actor, FilmActor
from app.services.base import BaseService


class ActorService(BaseService[Actor]):
    model = Actor

    async def get_actor_with_films(self, actor_id: int) -> Actor:
        q = (
            select(Actor)
            .where(Actor.actor_id == actor_id)
            .options(selectinload(Actor.film_actors).selectinload(FilmActor.film_rel))
        )
        result = await self.db.execute(q)
        actor = result.scalar_one_or_none()
        if actor is None:
            from fastapi import HTTPException, status

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor not found")
        return actor

    async def search_by_name(
        self,
        name: str,
        page: int = 1,
        size: int = 20,
        sort_by: str | None = None,
        order: str = "asc",
    ):
        from sqlalchemy import or_

        pattern = f"%{name}%"
        filters = [
            or_(
                Actor.first_name.ilike(pattern),
                Actor.last_name.ilike(pattern),
            )
        ]
        return await self.list(page=page, size=size, filters=filters, sort_by=sort_by, order=order)
