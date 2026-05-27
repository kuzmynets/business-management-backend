from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.modules.owner.Finance.finance_service import (
    get_finance_transactions,
    create_order_income_transactions,
    create_expense_transaction
)

router = APIRouter(prefix="/finance", tags=["finance"])


class ExpenseRequest(BaseModel):
    amount: float = Field(gt=0)
    category: str = Field(min_length=1)
    description: str | None = None


@router.get("")
def finance_dashboard(
    page: int = 1,
    limit: int = 10,
    user=Depends(get_current_user)
):
    if user["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Forbidden")
    create_order_income_transactions(user["business_id"])
    return get_finance_transactions(user["business_id"], page, limit)


@router.post("/sync-orders")
def sync_orders(user=Depends(get_current_user)):
    if user["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Forbidden")
    return create_order_income_transactions(user["business_id"])


@router.post("/expense")
def create_expense(
    data: ExpenseRequest,
    user=Depends(get_current_user)
):
    if user["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Forbidden")
    category = data.category.strip()
    if not category:
        raise HTTPException(status_code=400, detail="Category is required")
    payload = data.dict()
    payload["category"] = category
    return create_expense_transaction(user["business_id"], payload)
