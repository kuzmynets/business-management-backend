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

    if hasattr(v, "tzinfo"):
        return v.replace(tzinfo=timezone.utc) if v.tzinfo is None else v

    return None


def _month(dt):
    return f"{dt.year}-{dt.month:02d}"


def _is_done(status: str):
    return status in ["DONE", "COMPLETED"]


def _money(o: dict):
    return float(
        o.get("total_amount")
        or o.get("price")
        or o.get("budget")
        or 0
    )


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
        db.collection("finance")
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
        updated = _dt(order.get("updated_at"))

        if created:
            revenue[_month(created)] += _money(order)

        # FIX: completed_by priority
        if _is_done(order.get("status")):
            uid = (
                order.get("completed_by")
                or order.get("assigned_to")
                or order.get("created_by")
            )

            if uid in performance:
                performance[uid]["orders_completed"] += 1

        # bottleneck requires valid dates
        if created and updated:
            diff_days = (updated - created).total_seconds() / 86400

    # ---------------- TASKS ----------------
    for t in tasks:
        task = t.to_dict()

        uid = task.get("assigned_to")

        if uid and uid in performance and _is_done(task.get("status")):
            performance[uid]["tasks_completed"] += 1

    # ---------------- FINANCE ----------------
    for tr in transactions:
        tx = tr.to_dict()

        dt = _dt(tx.get("date"))
        if not dt:
            continue

        m = _month(dt)
        amount = float(tx.get("amount") or 0)

        if tx.get("type") == "INCOME":
            revenue[m] += amount
        elif tx.get("type") == "EXPENSE":
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

        diff_days = (updated - created).total_seconds() / 86400

        bottleneck_map[status]["status"] = status
        bottleneck_map[status]["total_days"] += diff_days
        bottleneck_map[status]["count"] += 1

    bottlenecks = []

    for status, data in bottleneck_map.items():
        avg = data["total_days"] / data["count"] if data["count"] else 0

        bottlenecks.append({
            "status": status,
            "avg_days": round(avg, 2)
        })

    return {
        "revenue": [
            {"month": m, "amount": a}
            for m, a in sorted(revenue.items())
        ],

        "manager_performance": sorted(
            performance.values(),
            key=lambda x: (
                x["orders_completed"] + x["tasks_completed"]
            ),
            reverse=True
        ),

        "bottlenecks": bottlenecks
    }