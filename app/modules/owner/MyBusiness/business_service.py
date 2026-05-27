from datetime import datetime
from app.firebase import db


def _serialize_business(doc, role: str):
    business = doc.to_dict()
    return {
        "id": doc.id,
        "name": business.get("name"),
        "logo_url": business.get("logo_url"),
        "subscription": business.get("subscription", "BASIC"),
        "is_active": business.get("is_active", True),
        "created_at": business.get("created_at"),
        "role": role
    }


def list_businesses(user_id: str):
    owned_docs = (
        db.collection("businesses")
        .where("owner_id", "==", user_id)
        .stream()
    )

    businesses = []
    seen = set()

    for doc in owned_docs:
        businesses.append(_serialize_business(doc, "OWNER"))
        seen.add(doc.id)

    member_docs = (
        db.collection("business_members")
        .where("user_id", "==", user_id)
        .where("status", "==", "active")
        .stream()
    )

    for member_doc in member_docs:
        member = member_doc.to_dict()
        business_id = member.get("business_id")
        if not business_id or business_id in seen:
            continue

        business_doc = db.collection("businesses").document(business_id).get()
        if business_doc.exists:
            businesses.append(_serialize_business(business_doc, member.get("role", "EMPLOYEE")))
            seen.add(business_id)

    businesses.sort(key=lambda x: x.get("created_at") or datetime.min)
    return businesses


def create_business(owner_id: str, name: str):
    ref = db.collection("businesses").document()

    data = {
        "name": name,
        "owner_id": owner_id,
        "subscription": "BASIC",
        "status": "active",
        "is_active": True,
        "created_at": datetime.utcnow()
    }

    ref.set(data)

    db.collection("business_members").add({
        "business_id": ref.id,
        "user_id": owner_id,
        "role": "OWNER",
        "status": "active",
        "joined_at": datetime.utcnow(),
        "created_at": datetime.utcnow()
    })

    return {
        "id": ref.id,
        **data
    }


def get_business(business_id: str):

    doc = db.collection("businesses").document(business_id).get()

    if not doc.exists:
        return None

    business = doc.to_dict()

    return {
        "id": doc.id,
        "name": business.get("name"),
        "logo_url": business.get("logo_url"),
        "subscription": business.get("subscription", "FREE"),
        "is_active": business.get("is_active", True),
        "created_at": business.get("created_at"),
        "owner_id": business.get("owner_id")
    }


def update_business(business_id: str, data: dict):

    ref = db.collection("businesses").document(business_id)

    doc = ref.get()

    if not doc.exists:
        return None

    update_data = {}

    for field in [
        "name",
        "logo_url",
    ]:
        if field in data:
            update_data[field] = data[field]

    update_data["updated_at"] = datetime.utcnow()

    ref.update(update_data)

    updated = ref.get().to_dict()

    return {
        "id": business_id,
        "name": updated.get("name"),
        "logo_url": updated.get("logo_url"),
        "subscription": updated.get("subscription", "FREE"),
        "is_active": updated.get("is_active", True),
        "created_at": updated.get("created_at"),
        "owner_id": updated.get("owner_id")
    }


def deactivate_business(business_id: str):

    ref = db.collection("businesses").document(business_id)

    if not ref.get().exists:
        return None

    ref.update({
        "is_active": False,
        "updated_at": datetime.utcnow()
    })

    return {
        "success": True
    }


def delete_business(business_id: str):

    ref = db.collection("businesses").document(business_id)

    if not ref.get().exists:
        return None

    ref.delete()

    return {
        "success": True
    }
