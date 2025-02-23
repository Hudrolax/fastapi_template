from repositories.interfaces import AbstractRepository
from .base_service import CRUDService
from domain.domain_user import DomainUser
from domain.exceptions import DoubleFoundError, NotFoundError
from util.crypto_hash import AbstractCrypto


class UserService(CRUDService):
    repository: AbstractRepository
    wrong_password_ex = NotFoundError('Wrong password or username')

    def __init__(self, repository: AbstractRepository, crypto_hash: AbstractCrypto) -> None:
        self.crypto_hash = crypto_hash
        super().__init__(repository)

    async def create(self, data: dict) -> DomainUser:
        username = data["username"]
        password = data["password"]
        try:
            await self.repository.read(filters={"username": username})
            raise DoubleFoundError
        except NotFoundError:
            hashed_password = self.crypto_hash.hash(password)
            return await self.repository.create(data={"username": username, "hashed_password": hashed_password})

    async def verify_password(self, username: str, password: str) -> DomainUser:
        user = await self.repository.read(filters={"username": username})
        if self.crypto_hash.verify(password, user.hashed_password):
            return user
        else:
            raise self.wrong_password_ex

    async def update_password(self, username: str, old_password: str, new_password: str) -> DomainUser:
        user = await self.repository.read(filters={"username": username})
        if self.crypto_hash.verify(old_password, user.hashed_password):
            hashed_password = self.crypto_hash.hash(new_password)
            updated_users = await self.repository.update(
                filters={'username': username},
                data={'hashed_password': hashed_password}
            )
            if len(updated_users) == 1:
                return updated_users[0]
            else:
                raise DoubleFoundError(f'username {username} has a double in DB!')
        else:
            raise self.wrong_password_ex
