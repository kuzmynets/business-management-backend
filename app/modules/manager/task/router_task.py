from fastapi import APIRouter, Depends, HTTPException, Body
from app.modules.manager.task.service_task import get_my_tasks, update_task_status
from app.core.security import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/my")
def my_tasks(current_user: dict = Depends(get_current_user)):
    return get_my_tasks(current_user["uid"])

@router.patch("/{task_id}/status")
def change_status(
    task_id: str,
    data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return update_task_status(
            task_id=task_id,
            user_uid=current_user["uid"],
            status=data["status"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
