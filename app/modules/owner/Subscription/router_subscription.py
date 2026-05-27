from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.modules.owner.Subscription.subscription_service import (
    get_subscription_for_business,
    set_subscription_for_business
)
from app.modules.owner.Subscription.subscription_models import SubscribeRequest

router = APIRouter()


@router.get("/subscription")
def get_subscription(user=Depends(get_current_user)):
    if user["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Forbidden")
    data = get_subscription_for_business(user["business_id"])
    if data is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return data


@router.post("/subscription/subscribe")
def subscribe(req: SubscribeRequest, user=Depends(get_current_user)):
    if user["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        data = set_subscription_for_business(user["business_id"], req.plan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan")
    if data is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return data
