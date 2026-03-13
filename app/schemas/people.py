from __future__ import annotations

from datetime import date, datetime

from pydantic import Field

from app.schemas.base import AppBaseModel
from app.schemas.geography import AddressResponse


# ──────────────────────── Customer ────────────────────────
class CustomerBase(AppBaseModel):
    store_id: int
    first_name: str = Field(max_length=45)
    last_name: str = Field(max_length=45)
    email: str | None = Field(None, max_length=50)
    address_id: int
    activebool: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(AppBaseModel):
    store_id: int | None = None
    first_name: str | None = Field(None, max_length=45)
    last_name: str | None = Field(None, max_length=45)
    email: str | None = Field(None, max_length=50)
    address_id: int | None = None
    activebool: bool | None = None
    active: int | None = None


class CustomerResponse(CustomerBase):
    customer_id: int
    create_date: date
    last_update: datetime | None = None
    active: int | None = None


class CustomerDetailResponse(CustomerResponse):
    address_rel: AddressResponse | None = None


# ──────────────────────── Staff ────────────────────────
class StaffBase(AppBaseModel):
    first_name: str = Field(max_length=45)
    last_name: str = Field(max_length=45)
    address_id: int
    email: str | None = Field(None, max_length=50)
    store_id: int
    active: bool = True
    username: str = Field(max_length=16)


class StaffCreate(StaffBase):
    password: str | None = Field(None, max_length=40)


class StaffUpdate(AppBaseModel):
    first_name: str | None = Field(None, max_length=45)
    last_name: str | None = Field(None, max_length=45)
    address_id: int | None = None
    email: str | None = Field(None, max_length=50)
    store_id: int | None = None
    active: bool | None = None
    username: str | None = Field(None, max_length=16)
    password: str | None = Field(None, max_length=40)


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
    manager_staff_id: int | None = None
    address_id: int | None = None


class StoreResponse(StoreBase):
    store_id: int
    last_update: datetime


class StoreDetailResponse(StoreResponse):
    manager_rel: StaffResponse | None = None
    address_rel: AddressResponse | None = None
