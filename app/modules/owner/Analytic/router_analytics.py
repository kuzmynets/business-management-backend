





#Це заглушка знизу закомічений норм код, потрібні дані в БД

from fastapi import APIRouter, Query
from typing import Dict, List
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("")
def analytics_stub(business_id: str = Query(...)) -> Dict:
    """
    Заглушка для сторінки Analytics.
    Повертає фейкові дані для тестування фронтенду.
    """
    now = datetime.utcnow()

    # Income over time (останні 7 днів)
    income_over_time = []
    for i in range(7):
        income_over_time.append({
            "date": (now - timedelta(days=6-i)).strftime("%Y-%m-%d"),
            "income": 1000 + i * 150  # фейковий приріст
        })

    # Orders completion (останні 7 днів)
    orders_completion = []
    for i in range(7):
        orders_completion.append({
            "date": (now - timedelta(days=6-i)).strftime("%Y-%m-%d"),
            "completed": 5 + i,
            "pending": 3 + i // 2
        })

    # Managers performance
    managers_performance = [
        {"manager": "Alice", "completed_orders": 20, "pending_orders": 2},
        {"manager": "Bob", "completed_orders": 15, "pending_orders": 5},
        {"manager": "Charlie", "completed_orders": 18, "pending_orders": 1},
    ]

    # Bottlenecks
    bottlenecks = [
        {"task_title": "Order #12 packaging", "issue": "Delayed due to missing items"},
        {"task_title": "Order #7 delivery", "issue": "Driver unavailable"}
    ]

    return {
        "has_subscription": True,  # можна змінювати на False для тесту підписки
        "incomeOverTime": income_over_time,
        "ordersCompletion": orders_completion,
        "managersPerformance": managers_performance,
        "bottlenecks": bottlenecks
    }
# from fastapi import APIRouter, Query
# from typing import Dict
# from app.modules.owner.Analytic.analytics_service import get_analytics_data
#
# router = APIRouter(prefix="/analytics", tags=["Analytics"])
#
# @router.get("")
# def analytics(business_id: str = Query(...)) -> Dict:
#     return get_analytics_data(business_id)