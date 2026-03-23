from app.firebase import db
from datetime import datetime, timezone

def serialize_business(doc):
    data = doc.to_dict()
    data["id"] = doc.id
    if data.get("created_at") and hasattr(data["created_at"], "isoformat"):
        data["created_at"] = data["created_at"].isoformat()
    return data

def get_business_by_id(business_id: str):
    doc_ref = db.collection("businesses").document(business_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    return serialize_business(doc)

def update_business(business_id: str, name: str = None, subscription: str = None):
    doc_ref = db.collection("businesses").document(business_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise ValueError("Business not found")

    update_data = {}
    if name is not None:
        update_data["name"] = name
    if subscription is not None:
        update_data["subscription"] = subscription
    update_data["updated_at"] = datetime.now(timezone.utc)

    if update_data:
        doc_ref.update(update_data)

    return {"success": True}

def deactivate_business(business_id: str):
    doc_ref = db.collection("businesses").document(business_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise ValueError("Business not found")
    doc_ref.update({
        "active": False,
        "deactivated_at": datetime.now(timezone.utc)
    })
    return {"success": True}