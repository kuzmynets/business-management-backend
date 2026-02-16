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

async def create_invite(email: str, role: str, business_id: str):
    token = generate_token()
    temp_password = generate_temp_password()

    try:
        user_record = admin_auth.create_user(email=email, password=temp_password, email_verified=False)
    except admin_auth.EmailAlreadyExistsError:
        user_record = admin_auth.get_user_by_email(email)
        admin_auth.update_user(user_record.uid, password=temp_password)

    invite = {
        "email": email,
        "role": role,
        "business_id": business_id,
        "status": "pending",
        "token": token,
        "temp_password": temp_password,
        "expires_at": datetime.utcnow() + timedelta(days=INVITE_EXPIRE_DAYS),
        "created_at": datetime.utcnow()
    }

    db.collection("invites").document(token).set(invite)

    await send_invite_email(to=email, temp_password=temp_password, token=token)

    return invite

def list_invites(business_id: str):
    invites_ref = db.collection("invites").where("business_id", "==", business_id)
    return [doc.to_dict() for doc in invites_ref.stream()]


def validate_invite(token: str):
    doc = db.collection("invites").document(token).get()
    if not doc.exists:
        return None

    invite = doc.to_dict()

    if invite["status"] != "pending":
        return None

    # перетворюємо на offset-aware datetime
    expires_at = invite["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        return None

    return invite

def accept_invite(token: str, password: str):
    invite_ref = db.collection("invites").document(token)
    invite_doc = invite_ref.get()

    if not invite_doc.exists:
        raise ValueError("Invite not found")

    invite = invite_doc.to_dict()

    if invite["status"] != "pending":
        raise ValueError("Invite already used")

    expires_at = invite["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise ValueError("Invite expired")

    email = invite["email"]

    user_record = admin_auth.get_user_by_email(email)
    admin_auth.update_user(user_record.uid, password=password)
    uid = user_record.uid

    db.collection("users").document(uid).set({
        "email": email,
        "role": invite["role"],
        "business_id": invite["business_id"],
        "status": "active",
        "created_at": datetime.now(timezone.utc)
    })

    invite_ref.update({
        "status": "accepted",
        "accepted_at": datetime.now(timezone.utc)
    })

    return {
        "email": email,
        "role": invite["role"],
        "business_id": invite["business_id"]
    }