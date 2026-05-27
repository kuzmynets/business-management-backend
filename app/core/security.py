from fastapi import Header, HTTPException
from app.firebase import firebase_auth, db


def _get_business_member(business_id: str, uid: str):
    docs = (
        db.collection("business_members")
        .where("business_id", "==", business_id)
        .where("user_id", "==", uid)
        .limit(1)
        .stream()
    )

    for doc in docs:
        member = doc.to_dict()
        member["id"] = doc.id
        return member

    return None


def _pick_default_business(uid: str, user_data: dict):
    fallback_business_id = user_data.get("business_id")
    if fallback_business_id:
        return fallback_business_id

    owned = (
        db.collection("businesses")
        .where("owner_id", "==", uid)
        .limit(1)
        .stream()
    )
    for doc in owned:
        return doc.id

    memberships = (
        db.collection("business_members")
        .where("user_id", "==", uid)
        .where("status", "==", "active")
        .limit(1)
        .stream()
    )
    for doc in memberships:
        return doc.to_dict().get("business_id")

    return None


def get_current_user(
    Authorization: str = Header(...),
    x_business_id: str | None = Header(default=None, alias="X-Business-Id")
):
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

    requested_business_id = x_business_id or _pick_default_business(decoded["uid"], user_data)

    if requested_business_id:
        business_doc = (
            db.collection("businesses")
            .document(requested_business_id)
            .get()
        )

        if not business_doc.exists:
            raise HTTPException(status_code=404, detail="Business not found")

        business = business_doc.to_dict()
        member = _get_business_member(requested_business_id, decoded["uid"])
        is_owner = business.get("owner_id") == decoded["uid"]
        has_active_membership = member and member.get("status") == "active"

        if not is_owner and not has_active_membership:
            raise HTTPException(status_code=403, detail="Business access denied")

        user_data["business_id"] = requested_business_id
        user_data["role"] = "OWNER" if is_owner else member.get("role")
        user_data["member_status"] = "active" if is_owner else member.get("status")
    else:
        user_data["role"] = user_data.get("role")

    return user_data
