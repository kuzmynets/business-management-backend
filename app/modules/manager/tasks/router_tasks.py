from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.security import get_current_user
from app.modules.manager.tasks.service_tasks import (
    get_tasks,
    create_task,
    get_task_by_id,
    update_task
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    title: str
    order_id: str | None = None
    assigned_to: str | None = None
    priority: str | None = None
    description: str | None = None


class UpdateTaskRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    assigned_to: str | None = None
    priority: str | None = None


@router.get("")
def list_tasks(user=Depends(get_current_user)):
    return get_tasks(user["business_id"])


@router.get("/{task_id}")
def get_task(task_id: str, user=Depends(get_current_user)):
    task = get_task_by_id(task_id)

    if not task:
        raise HTTPException(404, "Task not found")

    return task


@router.post("")
def create_task_endpoint(data: CreateTaskRequest, user=Depends(get_current_user)):
    task = create_task(user["business_id"], data)

    if not task:
        raise HTTPException(404, "Order not found")

    return task


@router.patch("/{task_id}")
def update_task_endpoint(task_id: str, data: UpdateTaskRequest):
    result = update_task(task_id, data.dict(exclude_none=True))

    if not result:
        raise HTTPException(404, "Task not found")

    return result