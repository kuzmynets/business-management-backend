from typing import List, Dict
from datetime import datetime
from google.cloud import firestore

def parse_period(period: str) -> datetime:
    now = datetime.utcnow()
    if period == "day":
        start = datetime(now.year, now.month, now.day)
    elif period == "month":
        start = datetime(now.year, now.month, 1)
    elif period == "year":
        start = datetime(now.year, 1, 1)
    else:
        start = datetime.min
    return start

async def get_finance_data(db: firestore.Client, business_id: str, period: str) -> List[Dict]:
    start_date = parse_period(period)

    transactions_ref = db.collection("transactions")
    query = transactions_ref.where("business_id", "==", business_id).where("date", ">=", start_date).order_by("date", direction=firestore.Query.DESCENDING)
    docs = query.stream()

    result = []
    async for doc in docs:
        t = doc.to_dict()
        # підтягуємо назву замовлення, якщо є
        order_title = None
        if t.get("order_id"):
            order_doc = await db.collection("orders").document(t["order_id"]).get()
            if order_doc.exists:
                order_title = order_doc.to_dict().get("title")
        result.append({
            "id": doc.id,
            "date": t.get("date").isoformat() if t.get("date") else None,
            "type": t.get("type"),
            "income": t.get("amount") if t.get("type") == "income" else 0.0,
            "expense": t.get("amount") if t.get("type") == "expense" else 0.0,
            "order_id": t.get("order_id"),
            "order_title": order_title,
            "description": t.get("description")
        })
    return result