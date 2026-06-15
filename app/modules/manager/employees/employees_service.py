from app.firebase import db


def get_employees(business_id: str):

    docs = (
        db.collection("business_members")
        .where("business_id", "==", business_id)
        .where("role", "==", "EMPLOYEE")
        .stream()
    )

    result = []
    user_cache = {}

    for d in docs:
        member = d.to_dict()
        if member.get("status") != "active":
            continue

        user_id = member.get("user_id")
        if user_id and user_id not in user_cache:
            user_doc = db.collection("users").document(user_id).get()
            user_cache[user_id] = user_doc.to_dict() if user_doc.exists else {}
        user = user_cache.get(user_id, {})

        result.append({
            "id": user_id,
            "member_id": d.id,
            "email": member.get("email") or user.get("email"),
            "name": member.get("name") or user.get("full_name") or user.get("name"),
            "role": member.get("role"),
            "status": member.get("status")
        })

    return result
