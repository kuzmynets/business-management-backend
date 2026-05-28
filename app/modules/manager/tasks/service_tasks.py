from datetime import datetime
from app.firebase import db

STATUSES = ["NEW", "IN_PROGRESS", "DONE"]

def get_tasks(business_id: str):

    docs = (
        db.collection("tasks")
        .where("business_id", "==", business_id)
        .stream()
    )

    result = []

    for t in docs:
        task = t.to_dict()

        result.append({
            "id": t.id,
            "title": task.get("title"),
            "description": task.get("description", ""),
            "status": task.get("status", "NEW"),
            "assigned_to": task.get("assigned_to"),
            "order_id": task.get("order_id"),
            "order_title": task.get("order_title"),
            "deadline": task.get("deadline")
        })

    return result


def get_task_by_id(task_id: str, business_id: str):

    ref = db.collection("tasks").document(task_id)
    doc = ref.get()

    if not doc.exists:
        return None

    t = doc.to_dict()
    if t.get("business_id") != business_id:
        return None

    return {
        "id": doc.id,
        "title": t.get("title"),
        "description": t.get("description", ""),
        "status": t.get("status", "NEW"),
        "assigned_to": t.get("assigned_to"),
        "order_id": t.get("order_id"),
        "order_title": t.get("order_title"),
        "deadline": t.get("deadline")
    }


def create_task(business_id: str, data, user=None):

    order_title = None
    deadline = None

    if data.order_id:
        order_doc = db.collection("orders").document(data.order_id).get()

        if not order_doc.exists:
            return None

        order = order_doc.to_dict()
        order_title = order.get("title")
        deadline = order.get("deadline")

    task_data = {
        "title": data.title,
        "description": data.description or "",
        "order_id": data.order_id,
        "order_title": order_title,
        "assigned_to": data.assigned_to,
        "status": "NEW",
        "deadline": deadline,
        "business_id": business_id,
        "created_by": user["uid"] if user else None,
        "assigned_by": user["uid"] if user else None,
        "created_at": datetime.utcnow()
    }

    ref = db.collection("tasks").add(task_data)

    return {
        "id": ref[1].id,
        **task_data
    }


def update_task(task_id: str, business_id: str, data: dict):

    ref = db.collection("tasks").document(task_id)
    doc = ref.get()

    if not doc.exists:
        return None

    if doc.to_dict().get("business_id") != business_id:
        return None

    update_data = {}

    allowed_fields = [
        "title",
        "description",
        "status",
        "assigned_to"
    ]

    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]

    update_data["updated_at"] = datetime.utcnow()

    ref.update(update_data)

    return {
        "id": task_id,
        **update_data
    }
