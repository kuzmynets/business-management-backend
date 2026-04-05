from fastapi import APIRouter, Depends, HTTPException, Body, Query
from app.core.security import get_current_user
from app.modules.manager.tasks.service_tasks import (
    get_tasks,
    create_task,
    update_task,
    update_task_status
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("")
def list_tasks(
    status: str | None = Query(None),
    order_id: str | None = Query(None),
    assigned_to: str | None = Query(None),
    current_user: dict = Depends(get_current_user)
):
    filters = {
        "status": status,
        "order_id": order_id,
        "assigned_to": assigned_to
    }
    return get_tasks(current_user["business_id"], filters)


@router.post("")
def new_task(
    data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return create_task(data, current_user["business_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{task_id}")
def edit_task(
    task_id: str,
    data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return update_task(task_id, data, current_user["business_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{task_id}/status")
def change_status(
    task_id: str,
    data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return update_task_status(
            task_id,
            data["status"],
            current_user["business_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))