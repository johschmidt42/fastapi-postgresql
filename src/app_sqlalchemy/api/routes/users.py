from typing import Annotated, List, Any

from fastapi import APIRouter, Body, Depends, status, Query
from sqlalchemy import Select, Result, Sequence, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app_sqlalchemy.api.dependencies import validate_user_id, get_db_session
from app_sqlalchemy.api.models import UserResponseModel, UserInput, UserUpdate
from app_sqlalchemy.db.db_models import User

router: APIRouter = APIRouter(
    tags=["Users"],
    prefix="/users",
)


@router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_user(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user_input: Annotated[UserInput, Body(...)],
) -> str:
    new_user: User = User(
        id=user_input.id,
        name=user_input.name,
        created_at=user_input.created_at,
    )

    db_session.add(new_user)

    return user_input.id

@router.get(path="", response_model=List[UserResponseModel], status_code=status.HTTP_200_OK)
async def get_users(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
) -> List[UserResponseModel]:

    query: Select = select(User).limit(limit).offset(offset)

    result: Result = await db_session.execute(query)

    users: Sequence[Row | RowMapping | Any] = result.scalars().all()

    return [UserResponseModel.model_validate(user) for user in users]

@router.get(
    path="/{user_id}", response_model=UserResponseModel, status_code=status.HTTP_200_OK
)
async def get_user(
    user: Annotated[User, Depends(validate_user_id)],
) -> UserResponseModel:
    return UserResponseModel.model_validate(user)


# get users

@router.put(path="/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(
    user: Annotated[User, Depends(validate_user_id)],
    update: Annotated[UserUpdate, Body(...)],
) -> str:
    user.name = update.name
    user.last_updated_at = update.last_updated_at

    return user.id

@router.delete(
    path="/{user_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(validate_user_id)],
) -> None:
    await db_session.delete(user)
