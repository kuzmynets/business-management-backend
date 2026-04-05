from datetime import datetime
from app.firebase import db


def get_orders(business_id: str):

    orders_ref = (
        db.collection("orders")
        .where("business_id", "==", business_id)
        .stream()
    )

    orders = []

    for doc in orders_ref:

        order = doc.to_dict()

        tasks_ref = (
            db.collection("tasks")
            .where("order_id", "==", doc.id)
            .stream()
        )

        tasks = []

        for t in tasks_ref:
            task = t.to_dict()
            tasks.append({
                "id": t.id,
                "title": task.get("title"),
                "status": task.get("status")
            })

        orders.append({
            "id": doc.id,
            "title": order.get("title"),
            "client": order.get("client"),
            "deadline": order.get("deadline"),
            "status": order.get("status", "NEW"),
            "tasks": tasks
        })

    return orders


def create_order(business_id: str, title: str, client: str, deadline: str | None):

    order_data = {
        "title": title,
        "client": client,
        "deadline": deadline,
        "status": "NEW",
        "business_id": business_id,
        "created_at": datetime.utcnow()
    }

    ref = db.collection("orders").add(order_data)

    return {
        "id": ref[1].id,
        **order_data,
        "tasks": []
    }


def update_order_status(order_id: str, status: str):

    doc_ref = db.collection("orders").document(order_id)
    doc = doc_ref.get()

    if not doc.exists:
        return None

    doc_ref.update({
        "status": status,
        "updated_at": datetime.utcnow()
    })

    order = doc.to_dict()

    return {
        "id": order_id,
        "title": order.get("title"),
        "client": order.get("client"),
        "deadline": order.get("deadline"),
        "status": status
    }