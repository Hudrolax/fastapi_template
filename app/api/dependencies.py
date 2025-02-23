from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Type
from domain.domain_user import DomainUser
from domain.base_domain_model import BaseDomainModel
from db.models.base_model import BaseORMModel
from db.models.user import UserORM
from db.db import get_db
from services.user_service import UserService
from repositories.sqlalchemy_repo import SQLAlchemyRepository
from util.crypto_hash import CryptoHash


def sqlalchemy_repository_factory(
    db: AsyncSession,
    orm_class: Type[BaseORMModel],
    domain_model: Type[BaseDomainModel],
) -> SQLAlchemyRepository:
    return SQLAlchemyRepository(db, orm_class, domain_model)


def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    repository = sqlalchemy_repository_factory(db, orm_class=UserORM, domain_model=DomainUser)
    return UserService(repository, crypto_hash=CryptoHash())
