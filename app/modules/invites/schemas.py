from pydantic import BaseModel, EmailStr
from typing import Literal

class InviteCreateRequest(BaseModel):
    email: EmailStr
    role: Literal["MANAGER", "EMPLOYEE"]

class AcceptInviteRequest(BaseModel):
    new_password: str