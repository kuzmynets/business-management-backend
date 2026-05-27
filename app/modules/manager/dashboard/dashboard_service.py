from datetime import datetime, timezone
from app.firebase import db


def normalize_dt(value):
    if not value:
        return None

    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except:
            return None

    if not isinstance(value, datetime):
        return None

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value


def is_overdue(deadline):
    dt = normalize_dt(deadline)
    if not dt:
        return False
    return dt < datetime.now(timezone.utc)


def get_manager_dashboard(business_id: str):

    orders = (
        db.collection("orders")
        .where("business_id", "==", business_id)
        .stream()
    )

    tasks = (
        db.collection("tasks")
        .where("business_id", "==", business_id)
        .stream()
    )

    active_orders = []
    overdue_orders = []
    problem_orders = []
    completed_today = 0
    in_progress = 0
    today = datetime.now(timezone.utc).date()

    for o in orders:
        order = o.to_dict()

        item = {
            "id": o.id,
            "title": order.get("title"),
            "client": order.get("client_name"),
            "deadline": order.get("deadline")
        }

        status = order.get("status", "NEW")
        overdue = is_overdue(order.get("deadline"))

        if status in ["NEW", "IN_PROGRESS"]:
            active_orders.append(item)

        if status == "IN_PROGRESS":
            in_progress += 1

        updated = normalize_dt(order.get("updated_at"))
        if status == "COMPLETED" and updated and updated.date() == today:
            completed_today += 1

        if overdue:
            overdue_orders.append(item)

        # критичність = бізнес + дедлайн
        if overdue or status == "REVIEW":
            problem_orders.append(item)

    team_tasks = []
    overdue_tasks = []

    for t in tasks:
        task = t.to_dict()

        item = {
            "id": t.id,
            "title": task.get("title"),
            "assigned": task.get("assigned_to"),
            "deadline": task.get("deadline")
        }

        if task.get("status") == "IN_PROGRESS":
            team_tasks.append(item)
            in_progress += 1

        updated = normalize_dt(task.get("updated_at"))
        if task.get("status") == "DONE" and updated and updated.date() == today:
            completed_today += 1

        if is_overdue(task.get("deadline")):
            overdue_tasks.append(item)

    employees_count = len(list(
        db.collection("business_members")
        .where("business_id", "==", business_id)
        .where("role", "==", "EMPLOYEE")
        .where("status", "==", "active")
        .stream()
    ))

    return {
        "active_orders": active_orders,
        "overdue_orders": overdue_orders,
        "team_tasks": team_tasks,
        "overdue_tasks": overdue_tasks,
        "problem_orders": problem_orders,
        "completed_today": completed_today,
        "in_progress": in_progress,
        "employees_count": employees_count
    }
