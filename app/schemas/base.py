from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PagedResponse[T](AppBaseModel):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class MessageResponse(AppBaseModel):
    message: str
