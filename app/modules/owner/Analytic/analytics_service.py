from datetime import datetime, timezone
from collections import defaultdict
from app.firebase import db


def _dt(v):
    if not v:
        return None

    if isinstance(v, str):
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

    transactions = list(
        db.collection("transactions")
        .where("business_id", "==", business_id)
        .stream()
    )

    # ---------------- REVENUE ----------------

    revenue = defaultdict(float)

    # ---------------- PERFORMANCE ----------------

    performance = defaultdict(lambda: {
        "user_id": "",
        "name": "",
        "role": "",
        "orders_completed": 0,
        "tasks_completed": 0
    })

    user_map = {}

    for u in users:

        d = u.to_dict()

        role = d.get("role", "").upper()

        # OWNER НЕ ВКЛЮЧАЄМО В АНАЛІТИКУ
        if role == "OWNER":
            continue

        user_map[u.id] = d

        performance[u.id]["user_id"] = u.id
        performance[u.id]["name"] = (
            d.get("full_name")
            or d.get("email")
            or "Unknown"
        )
        performance[u.id]["role"] = role

    # ---------------- ORDERS ----------------

    for o in orders:

        order = o.to_dict()

        created = _dt(order.get("created_at"))

        if created:
            revenue[_month(created)] += float(
                order.get("price", 0)
            )

        if (
            order.get("status") == "DONE"
            and order.get("assigned_to")
        ):

            uid = order.get("assigned_to")

            if uid in performance:
                performance[uid]["orders_completed"] += 1

    # ---------------- TASKS ----------------

    for t in tasks:

        task = t.to_dict()

        uid = task.get("assigned_to")

        if (
            uid
            and uid in performance
            and task.get("status") == "DONE"
        ):
            performance[uid]["tasks_completed"] += 1

    # ---------------- TRANSACTIONS ----------------

    for tr in transactions:

        tx = tr.to_dict()

        dt = _dt(tx.get("date"))

        if not dt:
            continue

        m = _month(dt)

        amount = float(tx.get("amount", 0))

        if tx.get("type") == "INCOME":
            revenue[m] += amount
        else:
            revenue[m] -= amount

    # ---------------- BOTTLENECKS ----------------

    bottleneck_map = defaultdict(lambda: {
        "status": "",
        "total_days": 0,
        "count": 0
    })

    for o in orders:

        order = o.to_dict()

        created = _dt(order.get("created_at"))
        updated = _dt(order.get("updated_at"))

        status = order.get("status")

        if not created or not updated:
            continue

        diff_days = (
            updated - created
        ).total_seconds() / 86400

        bottleneck_map[status]["status"] = status
        bottleneck_map[status]["total_days"] += diff_days
        bottleneck_map[status]["count"] += 1

    bottlenecks = []

    for status, data in bottleneck_map.items():

        avg = 0

        if data["count"]:
            avg = data["total_days"] / data["count"]

        bottlenecks.append({
            "status": status,
            "avg_days": round(avg, 2)
        })

    return {
        "revenue": [
            {
                "month": month,
                "amount": amount
            }
            for month, amount in sorted(revenue.items())
        ],

        "manager_performance": sorted(
            performance.values(),
            key=lambda x: (
                x["orders_completed"]
                + x["tasks_completed"]
            ),
            reverse=True
        ),

        "bottlenecks": bottlenecks
    }