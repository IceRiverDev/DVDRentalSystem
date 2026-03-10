from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import PaginationParams, pagination_params, build_paged_response
from app.core.database import DBSession
from app.schemas import (
    RentalCreate, RentalReturn, RentalUpdate, RentalResponse,
    PagedResponse, MessageResponse,
)
from app.services import RentalService

router = APIRouter(prefix="/rentals", tags=["Rentals"])
Pagination = Annotated[PaginationParams, Depends(pagination_params)]

ALLOWED_SORT_FIELDS = {"rental_id", "rental_date", "return_date", "customer_id", "staff_id"}


@router.get("", response_model=PagedResponse[RentalResponse])
async def list_rentals(
    db: DBSession,
    pagination: Pagination,
    sort_by: str | None = Query(None),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = None
    svc = RentalService(db)
    from app.models import Rental
    if sort_by:
        items, total = await svc.list(
            page=pagination.page, size=pagination.size, sort_by=sort_by, order=order
        )
    else:
        items, total = await svc.list(
            page=pagination.page, size=pagination.size, order_by=Rental.rental_date.desc()
        )
    return build_paged_response(items, total, pagination.page, pagination.size)


@router.post("", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
async def create_rental(body: RentalCreate, db: DBSession):
    svc = RentalService(db)
    return await svc.create_rental(
        inventory_id=body.inventory_id,
        customer_id=body.customer_id,
        staff_id=body.staff_id,
    )


@router.get("/overdue", response_model=PagedResponse[RentalResponse])
async def list_overdue_rentals(db: DBSession, pagination: Pagination):
    svc = RentalService(db)
    items, total = await svc.get_overdue_rentals(page=pagination.page, size=pagination.size)
    return build_paged_response(items, total, pagination.page, pagination.size)


@router.get("/{rental_id}", response_model=RentalResponse)
async def get_rental(rental_id: int, db: DBSession):
    svc = RentalService(db)
    return await svc.get_by_id(rental_id)


@router.post("/{rental_id}/return", response_model=RentalResponse)
async def return_rental(rental_id: int, body: RentalReturn, db: DBSession):
    svc = RentalService(db)
    return await svc.return_rental(rental_id, body.return_date)


@router.patch("/{rental_id}", response_model=RentalResponse)
async def update_rental(rental_id: int, body: RentalUpdate, db: DBSession):
    svc = RentalService(db)
    return await svc.update(rental_id, body.model_dump(exclude_none=True))


@router.delete("/{rental_id}", response_model=MessageResponse)
async def delete_rental(rental_id: int, db: DBSession):
    svc = RentalService(db)
    await svc.delete(rental_id)
    return {"message": "Rental deleted"}
