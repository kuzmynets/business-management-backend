import uuid
from app.firebase import db
from datetime import datetime, timezone
ALLOWED_STATUSES = ["pending", "in_progress", "done"]

def serialize_project(doc):
    data = doc.to_dict()
    data["id"] = doc.id

    if data.get("created_at"):
        created = data["created_at"]
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        data["created_at"] = created.isoformat()

    return data

def get_all_projects(business_id: str):
    query = db.collection("projects").where("business_id", "==", business_id)
    return [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]

def get_my_projects(manager_uid: str):
    query = (
        db.collection("projects")
        .where("managerId", "==", manager_uid)
        .stream()
    )

    return [serialize_project(doc) for doc in query]

def create_project(title: str, manager_uid: str):
    if not title or not title.strip():
        raise ValueError("Title required")

    doc_ref = db.collection("projects").add({
        "title": title.strip(),
        "description": "",
        "managerId": manager_uid,
        "created_at": datetime.now(timezone.utc),
    })

    project_id = doc_ref[1].id

    return {
        "id": project_id,
        "title": title.strip(),
    }

def serialize_task(doc):
    data = doc.to_dict()
    data["id"] = doc.id

    if data.get("deadline"):
        deadline = data["deadline"]
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        data["deadline"] = deadline.isoformat()

    if data.get("assigned_to"):
        user_doc = db.collection("users").document(data["assigned_to"]).get()
        data["assigned_email"] = user_doc.to_dict()["email"] if user_doc.exists else None

    return data


def get_tasks_by_project(project_id: str):
    query = db.collection("tasks").where("project_id", "==", project_id)
    return [serialize_task(doc) for doc in query.stream()]


def create_task1(title: str, description: str, project_id: str, assigned_to: str):
    if not title.strip():
        raise ValueError("Task title required")

    doc_ref = db.collection("tasks").add({
        "title": title.strip(),
        "description": description.strip(),
        "project_id": project_id,
        "assigned_to": assigned_to,
        "status": "pending",
        "created_at": datetime.now(timezone.utc)
    })

    task_doc = doc_ref[1].get()
    return serialize_task(task_doc)

def get_project_by_id(project_id: str):
    doc = db.collection("projects").document(project_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = doc.id
    return data

def create_task_service(title: str, project_id: str, assigned_to: str, description: str = ""):
    if not title or not project_id or not assigned_to:
        raise ValueError("Missing required fields")

    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "title": title,
        "description": description,
        "project_id": project_id,
        "assigned_to": assigned_to,
        "status": "pending",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    db.collection("tasks").document(task_id).set(task)

    user_doc = db.collection("users").document(assigned_to).get()
    if user_doc.exists:
        task["assigned_email"] = user_doc.to_dict().get("email")

    return task