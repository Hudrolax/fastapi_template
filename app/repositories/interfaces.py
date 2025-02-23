from abc import ABC, abstractmethod
from domain.base_domain_model import  TDomain
from typing import TypeVar, Generic, List, Optional


class AbstractRepository(ABC, Generic[TDomain]):
    @abstractmethod
    async def create(self, data: dict) -> TDomain:
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
        pass

    @abstractmethod
    async def read(self, filters: Optional[dict]) -> TDomain:
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
        pass

    @abstractmethod
    async def list(self, filters: Optional[dict], order_columns: Optional[list]) -> List[TDomain]:
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
        pass

    @abstractmethod
    async def update(self, filters: Optional[dict], data: dict) -> List[TDomain]:
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
        pass

    @abstractmethod
    async def delete(self, filters: Optional[dict]) -> int:
        """
        Deletes records from the repository based on the provided filters.

        Args:
            filters (Optional[dict]): A dictionary of filters to apply to the query.

        Returns:
            int: The number of records deleted.

        Raises:
            RepositoryException: If an error occurs during the repository operation.
        """
        pass



TRepo = TypeVar("TRepo", bound=AbstractRepository)
