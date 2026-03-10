from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field
from app.schemas.base import AppBaseModel


# ──────────────────────── Inventory ────────────────────────
class InventoryBase(AppBaseModel):
    film_id: int
    store_id: int


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(AppBaseModel):
    film_id: Optional[int] = None
    store_id: Optional[int] = None


class InventoryResponse(InventoryBase):
    inventory_id: int
    last_update: datetime


# ──────────────────────── Rental ────────────────────────
class RentalBase(AppBaseModel):
    inventory_id: int
    customer_id: int
    staff_id: int


class RentalCreate(RentalBase):
    rental_date: Optional[datetime] = None


class RentalReturn(AppBaseModel):
    return_date: Optional[datetime] = None


class RentalUpdate(AppBaseModel):
    inventory_id: Optional[int] = None
    customer_id: Optional[int] = None
    staff_id: Optional[int] = None
    return_date: Optional[datetime] = None


class RentalResponse(RentalBase):
    rental_id: int
    rental_date: datetime
    return_date: Optional[datetime] = None
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
    amount: Optional[Decimal] = Field(None, ge=0)
    payment_date: Optional[datetime] = None


class PaymentResponse(PaymentBase):
    payment_id: int
