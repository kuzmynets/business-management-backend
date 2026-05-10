from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.modules.manager.dashboard.dashboard_service import get_manager_dashboard

router = APIRouter(prefix="/manager", tags=["manager"])


@router.get("/dashboard")
def manager_dashboard(user=Depends(get_current_user)):
    return get_manager_dashboard(user["business_id"])