from typing import Generic, Optional, Protocol, Any, Sequence

from domain.base_domain_model import TDomain


class ICreateRepository(Protocol, Generic[TDomain]):
    async def create(self, data: dict[str, Any]) -> TDomain:
        """
        Asynchronously creates a new record in the repository.

        Args:
            data (dict): A dictionary containing the data for the new record.

        Returns:
            TDomain: The domain model instance of the created record.

        Raises:
            DoubleFoundError: If a duplicate entry is found in the repository.
            RepositoryException: If any other repository error occurs.
        """
        ...


class IReadRepository(Protocol, Generic[TDomain]):
    async def read(self, filters: Optional[dict[str, Any]] = None) -> TDomain:
        """
        Reads data using the specified filters.

        Args:
            filters (Optional[dict]): A dictionary of filters

        Returns:
            TDomain: The domain model instance corresponding to the query result.

        Raises:
            NotFoundError: If no records are found.
            DoubleFoundError: If more than one record is found.
        """
        ...


class IListRepository(Protocol, Generic[TDomain]):
    async def list(
        self, filters: Optional[dict[str, Any]] = None, order_columns: Optional[list[Any]] = None
    ) -> Sequence[TDomain]:
        """
        Asynchronously retrieves a list of domain objects based on provided filters and order columns.

        Args:
            filters (Optional[dict]): A dictionary of filters to apply to the query.
            order_columns (Optional[list]): A list of columns to order the results by.

        Returns:
            List[TDomain]: A list of domain objects.

        Raises:
            SQLAlchemyError: If there is an error executing the repository query.
            ValidationError: If there is an error validating the domain model.
        """
        ...


class IUpdateRepository(Protocol, Generic[TDomain]):
    async def update(self, data: dict[str, Any], filters: Optional[dict[str, Any]] = None) -> Sequence[TDomain]:
        """
        Updates records in the repository based on the provided filters and data.

        Args:
            filters (Optional[dict]): A dictionary of filters to apply to the query.
            data (dict): A dictionary of data to update the records with.

        Returns:
            List[TDomain]: A list of updated domain model instances.

        Raises:
            RepositoryException: If an error occurs during the repository operation.
        """
        ...


class IDeleteRepository(Protocol, Generic[TDomain]):
    async def delete(self, filters: dict[str, Any]) -> int:
        """
        Deletes records from the repository based on the provided filters.

        Args:
            filters (Optional[dict]): A dictionary of filters to apply to the query.

        Returns:
            int: The number of records deleted.

        Raises:
            RepositoryException: If an error occurs during the repository operation.
        """
        ...


class ICountRepository(Protocol, Generic[TDomain]):
    async def count(self, filters: Optional[dict[str, Any]] = None) -> int:
        """
        Returns records count from the repository based on the provided filters.

        Args:
            filters (Optional[dict]): A dictionary of filters to apply to the query.

        Returns:
            int: The number of records.
        """
        ...
