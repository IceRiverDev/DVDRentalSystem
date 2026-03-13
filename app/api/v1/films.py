from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import PaginationParams, build_paged_response, pagination_params
from app.core.database import DBSession
from app.schemas import (
    FilmCreate,
    FilmDetailResponse,
    FilmResponse,
    FilmUpdate,
    MessageResponse,
    PagedResponse,
)
from app.services import FilmService

router = APIRouter(prefix="/films", tags=["Films"])
Pagination = Annotated[PaginationParams, Depends(pagination_params)]

ALLOWED_SORT_FIELDS = {
    "film_id",
    "title",
    "release_year",
    "rental_rate",
    "length",
    "rental_duration",
    "rating",
}


@router.get("", response_model=PagedResponse[FilmResponse])
async def list_films(
    db: DBSession,
    pagination: Pagination,
    title: str | None = None,
    rating: str | None = None,
    language_id: int | None = None,
    category_id: int | None = None,
    sort_by: str | None = Query(None),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = None
    svc = FilmService(db)
    items, total = await svc.search(
        title=title,
        rating=rating,
        language_id=language_id,
        category_id=category_id,
        page=pagination.page,
        size=pagination.size,
        sort_by=sort_by,
        order=order,
    )
    return build_paged_response(items, total, pagination.page, pagination.size)


@router.post("", response_model=FilmResponse, status_code=status.HTTP_201_CREATED)
async def create_film(body: FilmCreate, db: DBSession):
    svc = FilmService(db)
    data = body.model_dump()
    data.setdefault("fulltext", "")
    return await svc.create(data)


@router.get("/{film_id}", response_model=FilmDetailResponse)
async def get_film(film_id: int, db: DBSession):
    svc = FilmService(db)
    film = await svc.get_film_detail(film_id)
    # Flatten nested relationships for the response
    film.__dict__["actors"] = [fa.actor_rel for fa in film.film_actors]
    film.__dict__["categories"] = [fc.category_rel for fc in film.film_categories]
    return film


@router.patch("/{film_id}", response_model=FilmResponse)
async def update_film(film_id: int, body: FilmUpdate, db: DBSession):
    svc = FilmService(db)
    return await svc.update(film_id, body.model_dump(exclude_none=True))


@router.delete("/{film_id}", response_model=MessageResponse)
async def delete_film(film_id: int, db: DBSession):
    svc = FilmService(db)
    await svc.delete(film_id)
    return {"message": "Film deleted"}


@router.post("/{film_id}/actors/{actor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_actor_to_film(film_id: int, actor_id: int, db: DBSession):
    svc = FilmService(db)
    await svc.add_actor(film_id, actor_id)


@router.delete("/{film_id}/actors/{actor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_actor_from_film(film_id: int, actor_id: int, db: DBSession):
    svc = FilmService(db)
    await svc.remove_actor(film_id, actor_id)


@router.post("/{film_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_category_to_film(film_id: int, category_id: int, db: DBSession):
    svc = FilmService(db)
    await svc.add_category(film_id, category_id)
