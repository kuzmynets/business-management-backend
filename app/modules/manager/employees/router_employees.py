from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.modules.manager.employees.employees_service import get_employees

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("")
def list_employees(user=Depends(get_current_user)):
    return get_employees(user["business_id"])