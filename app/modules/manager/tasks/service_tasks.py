from datetime import datetime
from app.firebase import db


def get_tasks(business_id: str):

    tasks_ref = (
        db.collection("tasks")
        .where("business_id", "==", business_id)
        .stream()
    )

    tasks = []

    for doc in tasks_ref:

        task = doc.to_dict()
        order_id = task.get("order_id")

        order_title = None
        if order_id:
            order_doc = db.collection("orders").document(order_id).get()
            if order_doc.exists:
                order_title = order_doc.to_dict().get("title")

        tasks.append({
            "id": doc.id,
            "title": task.get("title"),
            "status": task.get("status", "NEW"),
            "assigned_to": task.get("assigned_to"),
            "deadline": task.get("deadline"),
            "order_title": order_title
        })

    return tasks


def update_task_status(task_id: str, status: str):

    doc_ref = db.collection("tasks").document(task_id)
    doc = doc_ref.get()

    if not doc.exists:
        return None

    doc_ref.update({
        "status": status,
        "updated_at": datetime.utcnow()
    })

    task = doc.to_dict()

    return {
        "id": task_id,
        "status": status,
        "assigned_to": task.get("assigned_to")
    }


def assign_task(task_id: str, assigned_to: str | None):

    doc_ref = db.collection("tasks").document(task_id)
    doc = doc_ref.get()

    if not doc.exists:
        return None

    doc_ref.update({
        "assigned_to": assigned_to,
        "updated_at": datetime.utcnow()
    })

    task = doc.to_dict()

    return {
        "id": task_id,
        "assigned_to": assigned_to,
        "status": task.get("status")
    }