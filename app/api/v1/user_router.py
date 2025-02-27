from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends

from api.auth import check_token, create_jwt_token
from domain.domain_user import DomainUser
from .schemas.user_schema import UserCreate, UserRead, UserToken, UserUpdatePassword
from ..dependencies import get_user_service
from services.user_service import UserService
from domain.exceptions import DoubleFoundError, NotFoundError, RepositoryException


router = APIRouter(
    prefix="/users",
    tags=["/v1/users"],
    responses={404: {"description": "User not found"}},
)


@router.post("/", response_model=UserRead)
async def create_user(
    data: UserCreate, service: Annotated[UserService, Depends(get_user_service)]
) -> UserRead | None:
    try:
        user = await service.create(data=data.model_dump())
        return UserRead.model_validate(user)
    except DoubleFoundError as ex:
        raise HTTPException(422, str(ex))


@router.post("/login", response_model=UserToken)
async def login(user_data: UserCreate, service: Annotated[UserService, Depends(get_user_service)]):
    try:
        user = await service.verify_password(**user_data.model_dump())
        token = create_jwt_token(user_data.model_dump(exclude_unset=True))
        return UserToken(
            id=user.id,
            username=user.username,
            token=token,
        )
    except NotFoundError:
        raise HTTPException(
            422,
            f"Wrong password or user with username {
                            user_data.username} not found.",
        )


@router.get("/{id}", response_model=UserRead)
async def read_user(
    id: int,
    user: Annotated[DomainUser, Depends(check_token)],
) -> UserRead:
    try:
        if user.id == id:
            return UserRead.model_validate(user)
        else:
            raise HTTPException(422, f"Wrong user id {id}")
    except ValueError as ex:
        raise HTTPException(422, str(ex))
    except NotFoundError:
        raise HTTPException(404, f"User with id {id} not found.")


@router.post("/update_password", response_model=UserRead)
async def update_user_password(
    data: UserUpdatePassword,
    service: Annotated[UserService, Depends(get_user_service)],
    user: Annotated[DomainUser, Depends(check_token)],
) -> UserRead | None:
    try:
        user = await service.update_password(
            username=user.username,
            old_password=data.old_password,
            new_password=data.new_password,
        )
        return UserRead.model_validate(user)
    except RepositoryException as ex:
        raise HTTPException(422, str(ex))
