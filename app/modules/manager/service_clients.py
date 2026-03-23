from app.firebase import db

def get_clients(business_id: str):
    query = db.collection("clients").where("business_id", "==", business_id)
    return [
        {"id": doc.id, **doc.to_dict()}
        for doc in query.stream()
    ]