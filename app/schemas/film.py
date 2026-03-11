from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field

from app.models.models import MpaaRating
from app.schemas.base import AppBaseModel
from app.schemas.catalog import ActorResponse, CategoryResponse, LanguageResponse


class FilmBase(AppBaseModel):
    title: str = Field(max_length=255)
    description: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1888, le=2100)
    language_id: int
    rental_duration: int = Field(default=3, ge=1)
    rental_rate: Decimal = Field(default=Decimal("4.99"), ge=0)
    length: Optional[int] = Field(None, ge=1)
    replacement_cost: Decimal = Field(default=Decimal("19.99"), ge=0)
    rating: Optional[MpaaRating] = MpaaRating.G
    special_features: Optional[list[str]] = None


class FilmCreate(FilmBase):
    pass


class FilmUpdate(AppBaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    release_year: Optional[int] = Field(None, ge=1888, le=2100)
    language_id: Optional[int] = None
    rental_duration: Optional[int] = Field(None, ge=1)
    rental_rate: Optional[Decimal] = Field(None, ge=0)
    length: Optional[int] = Field(None, ge=1)
    replacement_cost: Optional[Decimal] = Field(None, ge=0)
    rating: Optional[MpaaRating] = None
    special_features: Optional[list[str]] = None


class FilmResponse(FilmBase):
    film_id: int
    last_update: datetime


class FilmDetailResponse(FilmResponse):
    language_rel: Optional[LanguageResponse] = None
    actors: list[ActorResponse] = []
    categories: list[CategoryResponse] = []
