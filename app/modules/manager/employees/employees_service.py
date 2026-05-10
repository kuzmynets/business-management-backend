from app.firebase import db


def get_employees(business_id: str):

    docs = (
        db.collection("users")
        .where("business_id", "==", business_id)
        .where("role", "==", "EMPLOYEE")
        .stream()
    )

    result = []

    for d in docs:
        u = d.to_dict()

        result.append({
            "id": d.id,
            "email": u.get("email"),
            "name": u.get("name")
        })

    return result