from typing import Type, Generic, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from .interfaces import AbstractRepository
from domain.base_domain_model import TDomain
from domain.exceptions import DoubleFoundError, NotFoundError, RepositoryException
from db.models.base_model import BaseORMModel


class SQLAlchemyRepository(Generic[TDomain], AbstractRepository[TDomain]):
    """
    Реализация репозитория для SQLAlchemy. Принимает сессию, ORM класс и доменную модель.
    Реализует универсальную обработку CRUD + list операций
    """

    def __init__(
        self,
        db: AsyncSession,
        orm_class: Type[BaseORMModel],
        domain_model: Type[TDomain],
    ) -> None:
        self.db: AsyncSession = db
        self.orm_class = orm_class
        self.domain_model = domain_model

    async def create(self, data: dict) -> TDomain:
        """
        Asynchronously creates a new record in the database.

        Args:
            data (dict): A dictionary containing the data for the new record.

        Returns:
            TDomain: The domain model instance of the created record.

        Raises:
            DoubleFoundError: If a duplicate entry is found in the database.
            RepositoryException: If any other database error occurs.
        """
        stmt = insert(self.orm_class).values(**data).returning(self.orm_class)
        try:
            res = (await self.db.execute(stmt)).scalar_one()
        except Exception as ex:
            if "duplicate" in str(ex).lower():
                raise DoubleFoundError("Duplicate entry found")
            raise RepositoryException(str(ex))
        return self.domain_model.model_validate(res)

    async def read(self, filters: Optional[dict] = None) -> TDomain:
        """
        Reads data from the database using the specified filters.

        Args:
            filters (Optional[dict]): A dictionary of filters to apply to the query.

        Returns:
            TDomain: The domain model instance corresponding to the query result.

        Raises:
            NotFoundError: If no records are found.
            DoubleFoundError: If more than one record is found.
        """
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

    async def list(self, filters: Optional[dict] = None, order_columns: Optional[list] = None) -> List[TDomain]:
        """
        Asynchronously retrieves a list of domain objects based on provided filters and order columns.

        Args:
            filters (Optional[dict]): A dictionary of filters to apply to the query.
            order_columns (Optional[list]): A list of columns to order the results by.

        Returns:
            List[TDomain]: A list of domain objects.

        Raises:
            RepositoryException: If there is an error executing the database query.
        """

        stmt = select(self.orm_class)
        if filters:
            stmt = stmt.filter_by(**filters)
        if order_columns:
            stmt = stmt.order_by(*order_columns)
        try:
            res = (await self.db.execute(stmt)).scalars().all()
        except Exception as ex:
            raise RepositoryException(str(ex))
        return [self.domain_model.model_validate(item) for item in res]

    async def update(self, filters: Optional[dict], data: dict) -> List[TDomain]:
        """
        Updates records in the database based on the provided filters and data.

        Args:
            filters (Optional[dict]): A dictionary of filters to apply to the query.
            data (dict): A dictionary of data to update the records with.

        Returns:
            List[TDomain]: A list of updated domain model instances.

        Raises:
            RepositoryException: If an error occurs during the database operation.
        """
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

    async def delete(self, filters: Optional[dict]) -> int:
        """
        Deletes records from the database based on the provided filters.

        Args:
            filters (Optional[dict]): A dictionary of filters to apply to the query.

        Returns:
            int: The number of records deleted.

        Raises:
            RepositoryException: If an error occurs during the database operation.
        """
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
