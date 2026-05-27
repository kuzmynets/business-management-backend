from fastapi import APIRouter, Depends, HTTPException
from app.modules.invites.schemas import InviteCreateRequest
from app.modules.invites.service import (
    approve_invite,
    create_invite,
    decline_invite,
    list_invites,
    list_members,
    reject_invite,
    reject_member_removal,
    remove_member,
    validate_invite,
    accept_invite
)
from app.core.security import get_current_user

router = APIRouter(prefix="/invites", tags=["Invites"])

# Отримання списку інвайтів для власника бізнесу
@router.get("/")
def get_invites(current_user=Depends(get_current_user)):
    if current_user["role"] not in ["OWNER", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return list_invites(current_user["business_id"])


@router.get("/members")
def get_members(current_user=Depends(get_current_user)):
    if current_user["role"] not in ["OWNER", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return list_members(current_user["business_id"])


# Створення нового інвайту
@router.post("/")
async def create_invite_endpoint(data: InviteCreateRequest, current_user=Depends(get_current_user)):
    if current_user["role"] not in ["OWNER", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    if current_user["role"] == "MANAGER" and data.role != "EMPLOYEE":
        raise HTTPException(status_code=403, detail="Manager can invite only employees")
    try:
        invite = await create_invite(
            data.email,
            data.role,
            current_user["business_id"],
            current_user["role"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "token": invite["token"]}


@router.post("/{token}/approve")
def approve_invite_endpoint(token: str, current_user=Depends(get_current_user)):
    if current_user["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Forbidden")
    result = approve_invite(token, current_user["business_id"])
    if not result:
        raise HTTPException(status_code=404, detail="Invite not found")
    return result


@router.post("/{token}/reject")
def reject_invite_endpoint(token: str, current_user=Depends(get_current_user)):
    if current_user["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Forbidden")
    result = reject_invite(token, current_user["business_id"])
    if not result:
        raise HTTPException(status_code=404, detail="Invite not found")
    return result


@router.delete("/members/{member_id}")
def remove_member_endpoint(member_id: str, current_user=Depends(get_current_user)):
    if current_user["role"] not in ["OWNER", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    result = remove_member(member_id, current_user["business_id"], current_user["role"])
    if not result:
        raise HTTPException(status_code=404, detail="Member not found")
    return result


@router.post("/members/{member_id}/reject-removal")
def reject_member_removal_endpoint(member_id: str, current_user=Depends(get_current_user)):
    if current_user["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Forbidden")
    result = reject_member_removal(member_id, current_user["business_id"])
    if not result:
        raise HTTPException(status_code=404, detail="Removal request not found")
    return result


# Валідація токена інвайту
@router.get("/validate/{token}")
def validate_invite_endpoint(token: str):
    invite = validate_invite(token)
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invite")
    return {
        "email": invite["email"],
        "role": invite["role"],
        "existing_user": invite.get("existing_user", False)
    }


# Прийняття інвайту: зміна тимчасового пароля на новий
@router.post("/accept/{token}")
def accept_invite_endpoint(token: str, data: dict):
    try:
        invite = accept_invite(token, data.get("password"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or already accepted invite")
    return {"success": True, "email": invite["email"], "role": invite["role"]}


@router.post("/decline/{token}")
def decline_invite_endpoint(token: str):
    result = decline_invite(token)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid or already processed invite")
    return result
