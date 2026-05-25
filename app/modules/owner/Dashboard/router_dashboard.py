from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user

from app.modules.owner.Dashboard.service_dashboard import (
    get_orders_for_business,
    get_recent_activities,
    calculate_revenue_and_profit
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard_stats(user=Depends(get_current_user)):

    business_id = user["business_id"]

    orders = get_orders_for_business(business_id)

    revenue, profit = calculate_revenue_and_profit(business_id)

    recent_activities = get_recent_activities(business_id)

    return {
        "revenue": revenue,
        "profit": profit,
        "recent_activities": recent_activities
    }