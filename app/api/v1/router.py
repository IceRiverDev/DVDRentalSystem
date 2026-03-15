from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.v1 import (
    actors,
    auth,
    customers,
    films,
    inventory,
    payments,
    reference,
    rentals,
)
from app.core.security import get_current_user

router = APIRouter()

_protected = [Depends(get_current_user)]

router.include_router(auth.router)
router.include_router(actors.router, dependencies=_protected)
router.include_router(films.router, dependencies=_protected)
router.include_router(customers.router, dependencies=_protected)
router.include_router(rentals.router, dependencies=_protected)
router.include_router(payments.router, dependencies=_protected)
router.include_router(inventory.router, dependencies=_protected)
router.include_router(reference.router, dependencies=_protected)


@router.get("/health", include_in_schema=False)
async def health_check():
    return JSONResponse({"status": "ok"})
