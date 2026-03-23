from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.modules.manager.service_dashboard import (
    get_active_orders,
    get_overdue_orders,
    get_team_tasks,
    get_overdue_tasks,
    get_problem_orders
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/active-orders")
def active_orders(current_user: dict = Depends(get_current_user)):
    return get_active_orders(current_user["business_id"])

@router.get("/overdue-orders")
def overdue_orders(current_user: dict = Depends(get_current_user)):
    return get_overdue_orders(current_user["business_id"])

@router.get("/team-tasks")
def team_tasks(current_user: dict = Depends(get_current_user)):
    return get_team_tasks(current_user["business_id"])

@router.get("/overdue-tasks")
def overdue_tasks(current_user: dict = Depends(get_current_user)):
    return get_overdue_tasks(current_user["business_id"])

@router.get("/problem-orders")
def problem_orders(current_user: dict = Depends(get_current_user)):
    return get_problem_orders(current_user["business_id"])