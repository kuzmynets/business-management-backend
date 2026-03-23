from pydantic import BaseModel

class SubscribeRequest(BaseModel):
    plan_id: str
    business_id: str