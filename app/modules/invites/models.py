from firebase_admin import firestore

db = firestore.client()

async def save_invite(invite: dict):
    doc_ref = db.collection("invites").document(invite["token"])
    doc_ref.set(invite)
    return invite["token"]