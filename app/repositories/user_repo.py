from typing import Protocol, Generic
from sqlalchemy import select

from db.models.base_model import TOrm

from domain.base_domain_model import TDomain
from domain.exceptions import RepositoryException

from .sqlalchemy_repo import CreateMixin, ReadMixin, UpdateMixin
from .interfaces import ICreateRepository, IReadRepository, IUpdateRepository

class IUserRepoProtocol(
    ICreateRepository[TDomain],
    IReadRepository[TDomain],
    IUpdateRepository[TDomain],
    Protocol,
):
    async def exists(self, username: str) -> bool:
        ...


class UserSQLAlchemyRepo(
    CreateMixin[TDomain, TOrm],
    ReadMixin[TDomain, TOrm],
    UpdateMixin[TDomain, TOrm],
    Generic[TDomain, TOrm],
):
    async def exists(self, username: str) -> bool:
        stmt = select(self.orm_class).filter_by(username=username)
        try:
            res = (await self.db.execute(stmt)).scalars().all()
            return len(res) > 0
        except Exception as ex:
            raise RepositoryException(str(ex))
