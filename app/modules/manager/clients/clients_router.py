from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.modules.manager.clients.service_clients import get_clients

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("")
def list_clients(user=Depends(get_current_user)):
    if user["role"] not in ["OWNER", "MANAGER"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return get_clients(user["business_id"])
