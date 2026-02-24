from app.firebase import db

def list_employees():
    query = db.collection("users").where("role", "==", "EMPLOYEE")
    employees = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        employees.append(data)
    return employees