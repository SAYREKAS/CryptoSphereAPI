from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.config import settings
from api.database.db_helper import db_helper
from api.v1.views.users_views import router as users_router
from api.v1.views.coins_views import router as coins_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await db_helper.dispose()


main_app = FastAPI(lifespan=lifespan)
main_app.include_router(users_router, prefix=settings.api.v1.users_prefix, tags=["Users"])
main_app.include_router(coins_router, prefix=settings.api.v1.coins_prefix, tags=["Coins"])


if __name__ == "__main__":
    uvicorn.run(
        app="main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload,
    )
