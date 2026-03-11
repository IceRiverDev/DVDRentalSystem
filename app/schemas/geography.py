from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.schemas.base import AppBaseModel


# ──────────────────────── Country ────────────────────────
class CountryBase(AppBaseModel):
    country: str = Field(max_length=50)


class CountryCreate(CountryBase):
    pass


class CountryUpdate(AppBaseModel):
    country: Optional[str] = Field(None, max_length=50)


class CountryResponse(CountryBase):
    country_id: int
    last_update: datetime


# ──────────────────────── City ────────────────────────
class CityBase(AppBaseModel):
    city: str = Field(max_length=50)
    country_id: int


class CityCreate(CityBase):
    pass


class CityUpdate(AppBaseModel):
    city: Optional[str] = Field(None, max_length=50)
    country_id: Optional[int] = None


class CityResponse(CityBase):
    city_id: int
    last_update: datetime


class CityDetailResponse(CityResponse):
    country_rel: Optional[CountryResponse] = None


# ──────────────────────── Address ────────────────────────
class AddressBase(AppBaseModel):
    address: str = Field(max_length=50)
    address2: Optional[str] = Field(None, max_length=50)
    district: str = Field(max_length=20)
    city_id: int
    postal_code: Optional[str] = Field(None, max_length=10)
    phone: str = Field(max_length=20)


class AddressCreate(AddressBase):
    pass


class AddressUpdate(AppBaseModel):
    address: Optional[str] = Field(None, max_length=50)
    address2: Optional[str] = Field(None, max_length=50)
    district: Optional[str] = Field(None, max_length=20)
    city_id: Optional[int] = None
    postal_code: Optional[str] = Field(None, max_length=10)
    phone: Optional[str] = Field(None, max_length=20)


class AddressResponse(AddressBase):
    address_id: int
    last_update: datetime
