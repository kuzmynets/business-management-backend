from datetime import datetime, timezone
from collections import defaultdict
from app.firebase import db


def _dt(v):
    if not v:
        return None

    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v.replace("Z", ""))
        except:
            return None

    return v.replace(tzinfo=timezone.utc) if v.tzinfo is None else v


def _month(dt):
    return f"{dt.year}-{dt.month:02d}"


def get_analytics(business_id: str):

    orders = list(
        db.collection("orders")
        .where("business_id", "==", business_id)
        .stream()
    )

    tasks = list(
        db.collection("tasks")
        .where("business_id", "==", business_id)
        .stream()
    )

    users = list(
        db.collection("users")
        .where("business_id", "==", business_id)
        .stream()
    )

    finance = list(
        db.collection("finance")
        .where("business_id", "==", business_id)
        .stream()
    )

    revenue = defaultdict(float)

    performance = defaultdict(lambda: {
        "user_id": "",
        "name": "",
        "role": "",
        "orders_completed": 0,
        "tasks_completed": 0
    })

    # ---------------- USERS ----------------
    for u in users:
        d = u.to_dict()

        if d.get("role") == "OWNER":
            continue

        performance[u.id]["user_id"] = u.id
        performance[u.id]["name"] = d.get("full_name") or d.get("email") or "Unknown"
        performance[u.id]["role"] = d.get("role", "EMPLOYEE")

    # ---------------- ORDERS ----------------
    for o in orders:
        order = o.to_dict()

        created = _dt(order.get("created_at"))
        if created:
            revenue[_month(created)] += float(order.get("budget") or 0)

        # FIX: completion tracking
        if order.get("status") == "COMPLETED":
            creator = order.get("created_by")
            completer = order.get("completed_by")

            if completer and completer in performance:
                performance[completer]["orders_completed"] += 1

    # ---------------- TASKS ----------------
    for t in tasks:
        task = t.to_dict()

        if task.get("status") == "DONE":
            uid = task.get("assigned_to")
            if uid and uid in performance:
                performance[uid]["tasks_completed"] += 1

    # ---------------- FINANCE ----------------
    for f in finance:
        tx = f.to_dict()

        dt = _dt(tx.get("date"))
        if not dt:
            continue

        m = _month(dt)
        amount = float(tx.get("amount") or 0)

        if tx.get("type") == "INCOME":
            revenue[m] += amount
        elif tx.get("type") == "EXPENSE":
            revenue[m] -= amount

    # ---------------- OUTPUT ----------------
    return {
        "revenue": [
            {"month": m, "amount": a}
            for m, a in sorted(revenue.items())
        ],

        "manager_performance": sorted(
            performance.values(),
            key=lambda x: x["orders_completed"] + x["tasks_completed"],
            reverse=True
        ),

        "bottlenecks": []
    }