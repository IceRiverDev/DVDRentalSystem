from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from pydantic import Field, EmailStr
from app.schemas.base import AppBaseModel
from app.schemas.geography import AddressResponse


# ──────────────────────── Customer ────────────────────────
class CustomerBase(AppBaseModel):
    store_id: int
    first_name: str = Field(max_length=45)
    last_name: str = Field(max_length=45)
    email: Optional[str] = Field(None, max_length=50)
    address_id: int
    activebool: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(AppBaseModel):
    store_id: Optional[int] = None
    first_name: Optional[str] = Field(None, max_length=45)
    last_name: Optional[str] = Field(None, max_length=45)
    email: Optional[str] = Field(None, max_length=50)
    address_id: Optional[int] = None
    activebool: Optional[bool] = None
    active: Optional[int] = None


class CustomerResponse(CustomerBase):
    customer_id: int
    create_date: date
    last_update: Optional[datetime] = None
    active: Optional[int] = None


class CustomerDetailResponse(CustomerResponse):
    address_rel: Optional[AddressResponse] = None


# ──────────────────────── Staff ────────────────────────
class StaffBase(AppBaseModel):
    first_name: str = Field(max_length=45)
    last_name: str = Field(max_length=45)
    address_id: int
    email: Optional[str] = Field(None, max_length=50)
    store_id: int
    active: bool = True
    username: str = Field(max_length=16)


class StaffCreate(StaffBase):
    password: Optional[str] = Field(None, max_length=40)


class StaffUpdate(AppBaseModel):
    first_name: Optional[str] = Field(None, max_length=45)
    last_name: Optional[str] = Field(None, max_length=45)
    address_id: Optional[int] = None
    email: Optional[str] = Field(None, max_length=50)
    store_id: Optional[int] = None
    active: Optional[bool] = None
    username: Optional[str] = Field(None, max_length=16)
    password: Optional[str] = Field(None, max_length=40)


class StaffResponse(StaffBase):
    staff_id: int
    last_update: datetime


# ──────────────────────── Store ────────────────────────
class StoreBase(AppBaseModel):
    manager_staff_id: int
    address_id: int


class StoreCreate(StoreBase):
    pass


class StoreUpdate(AppBaseModel):
    manager_staff_id: Optional[int] = None
    address_id: Optional[int] = None


class StoreResponse(StoreBase):
    store_id: int
    last_update: datetime


class StoreDetailResponse(StoreResponse):
    manager_rel: Optional[StaffResponse] = None
    address_rel: Optional[AddressResponse] = None
