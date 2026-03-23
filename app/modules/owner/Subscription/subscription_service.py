from app.firebase import db
from datetime import datetime
from google.cloud.firestore_v1 import DocumentReference

# Плани з id для фронтенду
PLANS = {
    "BASIC": {"id": "BASIC", "name": "Basic", "price": 0, "interval": "month"},
    "PRO": {"id": "PRO", "name": "Pro", "price": 20, "interval": "month"},
}


def get_subscription_for_business(business_id: str) -> dict:
    doc_ref: DocumentReference = db.collection("businesses").document(business_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None

    business = doc.to_dict()
    current_subscription_id = business.get("subscription", "BASIC")
    current_plan = PLANS.get(current_subscription_id, PLANS["BASIC"])

    return {
        "current": {
            "id": current_plan["id"],
            "name": current_plan["name"],
            "status": "active",
            "next_billing": None
        },
        "plans": list(PLANS.values())
    }


def set_subscription_for_business(business_id: str, plan_id: str) -> dict:
    if plan_id not in PLANS:
        raise ValueError("Invalid plan")

    doc_ref: DocumentReference = db.collection("businesses").document(business_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None

    doc_ref.update({
        "subscription": plan_id,
        "updated_at": datetime.utcnow()
    })

    return {"success": True, "subscription": plan_id}