from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import PaginationParams, pagination_params, build_paged_response
from app.core.database import DBSession
from app.schemas import (
    PaymentCreate, PaymentUpdate, PaymentResponse,
    PagedResponse, MessageResponse,
)
from app.services import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])
Pagination = Annotated[PaginationParams, Depends(pagination_params)]

ALLOWED_SORT_FIELDS = {"payment_id", "amount", "payment_date", "customer_id"}


@router.get("", response_model=PagedResponse[PaymentResponse])
async def list_payments(
    db: DBSession,
    pagination: Pagination,
    customer_id: int | None = None,
    sort_by: str | None = Query(None),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = None
    svc = PaymentService(db)
    from app.models import Payment
    if customer_id:
        items, total = await svc.get_customer_payments(
            customer_id, page=pagination.page, size=pagination.size,
            sort_by=sort_by, order=order,
        )
    else:
        if sort_by:
            items, total = await svc.list(
                page=pagination.page, size=pagination.size, sort_by=sort_by, order=order
            )
        else:
            items, total = await svc.list(
                page=pagination.page, size=pagination.size, order_by=Payment.payment_date.desc()
            )
    return build_paged_response(items, total, pagination.page, pagination.size)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(body: PaymentCreate, db: DBSession):
    svc = PaymentService(db)
    return await svc.create(body.model_dump())


@router.get("/summary", response_model=dict)
async def revenue_summary(db: DBSession):
    svc = PaymentService(db)
    return await svc.get_revenue_summary()


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int, db: DBSession):
    svc = PaymentService(db)
    return await svc.get_by_id(payment_id)


@router.patch("/{payment_id}", response_model=PaymentResponse)
async def update_payment(payment_id: int, body: PaymentUpdate, db: DBSession):
    svc = PaymentService(db)
    return await svc.update(payment_id, body.model_dump(exclude_none=True))


@router.delete("/{payment_id}", response_model=MessageResponse)
async def delete_payment(payment_id: int, db: DBSession):
    svc = PaymentService(db)
    await svc.delete(payment_id)
    return {"message": "Payment deleted"}
