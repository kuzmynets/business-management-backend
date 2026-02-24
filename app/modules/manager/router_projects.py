from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.security import get_current_user
from app.modules.manager.service_projects import (
    get_my_projects,
    create_project,
    get_tasks_by_project,
    get_project_by_id,
    get_all_projects,
    create_task_service
)
from app.modules.manager.employees_service import list_employees
from app.firebase import db
from datetime import datetime, timezone
import uuid

projects_router = APIRouter(prefix="/projects", tags=["projects"])
employees_router = APIRouter(prefix="/employees", tags=["employees"])
tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])

# --- PROJECTS ---
@projects_router.get("")
def my_projects(current_user: dict = Depends(get_current_user)):
    return get_my_projects(current_user["uid"])

@projects_router.get("/")
def list_projects(current_user: dict = Depends(get_current_user)):
    return get_all_projects(current_user["business_id"])

@projects_router.post("")
def new_project(
    data: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    try:
        return create_project(
            title=data["title"],
            manager_uid=current_user["uid"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@projects_router.get("/{project_id}")
def project_details(project_id: str, current_user: dict = Depends(get_current_user)):
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@projects_router.get("/{project_id}/tasks")
def project_tasks(project_id: str, current_user: dict = Depends(get_current_user)):
    return get_tasks_by_project(project_id)

# --- EMPLOYEES ---
@employees_router.get("")
def employees(current_user: dict = Depends(get_current_user)):
    return [emp for emp in list_employees() if emp.get("role") == "EMPLOYEE"]

# --- TASKS ---
@tasks_router.post("")
def create_task(data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    try:
        task = create_task_service(
            title=data["title"],
            description=data.get("description", ""),
            project_id=data["project_id"],
            assigned_to=data["assigned_to"]
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))