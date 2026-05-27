from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user
from app.modules.owner.MyBusiness.business_service import (
    list_businesses,
    create_business,
    get_business,
    update_business,
    delete_business
)

router = APIRouter(
    prefix="/business",
    tags=["business"]
)


class UpdateBusinessRequest(BaseModel):
    name: str | None = None
    logo_url: str | None = None
    currency: str | None = None
    timezone: str | None = None


class CreateBusinessRequest(BaseModel):
    name: str


@router.get("/all")
def list_businesses_endpoint(user=Depends(get_current_user)):
    return list_businesses(user["uid"])


@router.post("")
def create_business_endpoint(
    data: CreateBusinessRequest,
    user=Depends(get_current_user)
):
    if user["role"] != "OWNER":
        raise HTTPException(403, "Only owner can create businesses")

    name = data.name.strip()
    if not name:
        raise HTTPException(400, "Business name is required")

    return create_business(user["uid"], name)


@router.get("")
def get_business_endpoint(user=Depends(get_current_user)):

    business = get_business(user["business_id"])

    if not business:
        raise HTTPException(404, "Business not found")

    return business


@router.patch("")
def update_business_endpoint(
    data: UpdateBusinessRequest,
    user=Depends(get_current_user)
):
    if user["role"] != "OWNER":
        raise HTTPException(403, "Only owner can update business")

    business = update_business(
        user["business_id"],
        data.dict(exclude_none=True)
    )

    if not business:
        raise HTTPException(404, "Business not found")

    return business


@router.delete("")
def delete_business_endpoint(user=Depends(get_current_user)):
    if user["role"] != "OWNER":
        raise HTTPException(403, "Only owner can delete business")

    result = delete_business(user["business_id"])

    if not result:
        raise HTTPException(404, "Business not found")

    return result
