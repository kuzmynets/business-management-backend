from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.modules.owner.Analytic.analytics_service import get_analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("")
def analytics(user=Depends(get_current_user)):

    if user["role"] not in ["OWNER", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    return get_analytics(user["business_id"])