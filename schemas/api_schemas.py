from typing import Optional

from pydantic import BaseModel, EmailStr


class AddUserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class AddUserReportSchema(BaseModel):
    success: bool = False
    error_message: Optional[str | None] = None
