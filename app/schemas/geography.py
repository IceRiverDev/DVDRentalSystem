from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.base import AppBaseModel


# ──────────────────────── Country ────────────────────────
class CountryBase(AppBaseModel):
    country: str = Field(max_length=50)


class CountryCreate(CountryBase):
    pass


class CountryUpdate(AppBaseModel):
    country: str | None = Field(None, max_length=50)


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
    city: str | None = Field(None, max_length=50)
    country_id: int | None = None


class CityResponse(CityBase):
    city_id: int
    last_update: datetime


class CityDetailResponse(CityResponse):
    country_rel: CountryResponse | None = None


# ──────────────────────── Address ────────────────────────
class AddressBase(AppBaseModel):
    address: str = Field(max_length=50)
    address2: str | None = Field(None, max_length=50)
    district: str = Field(max_length=20)
    city_id: int
    postal_code: str | None = Field(None, max_length=10)
    phone: str = Field(max_length=20)


class AddressCreate(AddressBase):
    pass


class AddressUpdate(AppBaseModel):
    address: str | None = Field(None, max_length=50)
    address2: str | None = Field(None, max_length=50)
    district: str | None = Field(None, max_length=20)
    city_id: int | None = None
    postal_code: str | None = Field(None, max_length=10)
    phone: str | None = Field(None, max_length=20)


class AddressResponse(AddressBase):
    address_id: int
    last_update: datetime
