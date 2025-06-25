import os

from fastapi import FastAPI

from app_sqlalchemy_core.api.lifespan import lifespan
from app_sqlalchemy_core.api.routes import companies

app: FastAPI = FastAPI(lifespan=lifespan)

app.include_router(router=companies.router)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    port: int = os.environ["PORT"] if os.environ.get("PORT") else 9000
    uvicorn.run(app=app, host="localhost", port=int(port))
