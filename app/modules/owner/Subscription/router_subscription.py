from fastapi import APIRouter, HTTPException
from app.modules.owner.Subscription.subscription_service import (
    get_subscription_for_business,
    set_subscription_for_business
)
from app.modules.owner.Subscription.subscription_models import SubscribeRequest

router = APIRouter()


@router.get("/subscription")
def get_subscription(business_id: str):
    data = get_subscription_for_business(business_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return data


@router.post("/subscription/subscribe")
def subscribe(req: SubscribeRequest):
    try:
        data = set_subscription_for_business(req.business_id, req.plan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan")
    if data is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return data