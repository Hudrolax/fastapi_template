from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from domain.domain_user import DomainUser
from db.models.user import UserORM
from db.db import get_db
from services.user_service import UserService
from repositories.user_repo import UserSQLAlchemyRepo
from util.crypto_hash import CryptoHash


def user_sqlalchemy_repository_factory(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserSQLAlchemyRepo:
    return UserSQLAlchemyRepo(db, UserORM, DomainUser)


def get_user_service(repo_factory = Depends(user_sqlalchemy_repository_factory)) -> UserService:
    repository = repo_factory()
    return UserService(
        repository = repository,
        crypto_hash = CryptoHash()
    )
