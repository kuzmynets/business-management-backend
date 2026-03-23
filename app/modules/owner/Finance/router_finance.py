from fastapi import APIRouter, Query, Depends
from typing import List, Dict
from datetime import datetime, timedelta
from app.modules.owner.Finance.finance_service import get_finance_data
from app.firebase import db

router = APIRouter(prefix="/finance", tags=["Finance"])

@router.get("")
async def finance(
    business_id: str = Query(...),
    period: str = Query("month"),
):
    """
    Повертає фінансові транзакції бізнесу з Firebase за період.
    """
    data: List[Dict] = await get_finance_data(db, business_id, period)
    return data