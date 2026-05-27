from datetime import datetime, timezone
from collections import defaultdict
from app.firebase import db
from app.modules.owner.Finance.finance_service import create_order_income_transactions


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
    create_order_income_transactions(business_id)

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

    members = list(
        db.collection("business_members")
        .where("business_id", "==", business_id)
        .where("status", "==", "active")
        .stream()
    )

    finance = list(
        db.collection("finance")
        .where("business_id", "==", business_id)
        .stream()
    )

    revenue = defaultdict(float)
    income_total = 0.0
    expense_total = 0.0

    performance = defaultdict(lambda: {
        "user_id": "",
        "name": "",
        "role": "",
        "orders_completed": 0,
        "tasks_completed": 0
    })

    bottlenecks = defaultdict(int)
    completed_orders = 0
    active_orders = 0
    completed_tasks = 0
    active_tasks = 0

    # ---------------- MEMBERS ----------------
    for m in members:
        d = m.to_dict()
        user_id = d.get("user_id")

        if not user_id or d.get("role") == "OWNER":
            continue

        performance[user_id]["user_id"] = user_id
        performance[user_id]["name"] = d.get("name") or d.get("email") or "Unknown"
        performance[user_id]["role"] = d.get("role", "EMPLOYEE")

    # ---------------- ORDERS ----------------
    for o in orders:
        order = o.to_dict()

        # FIX: completion tracking
        if order.get("status") == "COMPLETED":
            completed_orders += 1
            completer = order.get("completed_by")

            if completer and completer in performance:
                performance[completer]["orders_completed"] += 1
        else:
            active_orders += 1
            bottlenecks[order.get("status", "NEW")] += 1

    # ---------------- TASKS ----------------
    for t in tasks:
        task = t.to_dict()

        if task.get("status") == "DONE":
            completed_tasks += 1
            uid = task.get("assigned_to")
            if uid and uid in performance:
                performance[uid]["tasks_completed"] += 1
        else:
            active_tasks += 1
            bottlenecks[task.get("status", "NEW")] += 1

    # ---------------- FINANCE ----------------
    for f in finance:
        tx = f.to_dict()

        dt = _dt(tx.get("date"))
        if not dt:
            continue

        m = _month(dt)
        amount = float(tx.get("amount") or 0)

        if tx.get("type") == "INCOME":
            income_total += amount
            revenue[m] += amount
        elif tx.get("type") == "EXPENSE":
            expense_total += amount
            revenue[m] -= amount

    total_orders = completed_orders + active_orders
    total_tasks = completed_tasks + active_tasks
    performance_list = sorted(
        performance.values(),
        key=lambda x: x["orders_completed"] + x["tasks_completed"],
        reverse=True
    )

    # ---------------- OUTPUT ----------------
    return {
        "revenue": [
            {"month": m, "amount": a}
            for m, a in sorted(revenue.items())
        ],

        "summary": {
            "income": income_total,
            "expenses": expense_total,
            "profit": income_total - expense_total,
            "completed_orders": completed_orders,
            "active_orders": active_orders,
            "completed_tasks": completed_tasks,
            "active_tasks": active_tasks,
            "order_completion_rate": round((completed_orders / total_orders) * 100, 1) if total_orders else 0,
            "task_completion_rate": round((completed_tasks / total_tasks) * 100, 1) if total_tasks else 0,
            "avg_order_value": round(income_total / completed_orders, 2) if completed_orders else 0,
            "team_members": len(performance_list)
        },

        "manager_performance": performance_list,
        "top_performers": performance_list[:3],

        "bottlenecks": [
            {"status": status, "count": count}
            for status, count in sorted(bottlenecks.items())
        ]
    }
