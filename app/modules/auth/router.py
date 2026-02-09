from fastapi import APIRouter, HTTPException, Header
from app.modules.auth.schemas import RegisterRequest
from app.modules.auth.service import register_owner
from app.firebase import firebase_auth, db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register-owner")
def register_owner_endpoint(data: RegisterRequest):
    try:
        uid, business_id = register_owner(
            data.email, data.password, data.business_name
        )
        return {"success": True, "uid": uid, "business_id": business_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
def me(Authorization: str = Header(...)):
    try:
        token = Authorization.replace("Bearer ", "")
        decoded = firebase_auth.verify_id_token(token)
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_doc = db.collection("users").document(decoded["uid"]).get()
    if not user_doc.exists:
        raise HTTPException(status_code=403, detail="User not found")

    user = user_doc.to_dict()
    return {
        "email": user["email"],
        "role": user["role"],
        "business_id": user["business_id"]
    }
