from fastapi import APIRouter, Depends, HTTPException, Query, Body
from app.core.security import get_current_user
from app.modules.manager.orders_service import (
    get_orders,
    create_order,
    update_order,
    update_order_status
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
def list_orders(
    status: str | None = Query(None),
    current_user: dict = Depends(get_current_user)
):
    return get_orders(current_user["business_id"], status)


@router.post("")
def new_order(
    data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return create_order(data, current_user["business_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{order_id}")
def edit_order(
    order_id: str,
    data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return update_order(order_id, data, current_user["business_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{order_id}/status")
def change_status(
    order_id: str,
    data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return update_order_status(
            order_id,
            data["status"],
            current_user["business_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))