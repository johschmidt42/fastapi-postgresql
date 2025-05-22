from fastapi import APIRouter

router: APIRouter = APIRouter(
    tags=["Companies"],
    prefix="/companies",
)
