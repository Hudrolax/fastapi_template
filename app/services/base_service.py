from abc import ABC, abstractmethod
from typing import Generic, Optional, List
from domain.base_domain_model import TDomain
from repositories.interfaces import TRepo


class AbstractService(ABC, Generic[TDomain]):
    @abstractmethod
    async def create(self, data: dict) -> TDomain:
        pass

    @abstractmethod
    async def read(self, filters: Optional[dict]) -> TDomain:
        pass

    @abstractmethod
    async def list(self, filters: Optional[dict], order_columns: Optional[list]) -> List[TDomain]:
        pass

    @abstractmethod
    async def update(self, filters: Optional[dict], data: dict) -> List[TDomain]:
        pass

    @abstractmethod
    async def delete(self, filters: Optional[dict]) -> int:
        pass


class CRUDService(AbstractService[TDomain], Generic[TRepo, TDomain]):
    def __init__(self, repository: TRepo) -> None:
        self.repository: TRepo = repository

    async def create(self, data: dict) -> TDomain:
        return await self.repository.create(data=data)

    async def read(self, filters: Optional[dict]) -> TDomain:
        return await self.repository.read(filters=filters)

    async def list(self, filters: Optional[dict], order_columns: Optional[list]) -> List[TDomain]:
        return await self.repository.list(filters=filters, order_columns=order_columns)

    async def update(self, filters: Optional[dict], data: dict) -> List[TDomain]:
        return await self.repository.update(filters=filters, data=data)

    async def delete(self, filters: Optional[dict]) -> int:
        return await self.repository.delete(filters=filters)
