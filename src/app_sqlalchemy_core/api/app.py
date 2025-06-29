import os

from fastapi import FastAPI


from app_sqlalchemy_core.api.routes import users, professions, companies
from app_sqlalchemy_core.api.routes import orders
from app_sqlalchemy_core.api.routes import documents

from app_sqlalchemy_core.api.routes import user_company_links

from common.sqlalchemy.lifespan import lifespan

app: FastAPI = FastAPI(lifespan=lifespan)
app.include_router(router=users.router)
app.include_router(router=orders.router)
app.include_router(router=documents.router)
app.include_router(router=professions.router)
app.include_router(router=companies.router)
app.include_router(router=user_company_links.router)

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    port: int = os.environ["PORT"] if os.environ.get("PORT") else 9000
    uvicorn.run(app=app, host="localhost", port=int(port))
