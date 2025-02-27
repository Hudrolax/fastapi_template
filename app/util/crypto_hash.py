from abc import ABC, abstractmethod

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AbstractCrypto(ABC):
    @abstractmethod
    def hash(self, value: str) -> str:
        """return hashed value"""
        ...

    @abstractmethod
    def verify(self, value: str, hash: str) -> bool: ...


class CryptoHash(AbstractCrypto):

    def hash(self, value: str) -> str:
        """return hashed value"""
        return pwd_context.hash(value)

    def verify(self, value: str, hash: str) -> bool:
        return pwd_context.verify(value, hash)
