from fastapi import APIRouter, Depends, HTTPException
from app.modules.invites.schemas import InviteCreateRequest
from app.modules.invites.service import create_invite, list_invites, validate_invite, accept_invite
from app.core.security import get_current_user

router = APIRouter(prefix="/invites", tags=["Invites"])

# Отримання списку інвайтів для власника бізнесу
@router.get("/")
def get_invites(current_user=Depends(get_current_user)):
    if current_user["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Forbidden")
    return list_invites(current_user["business_id"])


# Створення нового інвайту
@router.post("/")
async def create_invite_endpoint(data: InviteCreateRequest, current_user=Depends(get_current_user)):
    if current_user["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Forbidden")
    invite = await create_invite(data.email, data.role, current_user["business_id"])
    return {"success": True, "token": invite["token"]}


# Валідація токена інвайту
@router.get("/validate/{token}")
def validate_invite_endpoint(token: str):
    invite = validate_invite(token)
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invite")
    return {"email": invite["email"], "role": invite["role"]}


# Прийняття інвайту: зміна тимчасового пароля на новий
@router.post("/accept/{token}")
def accept_invite_endpoint(token: str, data: dict):
    if "password" not in data or not data["password"]:
        raise HTTPException(status_code=400, detail="Password is required")
    invite = accept_invite(token, data["password"])
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or already accepted invite")
    return {"success": True, "email": invite["email"], "role": invite["role"]}