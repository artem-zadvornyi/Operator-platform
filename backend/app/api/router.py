"""Root API router."""

from fastapi import APIRouter

from app.api.v1.companies import router as companies_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(companies_router)
