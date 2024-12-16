from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.db_helper import db_helper
from api.crud.transactions_crud import create_coin_transaction
from api.schemas.coins_crud_schemas import OperationActionSchema

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OperationActionSchema)
async def create_coin_transaction_endpoint(
    operation: OperationActionSchema,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    """Create a new coin transaction."""
    return await create_coin_transaction(operation=operation, session=session)
