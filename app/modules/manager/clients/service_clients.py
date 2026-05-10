from app.firebase import db


def get_clients(business_id: str):

    docs = (
        db.collection("clients")
        .where("business_id", "==", business_id)
        .stream()
    )

    result = []

    for doc in docs:
        data = doc.to_dict()

        result.append({
            "id": doc.id,
            "name": data.get("name")
        })

    return result