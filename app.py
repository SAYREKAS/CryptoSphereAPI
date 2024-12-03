import uvicorn
from fastapi import FastAPI

from src.views.users_views import router as users_router
from src.views.coins_views import router as coins_router

app = FastAPI()

API_VERSION = "/api/v1"
app.include_router(users_router, prefix=API_VERSION + "/users", tags=["Users"])
app.include_router(coins_router, prefix=API_VERSION + "/coins", tags=["Coins"])


if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)
