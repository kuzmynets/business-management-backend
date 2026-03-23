from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.security import get_current_user
from app.modules.owner.MyBusiness.service_business import get_business_by_id, update_business, deactivate_business

router = APIRouter(prefix="/business", tags=["business"])

@router.get("/{business_id}")
def read_business(business_id: str, current_user: dict = Depends(get_current_user)):
    business = get_business_by_id(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.patch("/{business_id}")
def patch_business(
    business_id: str,
    data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    name = data.get("name")
    subscription = data.get("subscription")

    if name is None and subscription is None:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        return update_business(
            business_id=business_id,
            name=name,
            subscription=subscription
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{business_id}/deactivate")
def post_deactivate_business(business_id: str, current_user: dict = Depends(get_current_user)):
    try:
        return deactivate_business(business_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))