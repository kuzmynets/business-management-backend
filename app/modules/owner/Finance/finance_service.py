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


def get_finance_transactions(business_id: str):

    docs = (
        db.collection("finance")
        .where("business_id", "==", business_id)
        .stream()
    )

    result = []

    for doc in docs:
        t = doc.to_dict()

        result.append({
            "id": doc.id,
            "type": t.get("type", "EXPENSE"),
            "amount": float(t.get("amount", 0)),
            "category": t.get("category"),
            "order_id": t.get("order_id"),
            "order_title": t.get("order_title"),
            "description": t.get("description"),
            "date": serialize_date(t.get("date")),
        })

    result.sort(key=lambda x: x["date"] or "", reverse=True)

    return result


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


def create_order_income_transactions(business_id: str):

    orders = (
        db.collection("orders")
        .where("business_id", "==", business_id)
        .stream()
    )

    created = 0

    for o in orders:
        order = o.to_dict()

        exists = (
            db.collection("finance")
            .where("order_id", "==", o.id)
            .where("type", "==", "INCOME")
            .limit(1)
            .stream()
        )

        if list(exists):
            continue

        price = float(order.get("price") or order.get("budget") or 0)

        if price <= 0:
            continue

        create_finance_transaction(business_id, {
            "type": "INCOME",
            "amount": price,
            "category": "Order Payment",
            "order_id": o.id,
            "order_title": order.get("title"),
            "description": f"Income from order {order.get('title')}",
            "date": order.get("created_at"),
        })

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