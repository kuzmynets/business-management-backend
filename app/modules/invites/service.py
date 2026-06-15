from app.firebase import db
from app.core.email_service import send_invite_email
from firebase_admin import auth as admin_auth
from datetime import datetime, timedelta, timezone
import random
import string

INVITE_EXPIRE_DAYS = 3

def generate_token(length: int = 32) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

def generate_temp_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(random.choice(chars) for _ in range(length))

async def create_invite(email: str, role: str, business_id: str, created_by_role: str = "OWNER"):
    token = generate_token()
    temp_password = None
    existing_user = False

    try:
        user_record = admin_auth.get_user_by_email(email)
        existing_user = True
    except admin_auth.EmailAlreadyExistsError:
        user_record = admin_auth.get_user_by_email(email)
        existing_user = True
    except Exception:
        temp_password = generate_temp_password()
        user_record = admin_auth.create_user(email=email, password=temp_password, email_verified=False)

    existing_member_docs = (
        db.collection("business_members")
        .where("business_id", "==", business_id)
        .where("user_id", "==", user_record.uid)
        .where("status", "==", "active")
        .limit(1)
        .stream()
    )

    if list(existing_member_docs):
        raise ValueError("User is already an active member of this business")

    invite = {
        "email": email,
        "role": role,
        "business_id": business_id,
        "status": "pending",
        "token": token,
        "temp_password": temp_password,
        "existing_user": existing_user,
        "requires_owner_approval": created_by_role == "MANAGER",
        "created_by_role": created_by_role,
        "expires_at": datetime.utcnow() + timedelta(days=INVITE_EXPIRE_DAYS),
        "created_at": datetime.utcnow()
    }

    db.collection("invites").document(token).set(invite)

    await send_invite_email(to=email, temp_password=temp_password, token=token)

    return invite

def list_invites(business_id: str):
    invites_ref = db.collection("invites").where("business_id", "==", business_id)
    result = []
    for doc in invites_ref.stream():
        invite = doc.to_dict()
        invite["id"] = doc.id
        result.append(invite)
    return result


def list_members(business_id: str):
    docs = (
        db.collection("business_members")
        .where("business_id", "==", business_id)
        .stream()
    )

    members = []
    user_cache = {}
    for doc in docs:
        member = doc.to_dict()
        if member.get("status") not in ["active", "removal_requested"]:
            continue

        user_id = member.get("user_id")
        if user_id and user_id not in user_cache:
            user_doc = db.collection("users").document(user_id).get()
            user_cache[user_id] = user_doc.to_dict() if user_doc.exists else {}
        user = user_cache.get(user_id, {})

        members.append({
            "id": doc.id,
            "user_id": user_id,
            "email": member.get("email") or user.get("email"),
            "name": member.get("name") or user.get("full_name") or user.get("name"),
            "role": member.get("role"),
            "status": member.get("status"),
            "joined_at": member.get("joined_at") or member.get("created_at")
        })

    return members


