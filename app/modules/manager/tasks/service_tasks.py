from app.firebase import db
from datetime import datetime, timezone

ALLOWED_STATUSES = ["NEW", "IN_PROGRESS", "COMPLETED", "CANCELLED"]


def serialize_task(doc):
    data = doc.to_dict()
    data["id"] = doc.id

    # deadline
    if data.get("deadline"):
        deadline = data["deadline"]
        if hasattr(deadline, "tzinfo") and deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        data["deadline"] = deadline.isoformat()[:10]

    # order title
    if data.get("order_id"):
        order_doc = db.collection("orders").document(data["order_id"]).get()
        if order_doc.exists:
            data["order_title"] = order_doc.to_dict().get("title")

    # employee email
    if data.get("assigned_to"):
        user_doc = db.collection("users").document(data["assigned_to"]).get()
        if user_doc.exists:
            data["assigned_email"] = user_doc.to_dict().get("email")

    return data


def get_tasks(business_id: str, filters: dict):
    query = db.collection("tasks").where("business_id", "==", business_id)

    if filters.get("status"):
        query = query.where("status", "==", filters["status"])

    if filters.get("order_id"):
        query = query.where("order_id", "==", filters["order_id"])

    if filters.get("assigned_to"):
        query = query.where("assigned_to", "==", filters["assigned_to"])

    return [serialize_task(doc) for doc in query.stream()]


def create_task(data: dict, business_id: str):
    if not data.get("title"):
        raise ValueError("Title required")

    task_ref = db.collection("tasks").document()
    task_ref.set({
        "title": data["title"],
        "description": data.get("description", ""),
        "order_id": data.get("order_id"),
        "assigned_to": data.get("assigned_to"),
        "status": data.get("status", "NEW"),
        "deadline": datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
        "business_id": business_id,
        "created_at": datetime.now(timezone.utc)
    })

    return {"id": task_ref.id}


def update_task(task_id: str, data: dict, business_id: str):
    task_ref = db.collection("tasks").document(task_id)
    doc = task_ref.get()

    if not doc.exists:
        raise ValueError("Task not found")

    if doc.to_dict()["business_id"] != business_id:
        raise ValueError("Forbidden")

    update_data = {
        "title": data.get("title"),
        "description": data.get("description"),
        "order_id": data.get("order_id"),
        "assigned_to": data.get("assigned_to"),
        "status": data.get("status"),
    }

    if data.get("deadline"):
        update_data["deadline"] = datetime.fromisoformat(data["deadline"])

    task_ref.update(update_data)

    return {"success": True}


def update_task_status(task_id: str, status: str, business_id: str):
    if status not in ALLOWED_STATUSES:
        raise ValueError("Invalid status")

    task_ref = db.collection("tasks").document(task_id)
    doc = task_ref.get()

    if not doc.exists:
        raise ValueError("Task not found")

    if doc.to_dict()["business_id"] != business_id:
        raise ValueError("Forbidden")

    task_ref.update({
        "status": status,
        "updated_at": datetime.now(timezone.utc)
    })

    return {"success": True}