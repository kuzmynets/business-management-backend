from app.firebase import db, firebase_auth
from datetime import datetime

def register_owner(email: str, password: str, business_name: str):
    user = firebase_auth.create_user(email=email, password=password)

    business_ref = db.collection("businesses").document()
    business_ref.set({
        "name": business_name,
        "owner_id": user.uid,
        "subscription": "BASIC",
        "status": "active",
        "created_at": datetime.utcnow()
    })

    db.collection("users").document(user.uid).set({
        "email": email,
        "role": "OWNER",
        "business_id": business_ref.id,
        "status": "active",
        "created_at": datetime.utcnow()
    })

    return user.uid, business_ref.id
