from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import PaginationParams, pagination_params, build_paged_response
from app.core.database import DBSession
from app.models import Category, Language, Country, City
from app.schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    LanguageCreate, LanguageUpdate, LanguageResponse,
    CountryCreate, CountryUpdate, CountryResponse,
    CityCreate, CityUpdate, CityResponse, CityDetailResponse,
    AddressCreate, AddressUpdate, AddressResponse,
    StaffCreate, StaffUpdate, StaffResponse,
    StoreCreate, StoreUpdate, StoreResponse, StoreDetailResponse,
    PagedResponse, MessageResponse,
)
from app.services.base import BaseService

router = APIRouter(tags=["Reference Data"])


# ──── Categories ────
cat_router = APIRouter(prefix="/categories")

@cat_router.get("", response_model=list[CategoryResponse])
async def list_categories(db: DBSession):
    svc = BaseService.__class_getitem__(Category)
    from sqlalchemy import select
    rows = (await db.execute(select(Category).order_by(Category.name))).scalars().all()
    return rows

@cat_router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(body: CategoryCreate, db: DBSession):
    from app.models import Category as M
    obj = M(**body.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj

@cat_router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, body: CategoryUpdate, db: DBSession):
    obj = await db.get(Category, category_id)
    if obj is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Category not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await db.flush(); await db.refresh(obj)
    return obj

@cat_router.delete("/{category_id}", response_model=MessageResponse)
async def delete_category(category_id: int, db: DBSession):
    obj = await db.get(Category, category_id)
    if obj is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Category not found")
    await db.delete(obj); await db.flush()
    return {"message": "Category deleted"}


# ──── Languages ────
lang_router = APIRouter(prefix="/languages")

@lang_router.get("", response_model=list[LanguageResponse])
async def list_languages(db: DBSession):
    from sqlalchemy import select
    return (await db.execute(select(Language).order_by(Language.name))).scalars().all()

@lang_router.post("", response_model=LanguageResponse, status_code=status.HTTP_201_CREATED)
async def create_language(body: LanguageCreate, db: DBSession):
    obj = Language(**body.model_dump())
    db.add(obj); await db.flush(); await db.refresh(obj)
    return obj

@lang_router.patch("/{language_id}", response_model=LanguageResponse)
async def update_language(language_id: int, body: LanguageUpdate, db: DBSession):
    obj = await db.get(Language, language_id)
    if obj is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Language not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await db.flush(); await db.refresh(obj)
    return obj


# ──── Countries ────
country_router = APIRouter(prefix="/countries")

@country_router.get("", response_model=list[CountryResponse])
async def list_countries(db: DBSession):
    from sqlalchemy import select
    return (await db.execute(select(Country).order_by(Country.country))).scalars().all()

@country_router.get("/{country_id}", response_model=CountryResponse)
async def get_country(country_id: int, db: DBSession):
    obj = await db.get(Country, country_id)
    if obj is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Country not found")
    return obj


# ──── Cities ────
city_router = APIRouter(prefix="/cities")

@city_router.get("", response_model=list[CityResponse])
async def list_cities(db: DBSession, country_id: int | None = None):
    from sqlalchemy import select
    q = select(City).order_by(City.city)
    if country_id:
        q = q.where(City.country_id == country_id)
    return (await db.execute(q)).scalars().all()


# ──── Staff ────
staff_router = APIRouter(prefix="/staff")

@staff_router.get("", response_model=list[StaffResponse])
async def list_staff(db: DBSession):
    from app.models import Staff
    from sqlalchemy import select
    return (await db.execute(select(Staff))).scalars().all()

@staff_router.get("/{staff_id}", response_model=StaffResponse)
async def get_staff(staff_id: int, db: DBSession):
    from app.models import Staff
    obj = await db.get(Staff, staff_id)
    if obj is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Staff not found")
    return obj

@staff_router.patch("/{staff_id}", response_model=StaffResponse)
async def update_staff(staff_id: int, body: StaffUpdate, db: DBSession):
    from app.models import Staff
    obj = await db.get(Staff, staff_id)
    if obj is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Staff not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await db.flush(); await db.refresh(obj)
    return obj


# ──── Stores ────
store_router = APIRouter(prefix="/stores")

@store_router.get("", response_model=list[StoreResponse])
async def list_stores(db: DBSession):
    from app.models import Store
    from sqlalchemy import select
    return (await db.execute(select(Store))).scalars().all()

@store_router.get("/{store_id}", response_model=StoreDetailResponse)
async def get_store(store_id: int, db: DBSession):
    from app.models import Store
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    q = (
        select(Store)
        .where(Store.store_id == store_id)
        .options(selectinload(Store.manager_rel), selectinload(Store.address_rel))
    )
    obj = (await db.execute(q)).scalar_one_or_none()
    if obj is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Store not found")
    return obj


# Register all sub-routers
router.include_router(cat_router)
router.include_router(lang_router)
router.include_router(country_router)
router.include_router(city_router)
router.include_router(staff_router)
router.include_router(store_router)
