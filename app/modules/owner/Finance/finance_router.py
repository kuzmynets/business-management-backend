from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import get_current_user
from app.modules.owner.Finance.finance_service import (
    get_finance_transactions,
    create_order_income_transactions,
    create_expense_transaction
)

router = APIRouter(prefix="/finance", tags=["finance"])


class ExpenseRequest(BaseModel):
    amount: float
    category: str
    description: str | None = None


@router.get("")
def finance_dashboard(user=Depends(get_current_user)):
    return get_finance_transactions(user["business_id"])


@router.post("/sync-orders")
def sync_orders(user=Depends(get_current_user)):
    return create_order_income_transactions(user["business_id"])


@router.post("/expense")
def create_expense(
    data: ExpenseRequest,
    user=Depends(get_current_user)
):
    return create_expense_transaction(user["business_id"], data.dict())