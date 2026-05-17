from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user
from app.modules.owner.MyBusiness.business_service import (
    get_business,
    update_business,
    deactivate_business,
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

    business = update_business(
        user["business_id"],
        data.dict(exclude_none=True)
    )

    if not business:
        raise HTTPException(404, "Business not found")

    return business


@router.post("/deactivate")
def deactivate_business_endpoint(user=Depends(get_current_user)):

    result = deactivate_business(user["business_id"])

    if not result:
        raise HTTPException(404, "Business not found")

    return result


@router.delete("")
def delete_business_endpoint(user=Depends(get_current_user)):

    result = delete_business(user["business_id"])

    if not result:
        raise HTTPException(404, "Business not found")

    return result