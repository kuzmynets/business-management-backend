from datetime import datetime, timedelta
from typing import List, Dict
from google.cloud import firestore

db = firestore.Client()

def get_analytics_data(business_id: str) -> Dict:
    """
    Отримує аналітичні дані для бізнесу з Firestore.
    Повертає доходи, виконання замовлень, ефективність менеджерів і вузькі місця.
    """
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=6)

    # --- Доходи за останні 7 днів ---
    transactions_ref = db.collection("transactions")
    transactions_query = transactions_ref.where("business_id", "==", business_id).where("date", ">=", seven_days_ago).order_by("date")
    transactions_docs = transactions_query.stream()

    income_over_time = []
    daily_income_map = {}
    for doc in transactions_docs:
        data = doc.to_dict()
        date_str = data["date"].strftime("%Y-%m-%d")
        daily_income_map.setdefault(date_str, 0)
        if data.get("type") == "income":
            daily_income_map[date_str] += data.get("amount", 0)

    for i in range(7):
        day = (seven_days_ago + timedelta(days=i)).strftime("%Y-%m-%d")
        income_over_time.append({
            "date": day,
            "income": daily_income_map.get(day, 0)
        })

    # --- Виконання замовлень за останні 7 днів ---
    orders_ref = db.collection("orders")
    orders_query = orders_ref.where("business_id", "==", business_id).where("created_at", ">=", seven_days_ago).order_by("created_at")
    orders_docs = orders_query.stream()

    orders_completion = []
    daily_orders_map = {}
    for doc in orders_docs:
        data = doc.to_dict()
        date_str = data["created_at"].strftime("%Y-%m-%d")
        daily_orders_map.setdefault(date_str, {"completed": 0, "pending": 0})
        if data.get("status") == "COMPLETED":
            daily_orders_map[date_str]["completed"] += 1
        else:
            daily_orders_map[date_str]["pending"] += 1

    for i in range(7):
        day = (seven_days_ago + timedelta(days=i)).strftime("%Y-%m-%d")
        orders_completion.append(daily_orders_map.get(day, {"completed": 0, "pending": 0}))

    # --- Ефективність менеджерів ---
    managers_ref = db.collection("managers")
    managers_query = managers_ref.where("business_id", "==", business_id)
    managers_docs = managers_query.stream()

    managers_performance = []
    for doc in managers_docs:
        data = doc.to_dict()
        managers_performance.append({
            "manager": data["name"],
            "completed_orders": data.get("completed_orders", 0),
            "pending_orders": data.get("pending_orders", 0)
        })

    # --- Вузькі місця ---
    tasks_ref = db.collection("tasks")
    tasks_query = tasks_ref.where("business_id", "==", business_id).where("status", "==", "BLOCKED")
    tasks_docs = tasks_query.stream()

    bottlenecks = []
    for doc in tasks_docs:
        data = doc.to_dict()
        bottlenecks.append({
            "task_title": data.get("title", ""),
            "issue": data.get("issue", "Unknown issue")
        })

    # --- Підписка ---
    business_ref = db.collection("businesses").document(business_id)
    business_doc = business_ref.get()
    has_subscription = False
    if business_doc.exists:
        has_subscription = business_doc.to_dict().get("subscription") in ["PRO", "ENTERPRISE"]

    return {
        "has_subscription": has_subscription,
        "incomeOverTime": income_over_time,
        "ordersCompletion": orders_completion,
        "managersPerformance": managers_performance,
        "bottlenecks": bottlenecks
    }