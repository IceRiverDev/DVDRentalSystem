from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import PaginationParams, build_paged_response, pagination_params
from app.core.database import DBSession
from app.schemas import (
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
    MessageResponse,
    PagedResponse,
)
from app.services import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])
Pagination = Annotated[PaginationParams, Depends(pagination_params)]

ALLOWED_SORT_FIELDS = {"inventory_id", "film_id", "store_id", "last_update"}


@router.get("", response_model=PagedResponse[InventoryResponse])
async def list_inventory(
    db: DBSession,
    pagination: Pagination,
    store_id: int | None = None,
    sort_by: str | None = Query(None),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = None
    svc = InventoryService(db)
    if store_id:
        items, total = await svc.get_store_inventory(
            store_id,
            page=pagination.page,
            size=pagination.size,
            sort_by=sort_by,
            order=order,
        )
    else:
        items, total = await svc.list(
            page=pagination.page, size=pagination.size, sort_by=sort_by, order=order
        )
    return build_paged_response(items, total, pagination.page, pagination.size)


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(body: InventoryCreate, db: DBSession):
    svc = InventoryService(db)
    return await svc.create(body.model_dump())


@router.get("/available", response_model=PagedResponse[InventoryResponse])
async def get_available_inventory(
    db: DBSession,
    pagination: Pagination,
    film_id: int = 1,
    store_id: int | None = None,
):
    svc = InventoryService(db)
    items, total = await svc.get_available_inventory(
        film_id=film_id,
        store_id=store_id,
        page=pagination.page,
        size=pagination.size,
    )
    return build_paged_response(items, total, pagination.page, pagination.size)


@router.get("/{inventory_id}", response_model=InventoryResponse)
async def get_inventory(inventory_id: int, db: DBSession):
    svc = InventoryService(db)
    return await svc.get_by_id(inventory_id)


@router.patch("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(inventory_id: int, body: InventoryUpdate, db: DBSession):
    svc = InventoryService(db)
    return await svc.update(inventory_id, body.model_dump(exclude_none=True))


@router.delete("/{inventory_id}", response_model=MessageResponse)
async def delete_inventory(inventory_id: int, db: DBSession):
    svc = InventoryService(db)
    await svc.delete(inventory_id)
    return {"message": "Inventory item deleted"}
