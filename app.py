import uvicorn
from fastapi import FastAPI

from views.users_views import router as users_router

app = FastAPI()
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
