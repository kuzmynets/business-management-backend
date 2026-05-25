from fastapi import APIRouter, Depends
from app.core.security import get_current_user

from app.modules.owner.Finance.finance_service import (
    get_finance_transactions,
    create_order_income_transactions
)

router = APIRouter(
    prefix="/finance",
    tags=["finance"]
)


@router.get("")
def finance_dashboard(user=Depends(get_current_user)):
    return get_finance_transactions(user["business_id"])


@router.post("/sync-orders")
def sync_order_transactions(user=Depends(get_current_user)):
    return create_order_income_transactions(user["business_id"])