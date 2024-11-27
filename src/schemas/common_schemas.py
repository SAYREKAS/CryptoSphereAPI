from pydantic import BaseModel


class ActionResult(BaseModel):
    """Represents the result of any action."""

    success: bool
    message: str
