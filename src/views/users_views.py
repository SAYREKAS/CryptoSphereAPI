from fastapi import APIRouter

from src.schemas.api_schemas import AddUserSchema, AddUserReportSchema

router = APIRouter()


@router.get("/")
def get_users():
    pass


@router.post("/")
async def create_user(user: AddUserSchema) -> AddUserReportSchema:
    return AddUserReportSchema(success=True if user else False)
