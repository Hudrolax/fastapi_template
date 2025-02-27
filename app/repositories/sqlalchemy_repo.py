from typing import Generic, Optional, Sequence, Type, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select

from db.models.base_model import TOrm
from domain.base_domain_model import TDomain
from domain.exceptions import NotFoundError, RepositoryException, DoubleFoundError


class BaseSQLAlchemyRepo(Generic[TDomain, TOrm]):
    def __init__(
        self,
        db: AsyncSession,
        domain_model: Type[TDomain],
        orm_class: Type[TOrm],
    ) -> None:
        self.db: AsyncSession = db
        self.domain_model = domain_model
        self.orm_class = orm_class


class CreateMixin(BaseSQLAlchemyRepo[TDomain, TOrm], Generic[TDomain, TOrm]):
    async def create(self, data: dict[str, Any]) -> TDomain:
        stmt = insert(self.orm_class).values(**data).returning(self.orm_class)
        result = await self.db.execute(stmt)
        row = result.scalar_one()
        return self.domain_model.model_validate(row)


class ReadMixin(BaseSQLAlchemyRepo[TDomain, TOrm], Generic[TDomain, TOrm]):
    async def read(self, filters: Optional[dict[str, Any]] = None) -> TDomain:
        stmt = select(self.orm_class)
        if filters:
            stmt = stmt.filter_by(**filters)
        try:
            res = (await self.db.execute(stmt)).scalars().all()
        except Exception as ex:
            raise RepositoryException(str(ex))

        if not res:
            raise NotFoundError
        elif len(res) > 1:
            raise DoubleFoundError

        return self.domain_model.model_validate(res[0])


class ListMixin(BaseSQLAlchemyRepo[TDomain, TOrm], Generic[TDomain, TOrm]):
    async def list(
        self,
        filters: Optional[dict[str, Any]] = None,
        order_columns: Optional[list[Any]] = None,
    ) -> Sequence[TDomain]:
        stmt = select(self.orm_class)
        if filters:
            stmt = stmt.filter_by(**filters)
        if order_columns:
            stmt = stmt.order_by(*order_columns)
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [self.domain_model.model_validate(row) for row in rows]


class UpdateMixin(BaseSQLAlchemyRepo[TDomain, TOrm], Generic[TDomain, TOrm]):
    async def update(self, data: dict[str, Any], filters: Optional[dict[str, Any]] = None) -> Sequence[TDomain]:
        stmt = select(self.orm_class)
        if filters:
            stmt = stmt.filter_by(**filters)
        try:
            records = (await self.db.execute(stmt)).scalars().all()
        except Exception as ex:
            raise RepositoryException(str(ex))
        if not records:
            return []

        updated_records = []
        for record in records:
            for key, value in data.items():
                setattr(record, key, value)
            updated_records.append(self.domain_model.model_validate(record))

        return updated_records


class DeleteMixin(BaseSQLAlchemyRepo[TDomain, TOrm], Generic[TDomain, TOrm]):
    async def delete(self, filters: dict[str, Any]) -> int:
        stmt = select(self.orm_class)
        if filters:
            stmt = stmt.filter_by(**filters)
        try:
            records = (await self.db.execute(stmt)).scalars().all()
        except Exception as ex:
            raise RepositoryException(str(ex))

        if not records:
            return 0

        for record in records:
            await self.db.delete(record)

        return len(records)


class CountMixin(BaseSQLAlchemyRepo[TDomain, TOrm], Generic[TDomain, TOrm]):
    async def count(self, filters: Optional[dict[str, Any]] = None) -> int:
        stmt = select(self.orm_class)
        if filters:
            stmt = stmt.filter_by(**filters)
        try:
            res = (await self.db.execute(stmt)).scalars().all()
        except Exception as ex:
            raise RepositoryException(str(ex))

        return len(res)