def validate_invite(token: str):
    doc = db.collection("invites").document(token).get()
    if not doc.exists:
        return None

    invite = doc.to_dict()

    if invite["status"] != "pending" or invite.get("accepted_at"):
        return None

    # перетворюємо на offset-aware datetime
    expires_at = invite["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        return None

    return invite

def accept_invite(token: str, password: str | None = None):
    invite_ref = db.collection("invites").document(token)
    invite_doc = invite_ref.get()

    if not invite_doc.exists:
        raise ValueError("Invite not found")

    invite = invite_doc.to_dict()

    if invite["status"] != "pending" or invite.get("accepted_at"):
        raise ValueError("Invite already used")

    expires_at = invite["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise ValueError("Invite expired")

    email = invite["email"]

    user_record = admin_auth.get_user_by_email(email)
    if not invite.get("existing_user"):
        if not password:
            raise ValueError("Password is required")
        admin_auth.update_user(user_record.uid, password=password)
    uid = user_record.uid

    db.collection("users").document(uid).set({
        "email": email,
        "status": "active",
        "created_at": datetime.now(timezone.utc)
    }, merge=True)

    member_docs = (
        db.collection("business_members")
        .where("business_id", "==", invite["business_id"])
        .where("user_id", "==", uid)
        .limit(1)
        .stream()
    )

    member_status = "pending" if invite.get("requires_owner_approval") else "active"

    member_data = {
        "business_id": invite["business_id"],
        "user_id": uid,
        "email": email,
        "role": invite["role"],
        "status": member_status,
        "invite_token": token,
        "joined_at": datetime.now(timezone.utc) if member_status == "active" else None,
        "created_at": datetime.now(timezone.utc)
    }

    existing_member = None
    for doc in member_docs:
        existing_member = doc
        break

    if existing_member:
        existing_member.reference.update(member_data)
    else:
        db.collection("business_members").add(member_data)

    invite_ref.update({
        "status": "pending" if invite.get("requires_owner_approval") else "approved",
        "accepted_at": datetime.now(timezone.utc)
    })

    return {
        "email": email,
        "role": invite["role"],
        "business_id": invite["business_id"]
    }


def decline_invite(token: str):
    invite_ref = db.collection("invites").document(token)
    invite_doc = invite_ref.get()
    if not invite_doc.exists:
        return None

    invite = invite_doc.to_dict()
    if invite.get("status") != "pending":
        return None

    invite_ref.update({
        "status": "rejected",
        "rejected_at": datetime.now(timezone.utc),
        "rejected_by": "invitee"
    })

    return {"success": True}


def approve_invite(token: str, business_id: str):
    invite_ref = db.collection("invites").document(token)
    invite_doc = invite_ref.get()
    if not invite_doc.exists:
        return None

    invite = invite_doc.to_dict()
    if invite.get("business_id") != business_id:
        return None
    if not invite.get("accepted_at"):
        return None

    user = admin_auth.get_user_by_email(invite["email"])

    member_docs = (
        db.collection("business_members")
        .where("business_id", "==", business_id)
        .where("user_id", "==", user.uid)
        .limit(1)
        .stream()
    )

    member_ref = None
    for doc in member_docs:
        member_ref = doc.reference
        break

    data = {
        "business_id": business_id,
        "user_id": user.uid,
        "email": invite["email"],
        "role": invite["role"],
        "status": "active",
        "invite_token": token,
        "joined_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    if member_ref:
        member_ref.update(data)
    else:
        db.collection("business_members").add(data)

    invite_ref.update({
        "status": "approved",
        "approved_at": datetime.now(timezone.utc)
    })

    return {"success": True}


def reject_invite(token: str, business_id: str):
    invite_ref = db.collection("invites").document(token)
    invite_doc = invite_ref.get()
    if not invite_doc.exists:
        return None

    invite = invite_doc.to_dict()
    if invite.get("business_id") != business_id:
        return None

    invite_ref.update({
        "status": "rejected",
        "rejected_at": datetime.now(timezone.utc)
    })

    member_docs = (
        db.collection("business_members")
        .where("business_id", "==", business_id)
        .where("email", "==", invite["email"])
        .stream()
    )

    for doc in member_docs:
        doc.reference.update({
            "status": "rejected",
            "updated_at": datetime.now(timezone.utc)
        })

    return {"success": True}


def remove_member(member_id: str, business_id: str, actor_role: str = "OWNER"):
    ref = db.collection("business_members").document(member_id)
    doc = ref.get()
    if not doc.exists:
        return None

    member = doc.to_dict()
    if member.get("business_id") != business_id or member.get("role") == "OWNER":
        return None

    if actor_role == "MANAGER":
        ref.update({
            "status": "removal_requested",
            "updated_at": datetime.now(timezone.utc)
        })
        return {"success": True, "requires_owner_approval": True}

    ref.delete()
    return {"success": True}


def reject_member_removal(member_id: str, business_id: str):
    ref = db.collection("business_members").document(member_id)
    doc = ref.get()
    if not doc.exists:
        return None

    member = doc.to_dict()
    if member.get("business_id") != business_id or member.get("status") != "removal_requested":
        return None

    ref.update({
        "status": "active",
        "updated_at": datetime.now(timezone.utc)
    })

    return {"success": True}
