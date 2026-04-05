from app.firebase import db
from datetime import datetime, timezone

def serialize_doc(doc):
    data = doc.to_dict()
    data["id"] = doc.id
    if data.get("deadline"):
        deadline = data["deadline"]
        if hasattr(deadline, "tzinfo") and deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        data["deadline"] = deadline.isoformat()[:10]
    return data

def get_active_orders(business_id: str):
    query = db.collection("orders").where("business_id", "==", business_id)\
                                   .where("status", "==", "IN_PROGRESS")
    return [serialize_doc(doc) for doc in query.stream()]

def get_overdue_orders(business_id: str):
    now = datetime.now(timezone.utc)
    query = db.collection("orders").where("business_id", "==", business_id)\
                                   .where("deadline", "<", now)
    return [serialize_doc(doc) for doc in query.stream()]

def get_team_tasks(business_id: str):
    query = db.collection("tasks").where("business_id", "==", business_id)\
                                  .where("status", "==", "IN_PROGRESS")
    return [serialize_doc(doc) for doc in query.stream()]

def get_overdue_tasks(business_id: str):
    now = datetime.now(timezone.utc)
    query = db.collection("tasks").where("business_id", "==", business_id)\
                                  .where("status", "==", "IN_PROGRESS")\
                                  .where("deadline", "<", now)
    return [serialize_doc(doc) for doc in query.stream()]

def get_problem_orders(business_id: str):
    query = db.collection("orders").where("business_id", "==", business_id)\
                                   .where("problematic", "==", True)
    return [serialize_doc(doc) for doc in query.stream()]