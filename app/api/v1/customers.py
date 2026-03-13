from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import PaginationParams, build_paged_response, pagination_params
from app.core.database import DBSession
from app.schemas import (
    CustomerCreate,
    CustomerDetailResponse,
    CustomerResponse,
    CustomerUpdate,
    MessageResponse,
    PagedResponse,
    RentalResponse,
)
from app.services import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])
Pagination = Annotated[PaginationParams, Depends(pagination_params)]

ALLOWED_SORT_FIELDS = {"customer_id", "first_name", "last_name", "email", "store_id", "create_date"}


@router.get("", response_model=PagedResponse[CustomerResponse])
async def list_customers(
    db: DBSession,
    pagination: Pagination,
    name: str | None = None,
    email: str | None = None,
    active: bool | None = None,
    sort_by: str | None = Query(None),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = None
    svc = CustomerService(db)
    items, total = await svc.search(
        name=name,
        email=email,
        active=active,
        page=pagination.page,
        size=pagination.size,
        sort_by=sort_by,
        order=order,
    )
    return build_paged_response(items, total, pagination.page, pagination.size)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(body: CustomerCreate, db: DBSession):
    svc = CustomerService(db)
    return await svc.create(body.model_dump())


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(customer_id: int, db: DBSession):
    svc = CustomerService(db)
    return await svc.get_detail(customer_id)


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, body: CustomerUpdate, db: DBSession):
    svc = CustomerService(db)
    return await svc.update(customer_id, body.model_dump(exclude_none=True))


@router.delete("/{customer_id}", response_model=MessageResponse)
async def delete_customer(customer_id: int, db: DBSession):
    svc = CustomerService(db)
    await svc.delete(customer_id)
    return {"message": "Customer deleted"}


@router.get("/{customer_id}/rentals", response_model=PagedResponse[RentalResponse])
async def get_customer_rentals(customer_id: int, db: DBSession, pagination: Pagination):
    svc = CustomerService(db)
    items, total = await svc.get_rental_history(
        customer_id, page=pagination.page, size=pagination.size
    )
    return build_paged_response(items, total, pagination.page, pagination.size)
