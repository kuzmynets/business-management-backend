from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user
from app.modules.employee.service_employee_tasks import (
    get_my_tasks,
    get_my_manager,
    update_task_status,
    update_task_result
)

# FIX: separate namespace to avoid collision with manager /tasks
router = APIRouter(prefix="/employee/tasks", tags=["employee-tasks"])


class StatusRequest(BaseModel):
    status: str


class ResultRequest(BaseModel):
    result_note: str | None = None


@router.get("/my")
def my_tasks(user=Depends(get_current_user)):
    if user["role"] != "EMPLOYEE":
        raise HTTPException(403, "Forbidden")
    return get_my_tasks(
        business_id=user["business_id"],
        user_id=user["uid"]
    )


@router.get("/manager")
def my_manager(user=Depends(get_current_user)):
    if user["role"] != "EMPLOYEE":
        raise HTTPException(403, "Forbidden")
    manager = get_my_manager(user["business_id"])
    if not manager:
        return None
    return manager


@router.patch("/{task_id}/status")
def change_status(task_id: str, data: StatusRequest, user=Depends(get_current_user)):
    if user["role"] != "EMPLOYEE":
        raise HTTPException(403, "Forbidden")

    updated = update_task_status(
        task_id=task_id,
        business_id=user["business_id"],
        user_id=user["uid"],
        status=data.status
    )

    if not updated:
        raise HTTPException(404, "Task not found or not allowed")

    return updated


@router.patch("/{task_id}")
def save_result(task_id: str, data: ResultRequest, user=Depends(get_current_user)):
    if user["role"] != "EMPLOYEE":
        raise HTTPException(403, "Forbidden")

    updated = update_task_result(
        task_id=task_id,
        business_id=user["business_id"],
        user_id=user["uid"],
        result_note=data.result_note
    )

    if not updated:
        raise HTTPException(404, "Task not found or not allowed")

    return updated
