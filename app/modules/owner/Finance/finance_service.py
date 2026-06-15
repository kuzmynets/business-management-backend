from datetime import datetime
from app.firebase import db


def serialize_date(value):
    if not value:
        return None
    if isinstance(value, str):
        return value
    try:
        return value.isoformat()
    except:
        return None


def get_finance_transactions(business_id: str, page: int = 1, limit: int = 10):

    docs = (
        db.collection("finance")
        .where("business_id", "==", business_id)
        .stream()
    )

    result = []
    income_total = 0.0
    expense_total = 0.0

    for doc in docs:
        t = doc.to_dict()
        amount = float(t.get("amount", 0))
        if t.get("type") == "INCOME":
            income_total += amount
        elif t.get("type") == "EXPENSE":
            expense_total += amount

        result.append({
            "id": doc.id,
            "type": t.get("type", "EXPENSE"),
            "amount": amount,
            "category": t.get("category"),
            "order_id": t.get("order_id"),
            "order_title": t.get("order_title"),
            "description": t.get("description"),
            "date": serialize_date(t.get("date")),
        })

    result.sort(key=lambda x: x["date"] or "", reverse=True)

    total = len(result)
    page = max(page, 1)
    limit = max(min(limit, 100), 1)
    start = (page - 1) * limit
    end = start + limit
    total_pages = (total + limit - 1) // limit

    return {
        "items": result[start:end],
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "summary": {
            "income": income_total,
            "expenses": expense_total,
            "profit": income_total - expense_total
        }
    }


def create_finance_transaction(business_id: str, data: dict):

    tx = {
        "type": data["type"],   # INCOME / EXPENSE
        "amount": float(data.get("amount", 0)),
        "category": data.get("category", ""),
        "order_id": data.get("order_id"),
        "order_title": data.get("order_title"),
        "description": data.get("description"),
        "business_id": business_id,
        "date": data.get("date") or datetime.utcnow(),
        "created_at": datetime.utcnow()
    }

    ref = db.collection("finance").add(tx)

    return {
        "id": ref[1].id,
        **tx,
        "date": serialize_date(tx["date"])
    }


def create_order_income_transaction(business_id: str, order_id: str, order: dict, existing_income_order_ids=None):
    if existing_income_order_ids is not None and order_id in existing_income_order_ids:
        return None

    if existing_income_order_ids is None:
        exists = (
            db.collection("finance")
            .where("order_id", "==", order_id)
            .where("type", "==", "INCOME")
            .limit(1)
            .stream()
        )

        if list(exists):
            return None

    price = float(order.get("price") or order.get("budget") or 0)
    if price <= 0:
        return None

    return create_finance_transaction(business_id, {
        "type": "INCOME",
        "amount": price,
        "category": "Order Payment",
        "order_id": order_id,
        "order_title": order.get("title"),
        "description": f"Income from order {order.get('title')}",
        "date": order.get("completed_at") or order.get("updated_at") or datetime.utcnow(),
    })


def create_order_income_transactions(business_id: str):

    orders = (
        db.collection("orders")
        .where("business_id", "==", business_id)
        .where("status", "==", "COMPLETED")
        .stream()
    )

    income_docs = (
        db.collection("finance")
        .where("business_id", "==", business_id)
        .where("type", "==", "INCOME")
        .stream()
    )
    existing_income_order_ids = set()
    for doc in income_docs:
        order_id = doc.to_dict().get("order_id")
        if order_id:
            existing_income_order_ids.add(order_id)

    created = 0

    for o in orders:
        order = o.to_dict()

        if create_order_income_transaction(business_id, o.id, order, existing_income_order_ids):
            existing_income_order_ids.add(o.id)
            created += 1

    return {"created": created}


def create_expense_transaction(business_id: str, data: dict):

    return create_finance_transaction(business_id, {
        "type": "EXPENSE",
        "amount": data.get("amount"),
        "category": data.get("category"),
        "description": data.get("description"),
        "date": data.get("date"),
    })
