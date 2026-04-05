from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.modules.manager.tasks.service_tasks import (
    get_tasks,
    update_task_status,
    assign_task
)
from app.core.security import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


class UpdateStatusRequest(BaseModel):
    status: str


class AssignTaskRequest(BaseModel):
    assigned_to: str | None = None


@router.get("")
def list_tasks(current_user: dict = Depends(get_current_user)):
    return get_tasks(current_user["business_id"])


@router.patch("/{task_id}/status")
def change_status(task_id: str, data: UpdateStatusRequest):
    task = update_task_status(task_id, data.status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/assign")
def change_assignee(task_id: str, data: AssignTaskRequest):
    task = assign_task(task_id, data.assigned_to)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task