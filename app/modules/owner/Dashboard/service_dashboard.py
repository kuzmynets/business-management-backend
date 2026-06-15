from app.firebase import db
from app.modules.owner.Finance.finance_service import create_order_income_transactions


def _user_label(user_id: str | None, cache: dict | None = None):
    if not user_id:
        return None

    if cache is not None and user_id in cache:
        return cache[user_id]

    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        if cache is not None:
            cache[user_id] = user_id
        return user_id

    user = doc.to_dict()
    label = user.get("full_name") or user.get("name") or user.get("email") or user_id
    if cache is not None:
        cache[user_id] = label
    return label


def get_orders_for_business(business_id: str):
    docs = (
        db.collection("orders")
        .where("business_id", "==", business_id)
        .stream()
    )

    orders = []
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        orders.append(item)

    return orders


def get_owner_dashboard_stats(business_id: str, owner_id: str):
    create_order_income_transactions(business_id)
    orders = get_orders_for_business(business_id)
    revenue, profit = calculate_revenue_and_profit(business_id)

    members = list(
        db.collection("business_members")
        .where("business_id", "==", business_id)
        .where("status", "==", "active")
        .stream()
    )

    businesses = list(
        db.collection("businesses")
        .where("owner_id", "==", owner_id)
        .stream()
    )

    return {
        "total_revenue": revenue,
        "profit": profit,
        "active_orders": len([
            order for order in orders
            if order.get("status") in ["NEW", "IN_PROGRESS", "REVIEW"]
        ]),
        "team_members": len(members),
        "businesses_count": len(businesses)
    }


def get_owner_work_overview(business_id: str):
    orders = get_orders_for_business(business_id)
    tasks_docs = (
        db.collection("tasks")
        .where("business_id", "==", business_id)
        .stream()
    )

    order_rows = []
    user_cache = {}
    for order in orders:
        created_by = order.get("created_by")
        completed_by = order.get("completed_by")
        order_rows.append({
            "id": order.get("id"),
            "title": order.get("title"),
            "client_name": order.get("client_name"),
            "budget": order.get("budget"),
            "status": order.get("status", "NEW"),
            "created_by": created_by,
            "created_by_name": _user_label(created_by, user_cache),
            "completed_by": completed_by,
            "completed_by_name": _user_label(completed_by, user_cache),
            "created_at": order.get("created_at"),
            "updated_at": order.get("updated_at")
        })

    task_rows = []
    for doc in tasks_docs:
        task = doc.to_dict()
        assigned_to = task.get("assigned_to")
        created_by = task.get("created_by")
        assigned_by = task.get("assigned_by") or created_by

        task_rows.append({
            "id": doc.id,
            "title": task.get("title"),
            "order_title": task.get("order_title"),
            "status": task.get("status", "NEW"),
            "priority": task.get("priority", "MEDIUM"),
            "created_by": created_by,
            "created_by_name": _user_label(created_by, user_cache),
            "assigned_by": assigned_by,
            "assigned_by_name": _user_label(assigned_by, user_cache),
            "assigned_to": assigned_to,
            "assigned_to_name": _user_label(assigned_to, user_cache),
            "deadline": task.get("deadline"),
            "updated_at": task.get("updated_at") or task.get("created_at")
        })

    order_rows.sort(key=lambda x: str(x.get("updated_at") or x.get("created_at") or ""), reverse=True)
    task_rows.sort(key=lambda x: str(x.get("updated_at") or ""), reverse=True)

    return {
        "orders": order_rows[:20],
        "tasks": task_rows[:20]
    }


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
