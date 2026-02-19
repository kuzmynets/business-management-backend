from app.firebase import db
from datetime import datetime, timezone

ALLOWED_STATUSES = ["pending", "in_progress", "done"]

def get_my_tasks(user_uid: str):
    tasks_ref = db.collection("tasks").where("assigned_to", "==", user_uid)

    tasks = []
    for doc in tasks_ref.stream():
        data = doc.to_dict()
        data["id"] = doc.id

        # перетворення deadline у ISO
        if data.get("deadline"):
            deadline = data["deadline"]
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            data["deadline"] = deadline.isoformat()

        tasks.append(data)

    return tasks


def update_task_status(task_id: str, user_uid: str, status: str):
    if status not in ALLOWED_STATUSES:
        raise ValueError("Invalid status")

    task_ref = db.collection("tasks").document(task_id)
    task_doc = task_ref.get()

    if not task_doc.exists:
        raise ValueError("Task not found")

    task = task_doc.to_dict()

    if task["assigned_to"] != user_uid:
        raise ValueError("Not allowed")

    task_ref.update({
        "status": status,
        "updated_at": datetime.now(timezone.utc)
    })

    return {"success": True}
