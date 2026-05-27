from fastapi import APIRouter, Depends, HTTPException
from app.modules.auth.schemas import RegisterRequest
from app.modules.auth.service import register_owner
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register_owner_endpoint(data: RegisterRequest):
    try:
        uid, business_id = register_owner(
            data.email, data.password, data.business_name
        )
        return {
            "success": True,
            "uid": uid,
            "email": data.email,
            "role": "OWNER",
            "business_id": business_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {
        "email": user["email"],
        "role": user["role"],
        "business_id": user["business_id"]
    }
