from fastapi import APIRouter, HTTPException, Depends
from app.modules.manager.orders.orders_service import (
    get_orders,
    create_order,
    update_order_status
)
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/orders", tags=["orders"])


class CreateOrderRequest(BaseModel):
    title: str
    client: str
    deadline: str | None = None


class UpdateStatusRequest(BaseModel):
    status: str


@router.get("")
def list_orders(current_user: dict = Depends(get_current_user)):
    return get_orders(current_user["business_id"])


@router.post("")
def create_order_endpoint(data: CreateOrderRequest, current_user: dict = Depends(get_current_user)):
    return create_order(
        business_id=current_user["business_id"],
        title=data.title,
        client=data.client,
        deadline=data.deadline
    )


@router.patch("/{order_id}/status")
def update_status(order_id: str, data: UpdateStatusRequest):
    order = update_order_status(order_id, data.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order