from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.security import get_current_user
from app.modules.manager.projects.service_projects import (
    get_my_projects,
    create_project,
    get_project_by_id,
    get_all_projects
)
from app.modules.manager.clients.employees_service import list_employees

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

# --- EMPLOYEES ---
@employees_router.get("")
def employees(current_user: dict = Depends(get_current_user)):
    return [emp for emp in list_employees() if emp.get("role") == "EMPLOYEE"]