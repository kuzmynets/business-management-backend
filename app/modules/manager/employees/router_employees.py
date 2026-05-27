from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user
from app.modules.manager.employees.employees_service import get_employees

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("")
def list_employees(user=Depends(get_current_user)):
    if user["role"] not in ["OWNER", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return get_employees(user["business_id"])
