from datetime import datetime
from app.firebase import db


def get_business(business_id: str):

    doc = db.collection("businesses").document(business_id).get()

    if not doc.exists:
        return None

    business = doc.to_dict()

    return {
        "id": doc.id,
        "name": business.get("name"),
        "logo_url": business.get("logo_url"),
        "currency": business.get("currency", "USD"),
        "timezone": business.get("timezone", "UTC"),
        "subscription": business.get("subscription", "FREE"),
        "is_active": business.get("is_active", True),
        "created_at": business.get("created_at")
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
        "currency",
        "timezone"
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
        "currency": updated.get("currency", "USD"),
        "timezone": updated.get("timezone", "UTC"),
        "subscription": updated.get("subscription", "FREE"),
        "is_active": updated.get("is_active", True),
        "created_at": updated.get("created_at")
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