import pytest
from unittest.mock import AsyncMock, Mock
from domain.domain_user import DomainUser
from domain.exceptions import DoubleFoundError, NotFoundError
from services.user_service import UserService
from util.crypto_hash import AbstractCrypto

@pytest.mark.asyncio
async def test_create_success():
    # Мокаем репозиторий:
    repo = AsyncMock()
    # При попытке прочитать пользователя генерируем NotFoundError,
    # что означает — пользователь с таким именем отсутствует.
    repo.read = AsyncMock(side_effect=NotFoundError("User not found"))
    # При создании пользователя репозиторий возвращает объект DomainUser.
    created_user = DomainUser(id=1, username="test", hashed_password="fake_hashed_password")
    repo.create = AsyncMock(return_value=created_user)

    # Создаем сервис, передавая в него мокаемый репозиторий.
    service = UserService(repository=repo, crypto_hash=Mock())

    input_data = {"username": "test", "password": "secret"}
    result = await service.create(data=input_data)

    # Проверяем, что метод read был вызван с нужным аргументом.
    repo.read.assert_called_once_with(filters={'username':"test"})
    # Проверяем, что метод create был вызван.
    repo.create.assert_called_once()
    # Результат должен быть объектом DomainUser с корректными данными.
    assert isinstance(result, DomainUser)
    assert result.username == "test"
    # Хешированный пароль должен отличаться от исходного.
    assert result.hashed_password != "secret"
    assert isinstance(result.hashed_password, str)

@pytest.mark.asyncio
async def test_create_double_found():
    # Мокаем репозиторий:
    repo = AsyncMock()
    # Симулируем, что пользователь с таким именем уже существует.
    existing_user = DomainUser(id=1, username="test", hashed_password="existing_hash")
    repo.read = AsyncMock(return_value=existing_user)
    # Метод create в этом случае не должен вызываться.
    repo.create = AsyncMock()

    service = UserService(repository=repo, crypto_hash=Mock())

    input_data = {"username": "test", "password": "secret"}
    # Ожидаем, что при попытке создать пользователя с уже существующим именем
    # будет выброшено исключение DoubleFoundError.
    with pytest.raises(DoubleFoundError):
         await service.create(data=input_data)

    repo.read.assert_called_once_with(filters={'username':"test"})
    repo.create.assert_not_called()

@pytest.mark.asyncio
async def test_verify_password_success():
    crypto_hash: AbstractCrypto = Mock()
    crypto_hash.hash = Mock(return_value='hashed_password')
    crypto_hash.verify = Mock(return_value=True)

    # Подготавливаем тестового пользователя с корректным хешированным паролем.
    password = "secret"
    hashed = crypto_hash.hash(password)
    user = DomainUser(id=1, username="test", hashed_password=hashed)
    
    # Мокаем репозиторий: метод read возвращает тестового пользователя.
    repo = AsyncMock()
    repo.read = AsyncMock(return_value=user)
    
    service = UserService(repository=repo, crypto_hash=crypto_hash)
    
    result = await service.verify_password(username="test", password=password)
    
    repo.read.assert_called_once_with(filters={'username': "test"})
    assert result == user

@pytest.mark.asyncio
async def test_verify_password_wrong_password():
    # Мокаем crypto_hash, чтобы verify возвращал False.
    crypto_hash = Mock()
    crypto_hash.verify = Mock(return_value=False)
    crypto_hash.hash = Mock(return_value='hashed_password')

    # Подготавливаем пользователя с хешированным паролем.
    user = DomainUser(id=1, username="test", hashed_password="hashed_password")
    
    repo = AsyncMock()
    repo.read = AsyncMock(return_value=user)
    
    service = UserService(repository=repo, crypto_hash=crypto_hash)
    
    # При неверном пароле должно быть выброшено исключение NotFoundError.
    with pytest.raises(NotFoundError):
        await service.verify_password(username="test", password="wrong_password")
    
    repo.read.assert_called_once_with(filters={'username': "test"})

@pytest.mark.asyncio
async def test_update_password_success():
    # Мокаем crypto_hash, чтобы verify возвращал True и hash возвращал новый хеш.
    crypto_hash = Mock()
    crypto_hash.verify = Mock(return_value=True)
    crypto_hash.hash = Mock(return_value="new_hashed_password")

    old_password = "oldsecret"
    new_password = "newsecret"
    user = DomainUser(id=1, username="test", hashed_password="old_hashed_password")
    
    repo = AsyncMock()
    repo.read = AsyncMock(return_value=user)
    # Метод update возвращает список с одним обновлённым пользователем.
    updated_user = DomainUser(id=1, username="test", hashed_password="new_hashed_password")
    repo.update = AsyncMock(return_value=[updated_user])
    
    service = UserService(repository=repo, crypto_hash=crypto_hash)
    
    result = await service.update_password("test", old_password, new_password)
    
    repo.read.assert_called_once_with(filters={'username': "test"})
    repo.update.assert_called_once_with(filters={'username': "test"}, data={'hashed_password': "new_hashed_password"})
    assert result == updated_user

@pytest.mark.asyncio
async def test_update_password_wrong_old_password():
    # Мокаем crypto_hash, чтобы verify возвращал False для старого пароля.
    crypto_hash = Mock()
    crypto_hash.verify = Mock(return_value=False)
    crypto_hash.hash = Mock(return_value="new_hashed_password")

    old_password = "oldsecret"
    new_password = "newsecret"
    user = DomainUser(id=1, username="test", hashed_password="old_hashed_password")
    
    repo = AsyncMock()
    repo.read = AsyncMock(return_value=user)
    
    service = UserService(repository=repo, crypto_hash=crypto_hash)
    
    with pytest.raises(NotFoundError):
        await service.update_password("test", old_password, new_password)
    
    repo.read.assert_called_once_with(filters={'username': "test"})

@pytest.mark.asyncio
async def test_update_password_double_found():
    # Мокаем crypto_hash, чтобы verify возвращал True.
    crypto_hash = Mock()
    crypto_hash.verify = Mock(return_value=True)
    crypto_hash.hash = Mock(return_value="new_hashed_password")

    old_password = "oldsecret"
    new_password = "newsecret"
    user = DomainUser(id=1, username="test", hashed_password="old_hashed_password")
    
    repo = AsyncMock()
    repo.read = AsyncMock(return_value=user)
    # Симулируем ситуацию, когда update возвращает более одного пользователя.
    updated_user1 = DomainUser(id=1, username="test", hashed_password="new_hashed_password")
    updated_user2 = DomainUser(id=2, username="test", hashed_password="new_hashed_password")
    repo.update = AsyncMock(return_value=[updated_user1, updated_user2])
    
    service = UserService(repository=repo, crypto_hash=crypto_hash)
    
    with pytest.raises(DoubleFoundError):
        await service.update_password("test", old_password, new_password)
    
    repo.read.assert_called_once_with(filters={'username': "test"})
    repo.update.assert_called_once_with(filters={'username': "test"}, data={'hashed_password': "new_hashed_password"})
