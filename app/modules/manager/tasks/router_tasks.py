from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.security import get_current_user
from app.modules.manager.tasks.service_tasks import (
    get_tasks,
    create_task,
    get_task_by_id,
    update_task,
    delete_task
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
    if user["role"] not in ["OWNER", "MANAGER"]:
        raise HTTPException(403, "Forbidden")
    return get_tasks(user["business_id"])


@router.get("/{task_id}")
def get_task(task_id: str, user=Depends(get_current_user)):
    if user["role"] not in ["OWNER", "MANAGER"]:
        raise HTTPException(403, "Forbidden")
    task = get_task_by_id(task_id, user["business_id"])

    if not task:
        raise HTTPException(404, "Task not found")

    return task


@router.post("")
def create_task_endpoint(data: CreateTaskRequest, user=Depends(get_current_user)):
    if user["role"] not in ["OWNER", "MANAGER"]:
        raise HTTPException(403, "Forbidden")
    task = create_task(user["business_id"], data, user)

    if not task:
        raise HTTPException(404, "Order not found")

    return task


@router.patch("/{task_id}")
def update_task_endpoint(task_id: str, data: UpdateTaskRequest, user=Depends(get_current_user)):
    if user["role"] not in ["OWNER", "MANAGER"]:
        raise HTTPException(403, "Forbidden")
    result = update_task(task_id, user["business_id"], data.dict(exclude_none=True))

    if not result:
        raise HTTPException(404, "Task not found")

    return result

@router.delete("/{task_id}")
def remove_task(
    task_id: str,
    user=Depends(get_current_user)
):

    deleted = delete_task(
        task_id,
        user["business_id"]
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {
        "success": True,
        "message": "Task deleted"
    }