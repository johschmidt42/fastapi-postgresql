from fastapi import APIRouter

router: APIRouter = APIRouter(
    tags=["User-Company Links"],
    prefix="/user-company-links",
)
