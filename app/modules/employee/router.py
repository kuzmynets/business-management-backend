from fastapi import APIRouter, Depends, Body
from app.modules.employee.service import get_my_tasks, update_task_status
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
    return update_task_status(
        task_id=task_id,
        user_uid=current_user["uid"],
        status=data["status"]
    )
