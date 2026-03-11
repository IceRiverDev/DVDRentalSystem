from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class AppBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PagedResponse(AppBaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class MessageResponse(AppBaseModel):
    message: str
