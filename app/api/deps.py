from __future__ import annotations

from math import ceil
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()


class PaginationParams(BaseModel):
    page: int = 1
    size: int = settings.DEFAULT_PAGE_SIZE

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


def pagination_params(
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
) -> PaginationParams:
    return PaginationParams(page=page, size=size)


def build_paged_response(items, total: int, page: int, size: int) -> dict:
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": ceil(total / size) if size else 0,
    }
