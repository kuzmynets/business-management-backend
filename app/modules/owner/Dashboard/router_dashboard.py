from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user

from app.modules.owner.Dashboard.service_dashboard import (
    get_recent_activities,
    get_owner_dashboard_stats,
    get_owner_work_overview
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard_stats(user=Depends(get_current_user)):
    if user["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Forbidden")

    business_id = user["business_id"]

    stats = get_owner_dashboard_stats(business_id, user["uid"])

    recent_activities = get_recent_activities(business_id)
    work = get_owner_work_overview(business_id)

    return {
        "revenue": stats["total_revenue"],
        "total_revenue": stats["total_revenue"],
        "profit": stats["profit"],
        "active_orders": stats["active_orders"],
        "team_members": stats["team_members"],
        "businesses_count": stats["businesses_count"],
        "recent_activities": recent_activities,
        "orders": work["orders"],
        "tasks": work["tasks"]
    }
