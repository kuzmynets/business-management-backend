from fastapi import Header, HTTPException
from app.firebase import firebase_auth, db

def get_current_user(Authorization: str = Header(...)):
    try:
        token = Authorization.replace("Bearer ", "")
        decoded = firebase_auth.verify_id_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_doc = db.collection("users").document(decoded["uid"]).get()
    if not user_doc.exists:
        raise HTTPException(status_code=403, detail="User not found")

    user_data = user_doc.to_dict()
    user_data["uid"] = decoded["uid"]

    return user_data