from datetime import datetime
from app.firebase import db


STATUSES = ["NEW", "IN_PROGRESS", "REVIEW", "COMPLETED"]


def get_orders(business_id: str):

    docs = (
        db.collection("orders")
        .where("business_id", "==", business_id)
        .stream()
    )

    result = []

    for doc in docs:
        o = doc.to_dict()

        result.append({
            "id": doc.id,
            "title": o.get("title"),
            "client_name": o.get("client_name"),
            "status": o.get("status", "NEW")
        })

    return result


def create_order(business_id: str, data, user):

    client_name = data.client_name

    if data.client_id:
        client_doc = db.collection("clients").document(data.client_id).get()
        if client_doc.exists:
            client_name = client_doc.to_dict().get("name")

    elif data.client_name:
        db.collection("clients").add({
            "name": data.client_name,
            "business_id": business_id,
            "created_at": datetime.utcnow()
        })

    order_data = {
        "title": data.title,
        "client_name": client_name,
        "client_id": data.client_id,
        "budget": data.budget,
        "deadline": data.deadline,
        "description": data.description,

        "status": "NEW",

        "business_id": business_id,

        "created_by": user["uid"],   # FIX
        "completed_by": None,        # FIX

        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    doc_ref = db.collection("orders").document()
    doc_ref.set(order_data)

    return {
        "id": doc_ref.id,
        **order_data
    }


def get_order_by_id(order_id: str):

    ref = db.collection("orders").document(order_id)
    doc = ref.get()

    if not doc.exists:
        return None

    order = doc.to_dict()

    tasks_docs = (
        db.collection("tasks")
        .where("order_id", "==", order_id)
        .stream()
    )

    history_docs = (
        db.collection("order_history")
        .where("order_id", "==", order_id)
        .stream()
    )

    tasks = [
        {
            "id": t.id,
            **t.to_dict()
        }
        for t in tasks_docs
    ]

    history = [
        {
            "id": h.id,
            **h.to_dict()
        }
        for h in history_docs
    ]

    return {
        "id": order_id,
        **order,
        "tasks": tasks,
        "history": history
    }


def update_order_fields(order_id: str, data: dict):

    ref = db.collection("orders").document(order_id)
    doc = ref.get()

    if not doc.exists:
        return None

    allowed_fields = ["title", "description", "budget", "deadline", "status"]

    update_data = {}

    for key in allowed_fields:
        if key in data:
            update_data[key] = data[key]

    if not update_data:
        return {"id": order_id}

    update_data["updated_at"] = datetime.utcnow()

    ref.update(update_data)

    if "status" in update_data:
        db.collection("order_history").add({
            "order_id": order_id,
            "action": f"status -> {update_data['status']}",
            "created_at": datetime.utcnow()
        })

    return {
        "id": order_id,
        **update_data
    }


def update_order_status(order_id: str, status: str, user):

    if status not in STATUSES:
        return None

    ref = db.collection("orders").document(order_id)
    doc = ref.get()

    if not doc.exists:
        return None

    update_data = {
        "status": status,
        "updated_at": datetime.utcnow()
    }

    # FIX: якщо завершили — фіксуємо хто завершив
    if status == "COMPLETED":
        update_data["completed_by"] = user["uid"]

    ref.update(update_data)

    db.collection("order_history").add({
        "order_id": order_id,
        "action": f"Status -> {status}",
        "created_at": datetime.utcnow()
    })

    return {
        "id": order_id,
        **update_data
    }