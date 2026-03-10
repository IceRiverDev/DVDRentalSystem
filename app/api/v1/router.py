from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.v1 import actors, auth, customers, films, inventory, payments, reference, rentals

router = APIRouter()

router.include_router(auth.router)
router.include_router(actors.router)
router.include_router(films.router)
router.include_router(customers.router)
router.include_router(rentals.router)
router.include_router(payments.router)
router.include_router(inventory.router)
router.include_router(reference.router)


@router.get("/health", include_in_schema=False)
async def health_check():
    return JSONResponse({"status": "ok"})
