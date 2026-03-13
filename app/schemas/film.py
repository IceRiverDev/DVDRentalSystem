from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.models.models import MpaaRating
from app.schemas.base import AppBaseModel
from app.schemas.catalog import ActorResponse, CategoryResponse, LanguageResponse


class FilmBase(AppBaseModel):
    title: str = Field(max_length=255)
    description: str | None = None
    release_year: int | None = Field(None, ge=1888, le=2100)
    language_id: int
    rental_duration: int = Field(default=3, ge=1)
    rental_rate: Decimal = Field(default=Decimal("4.99"), ge=0)
    length: int | None = Field(None, ge=1)
    replacement_cost: Decimal = Field(default=Decimal("19.99"), ge=0)
    rating: MpaaRating | None = MpaaRating.G
    special_features: list[str] | None = None


class FilmCreate(FilmBase):
    pass


class FilmUpdate(AppBaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    release_year: int | None = Field(None, ge=1888, le=2100)
    language_id: int | None = None
    rental_duration: int | None = Field(None, ge=1)
    rental_rate: Decimal | None = Field(None, ge=0)
    length: int | None = Field(None, ge=1)
    replacement_cost: Decimal | None = Field(None, ge=0)
    rating: MpaaRating | None = None
    special_features: list[str] | None = None


class FilmResponse(FilmBase):
    film_id: int
    last_update: datetime


class FilmDetailResponse(FilmResponse):
    language_rel: LanguageResponse | None = None
    actors: list[ActorResponse] = []
    categories: list[CategoryResponse] = []
