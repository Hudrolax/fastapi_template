from repositories.user_repo import IUserRepoProtocol
from domain.domain_user import DomainUser
from domain.exceptions import DoubleFoundError, NotFoundError
from util.crypto_hash import AbstractCrypto


class UserService:
    repository: IUserRepoProtocol
    wrong_password_ex = NotFoundError('Wrong password or username')

    def __init__(self, repository: IUserRepoProtocol, crypto_hash: AbstractCrypto) -> None:
        self.repository = repository
        self.crypto_hash = crypto_hash

    async def create(self, data: dict) -> DomainUser:
        """
        Asynchronously creates a new user in the repository.

        This function takes a dictionary containing user data, checks if a user with the given username
        already exists, and if not, hashes the provided password and creates a new user entry in the repository.

        Args:
            data (dict): A dictionary containing user information. Expected keys are:
                - "username": The username of the user to be created.
                - "password": The plaintext password of the user to be hashed and stored.

        Returns:
            DomainUser: An instance of the DomainUser class representing the newly created user.

        Raises:
            DoubleFoundError: If a user with the specified username already exists in the repository.
        """
        username = data["username"]
        if await self.repository.exists(username=username):
            raise DoubleFoundError(f'user with username {username} already exists.')

        password = data["password"]
        hashed_password = self.crypto_hash.hash(password)
        return await self.repository.create(data={"username": username, "hashed_password": hashed_password})

    async def verify_password(self, username: str, password: str) -> DomainUser:
        """
        Verifies the provided password for a given username.

        Args:
            username (str): The username of the user whose password needs to be verified.
            password (str): The password to verify against the stored hashed password.

        Returns:
            DomainUser: The user object if the password is verified successfully.

        Raises:
            self.wrong_password_ex: If the password verification fails.
        """
        user = await self.repository.read(filters={"username": username})
        if self.crypto_hash.verify(password, user.hashed_password):
            return user
        else:
            raise self.wrong_password_ex

    async def update_password(self, username: str, old_password: str, new_password: str) -> DomainUser:
        """
        Updates the password for a given user if the old password is verified.

        Args:
            username (str): The username of the user whose password is to be updated.
            old_password (str): The current password of the user.
            new_password (str): The new password to be set for the user.

        Returns:
            DomainUser: The updated user object with the new password.

        Raises:
            DoubleFoundError: If more than one user with the same username is found in the database.
            Exception: If the old password does not match the current password.
        """
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
