from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import PaginationParams, build_paged_response, pagination_params
from app.core.database import DBSession
from app.models import Actor
from app.schemas import (
    ActorCreate,
    ActorResponse,
    ActorUpdate,
    MessageResponse,
    PagedResponse,
)
from app.services import ActorService

router = APIRouter(prefix="/actors", tags=["Actors"])
Pagination = Annotated[PaginationParams, Depends(pagination_params)]

ALLOWED_SORT_FIELDS = {"actor_id", "first_name", "last_name", "last_update"}


@router.get("", response_model=PagedResponse[ActorResponse])
async def list_actors(
    db: DBSession,
    pagination: Pagination,
    name: str | None = None,
    sort_by: str | None = Query(None),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = None
    svc = ActorService(db)
    if name:
        items, total = await svc.search_by_name(
            name, page=pagination.page, size=pagination.size, sort_by=sort_by, order=order
        )
    else:
        items, total = await svc.list(
            page=pagination.page,
            size=pagination.size,
            sort_by=sort_by,
            order=order,
            order_by=Actor.last_name if not sort_by else None,
        )
    return build_paged_response(items, total, pagination.page, pagination.size)


@router.post("", response_model=ActorResponse, status_code=status.HTTP_201_CREATED)
async def create_actor(body: ActorCreate, db: DBSession):
    svc = ActorService(db)
    return await svc.create(body.model_dump())


@router.get("/{actor_id}", response_model=ActorResponse)
async def get_actor(actor_id: int, db: DBSession):
    svc = ActorService(db)
    return await svc.get_by_id(actor_id)


@router.patch("/{actor_id}", response_model=ActorResponse)
async def update_actor(actor_id: int, body: ActorUpdate, db: DBSession):
    svc = ActorService(db)
    return await svc.update(actor_id, body.model_dump(exclude_none=True))


@router.delete("/{actor_id}", response_model=MessageResponse)
async def delete_actor(actor_id: int, db: DBSession):
    svc = ActorService(db)
    await svc.delete(actor_id)
    return {"message": "Actor deleted"}


@router.get("/{actor_id}/films", response_model=list[dict])
async def get_actor_films(actor_id: int, db: DBSession):
    svc = ActorService(db)
    actor = await svc.get_actor_with_films(actor_id)
    return [
        {
            "film_id": fa.film_rel.film_id,
            "title": fa.film_rel.title,
            "release_year": fa.film_rel.release_year,
            "rating": fa.film_rel.rating,
        }
        for fa in actor.film_actors
    ]
