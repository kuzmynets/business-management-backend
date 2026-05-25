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

    transactions_docs = (
        db.collection("finance")
        .where("business_id", "==", business_id)
        .stream()
    )

    result = []

    for doc in transactions_docs:

        transaction = doc.to_dict()

        result.append({
            "id": doc.id,
            "type": transaction.get("type", "EXPENSE"),
            "amount": float(transaction.get("amount", 0)),
            "category": transaction.get("category"),
            "order_id": transaction.get("order_id"),
            "order_title": transaction.get("order_title"),
            "description": transaction.get("description"),
            "date": serialize_date(
                transaction.get("date")
            )
        })

    result.sort(
        key=lambda x: x.get("date") or "",
        reverse=True
    )

    return result


def create_finance_transaction(data: dict):

    transaction_data = {
        "type": data.get("type", "EXPENSE"),
        "amount": float(data.get("amount", 0)),
        "category": data.get("category"),
        "order_id": data.get("order_id"),
        "order_title": data.get("order_title"),
        "description": data.get("description"),
        "business_id": data.get("business_id"),
        "date": data.get("date") or datetime.utcnow(),
        "created_at": datetime.utcnow()
    }

    ref = db.collection("finance").add(transaction_data)

    return {
        "id": ref[1].id,
        **transaction_data,
        "date": serialize_date(transaction_data.get("date"))
    }


def create_order_income_transactions(business_id: str):

    orders_docs = (
        db.collection("orders")
        .where("business_id", "==", business_id)
        .stream()
    )

    created = 0

    for doc in orders_docs:

        order = doc.to_dict()

        existing = (
            db.collection("finance")
            .where("order_id", "==", doc.id)
            .where("type", "==", "INCOME")
            .limit(1)
            .stream()
        )

        if list(existing):
            continue

        price = order.get("price") or order.get("budget") or 0

        if float(price) <= 0:
            continue

        create_finance_transaction({
            "type": "INCOME",
            "amount": price,
            "category": "Order Payment",
            "order_id": doc.id,
            "order_title": order.get("title"),
            "description": f"Income from order {order.get('title')}",
            "business_id": business_id,
            "date": order.get("created_at")
        })

        created += 1

    return {
        "created": created
    }