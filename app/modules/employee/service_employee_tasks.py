from datetime import datetime
from app.firebase import db

STATUSES = ["TODO", "IN_PROGRESS", "PAUSED", "DONE"]


def get_my_tasks(business_id: str, user_id: str):

    docs = (
        db.collection("tasks")
        .where("business_id", "==", business_id)
        .where("assigned_to", "==", user_id)
        .stream()
    )

    result = []

    for t in docs:
        task = t.to_dict()

        result.append({
            "id": t.id,
            "title": task.get("title"),
            "description": task.get("description", ""),
            "status": task.get("status", "TODO"),
            "priority": task.get("priority", "MEDIUM"),
            "order_title": task.get("order_title"),
            "deadline": task.get("deadline"),
            "result_note": task.get("result_note", "")
        })

    return result


def update_task_status(task_id: str, business_id: str, user_id: str, status: str):

    if status not in STATUSES:
        return None

    ref = db.collection("tasks").document(task_id)
    doc = ref.get()

    if not doc.exists:
        return None

    task = doc.to_dict()

    if task.get("business_id") != business_id or task.get("assigned_to") != user_id:
        return None

    ref.update({
        "status": status,
        "updated_at": datetime.utcnow()
    })

    return {"id": task_id, "status": status}


def update_task_result(task_id: str, business_id: str, user_id: str, result_note: str):

    ref = db.collection("tasks").document(task_id)
    doc = ref.get()

    if not doc.exists:
        return None

    task = doc.to_dict()

    if task.get("business_id") != business_id or task.get("assigned_to") != user_id:
        return None

    ref.update({
        "result_note": result_note,
        "updated_at": datetime.utcnow()
    })

    return {"id": task_id, "result_note": result_note}


def get_my_manager(business_id: str):
    docs = (
        db.collection("business_members")
        .where("business_id", "==", business_id)
        .where("role", "==", "MANAGER")
        .where("status", "==", "active")
        .limit(1)
        .stream()
    )

    for doc in docs:
        member = doc.to_dict()
        return {
            "name": member.get("name"),
            "email": member.get("email"),
            "role": member.get("role"),
            "contacts": member.get("contacts") or member.get("phone") or ""
        }

    return None
