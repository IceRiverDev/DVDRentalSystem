from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.base import AppBaseModel


# ──────────────────────── Inventory ────────────────────────
class InventoryBase(AppBaseModel):
    film_id: int
    store_id: int


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(AppBaseModel):
    film_id: int | None = None
    store_id: int | None = None


class InventoryResponse(InventoryBase):
    inventory_id: int
    last_update: datetime


# ──────────────────────── Rental ────────────────────────
class RentalBase(AppBaseModel):
    inventory_id: int
    customer_id: int
    staff_id: int


class RentalCreate(RentalBase):
    rental_date: datetime | None = None


class RentalReturn(AppBaseModel):
    return_date: datetime | None = None


class RentalUpdate(AppBaseModel):
    inventory_id: int | None = None
    customer_id: int | None = None
    staff_id: int | None = None
    return_date: datetime | None = None


class RentalResponse(RentalBase):
    rental_id: int
    rental_date: datetime
    return_date: datetime | None = None
    last_update: datetime


# ──────────────────────── Payment ────────────────────────
class PaymentBase(AppBaseModel):
    customer_id: int
    staff_id: int
    rental_id: int
    amount: Decimal = Field(ge=0)
    payment_date: datetime


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(AppBaseModel):
    amount: Decimal | None = Field(None, ge=0)
    payment_date: datetime | None = None


class PaymentResponse(PaymentBase):
    payment_id: int
