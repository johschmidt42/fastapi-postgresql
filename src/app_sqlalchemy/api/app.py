import os

from fastapi import FastAPI

from lifespan import lifespan
from app_sqlalchemy.api.routes import users
from app_sqlalchemy.api.routes import orders

app: FastAPI = FastAPI(lifespan=lifespan)
app.include_router(router=users.router)
app.include_router(router=orders.router)

if __name__ == "__main__":
    import uvicorn

    port: int = os.environ["PORT"] if os.environ.get("PORT") else 9000
    uvicorn.run(app=app, host="localhost", port=int(port))
