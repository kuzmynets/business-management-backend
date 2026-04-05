from app.firebase import db
from datetime import datetime, timezone

ALLOWED_STATUSES = ["NEW", "IN_PROGRESS", "COMPLETED", "CANCELLED"]


def serialize_order(doc):
    data = doc.to_dict()
    data["id"] = doc.id

    if data.get("deadline"):
        deadline = data["deadline"]
        if hasattr(deadline, "tzinfo") and deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        data["deadline"] = deadline.isoformat()[:10]

    return data


def get_orders(business_id: str, status: str | None = None):
    query = db.collection("orders").where("business_id", "==", business_id)

    if status:
        query = query.where("status", "==", status)

    return [serialize_order(doc) for doc in query.stream()]


def create_order(data: dict, business_id: str):
    if not data.get("title"):
        raise ValueError("Title required")

    order_ref = db.collection("orders").document()

    order_ref.set({
        "title": data["title"],
        "description": data.get("description", ""),
        "client_name": data.get("client_name", ""),
        "status": data.get("status", "NEW"),
        "deadline": datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
        "business_id": business_id,
        "created_at": datetime.now(timezone.utc)
    })

    return {"id": order_ref.id}


def update_order(order_id: str, data: dict, business_id: str):
    order_ref = db.collection("orders").document(order_id)
    doc = order_ref.get()

    if not doc.exists:
        raise ValueError("Order not found")

    if doc.to_dict()["business_id"] != business_id:
        raise ValueError("Forbidden")

    update_data = {
        "title": data.get("title"),
        "description": data.get("description"),
        "client_name": data.get("client_name"),
        "status": data.get("status")
    }

    if data.get("deadline"):
        update_data["deadline"] = datetime.fromisoformat(data["deadline"])
    else:
        update_data["deadline"] = None

    order_ref.update(update_data)

    return {"success": True}


def update_order_status(order_id: str, status: str, business_id: str):
    if status not in ALLOWED_STATUSES:
        raise ValueError("Invalid status")

    order_ref = db.collection("orders").document(order_id)
    doc = order_ref.get()

    if not doc.exists:
        raise ValueError("Order not found")

    if doc.to_dict()["business_id"] != business_id:
        raise ValueError("Forbidden")

    order_ref.update({
        "status": status,
        "updated_at": datetime.now(timezone.utc)
    })

    return {"success": True}