from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.base import AppBaseModel


# ──────────────────────── Language ────────────────────────
class LanguageBase(AppBaseModel):
    name: str = Field(max_length=20)


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdate(AppBaseModel):
    name: str | None = Field(None, max_length=20)


class LanguageResponse(LanguageBase):
    language_id: int
    last_update: datetime


# ──────────────────────── Category ────────────────────────
class CategoryBase(AppBaseModel):
    name: str = Field(max_length=25)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(AppBaseModel):
    name: str | None = Field(None, max_length=25)


class CategoryResponse(CategoryBase):
    category_id: int
    last_update: datetime


# ──────────────────────── Actor ────────────────────────
class ActorBase(AppBaseModel):
    first_name: str = Field(max_length=45)
    last_name: str = Field(max_length=45)


class ActorCreate(ActorBase):
    pass


class ActorUpdate(AppBaseModel):
    first_name: str | None = Field(None, max_length=45)
    last_name: str | None = Field(None, max_length=45)


class ActorResponse(ActorBase):
    actor_id: int
    last_update: datetime
