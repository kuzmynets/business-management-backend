from app.firebase import db


def get_orders_for_business(business_id: str):
    docs = (
        db.collection("businesses")
        .document(business_id)
        .collection("orders")
        .stream()
    )

    orders = []
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        orders.append(item)

    return orders


def get_recent_activities(business_id: str, limit: int = 10):
    orders = get_orders_for_business(business_id)

    tasks_docs = (
        db.collection("tasks")
        .where("business_id", "==", business_id)
        .stream()
    )

    activities = []

    for o in orders:
        activities.append({
            "type": "ORDER",
            "id": o["id"],
            "title": o.get("title"),
            "status": o.get("status"),
            "date": o.get("created_at")
        })

    for t in tasks_docs:
        task = t.to_dict()
        activities.append({
            "type": "TASK",
            "id": t.id,
            "title": task.get("title"),
            "status": task.get("status"),
            "date": task.get("updated_at") or task.get("created_at")
        })

    # без Firestore order_by → сортуємо в Python
    activities.sort(
        key=lambda x: x["date"] or "",
        reverse=True
    )

    return activities[:limit]


def calculate_revenue_and_profit(business_id: str):
    docs = (
        db.collection("finance")
        .where("business_id", "==", business_id)
        .stream()
    )

    revenue = 0.0
    expense = 0.0

    for d in docs:
        t = d.to_dict()

        amount = float(t.get("amount", 0))
        ttype = t.get("type")

        if ttype == "INCOME":
            revenue += amount
        elif ttype == "EXPENSE":
            expense += amount

    return revenue, revenue - expense