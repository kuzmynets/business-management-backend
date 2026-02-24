from app.firebase import db
from datetime import datetime, timezone

ALLOWED_STATUSES = ["pending", "in_progress", "done"]


def serialize_task(doc):
    data = doc.to_dict()
    data["id"] = doc.id

    if data.get("deadline"):
        deadline = data["deadline"]
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        data["deadline"] = deadline.isoformat()

    return data


def get_my_tasks(user_uid: str):
    query = db.collection("tasks").where("assigned_to", "==", user_uid)
    return [serialize_task(doc) for doc in query.stream()]


def update_task_status(task_id: str, user_uid: str, status: str):
    if status not in ALLOWED_STATUSES:
        raise ValueError("Invalid status")

    task_ref = db.collection("tasks").document(task_id)
    doc = task_ref.get()

    if not doc.exists:
        raise ValueError("Task not found")

    task = doc.to_dict()

    if task["assigned_to"] != user_uid:
        raise ValueError("Forbidden")

    task_ref.update({
        "status": status,
        "updated_at": datetime.now(timezone.utc)
    })

    return {"success": True}
