"""API v1 company routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_company_orchestrator
from app.application.company_orchestrator import CompanyNotFoundError, CompanyOrchestrator
from app.schemas.company import (
    CompanyCreateRequest,
    CompanyDetailResponse,
    CreateCompanyResponse,
    StartCompanyResponse,
)

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CreateCompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    payload: CompanyCreateRequest,
    orchestrator: CompanyOrchestrator = Depends(get_company_orchestrator),
) -> CreateCompanyResponse:
    try:
        return orchestrator.create_company(payload.idea)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.post("/{company_id}/start", response_model=StartCompanyResponse)
def start_company(
    company_id: UUID,
    orchestrator: CompanyOrchestrator = Depends(get_company_orchestrator),
) -> StartCompanyResponse:
    try:
        return orchestrator.start_company(company_id)
    except CompanyNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get("/{company_id}", response_model=CompanyDetailResponse)
def get_company(
    company_id: UUID,
    orchestrator: CompanyOrchestrator = Depends(get_company_orchestrator),
) -> CompanyDetailResponse:
    try:
        return orchestrator.get_company(company_id)
    except CompanyNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
