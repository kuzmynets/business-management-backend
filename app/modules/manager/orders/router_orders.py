from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from app.modules.manager.orders.orders_service import (
    get_orders,
    create_order,
    get_order_by_id,
    update_order_fields,
    update_order_status
)

from app.core.security import get_current_user


router = APIRouter(prefix="/orders", tags=["orders"])


class CreateOrderRequest(BaseModel):
    title: str
    client_id: Optional[str] = None
    client_name: Optional[str] = None
    budget: Optional[float] = None
    deadline: Optional[str] = None
    description: Optional[str] = None


class UpdateOrderRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    deadline: Optional[str] = None
    status: Optional[str] = None


class UpdateStatusRequest(BaseModel):
    status: str


@router.get("")
def list_orders(user=Depends(get_current_user)):
    return get_orders(user["business_id"])


@router.post("")
def create_order_endpoint(
    data: CreateOrderRequest,
    user=Depends(get_current_user)
):
    return create_order(user["business_id"], data)


@router.get("/{order_id}")
def get_order(order_id: str):
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{order_id}")
def update_order(order_id: str, data: UpdateOrderRequest):
    result = update_order_fields(order_id, data.dict(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


@router.patch("/{order_id}/status")
def change_status(order_id: str, data: UpdateStatusRequest):
    result = update_order_status(order_id, data.status)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result