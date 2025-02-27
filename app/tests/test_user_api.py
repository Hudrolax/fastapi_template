from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from domain.domain_user import DomainUser
from domain.exceptions import DoubleFoundError, NotFoundError, RepositoryException
from api.auth import check_token
from services.user_service import UserService
from api.v1 import user_router

# Фиктивная реализация UserService для тестирования роутера
class FakeUserService():
    async def create(self, data: dict) -> DomainUser:
        # Если имя пользователя "exists", симулируем наличие такого пользователя
        if data["username"] == "exists":
            raise DoubleFoundError('already exists')
        # Иначе возвращаем созданного пользователя
        return DomainUser(id=1, username=data["username"], hashed_password="fake_hashed")

    async def verify_password(self, username: str, password: str) -> DomainUser:
        # Если имя "notfound", симулируем ошибку репозитория
        if username == "notfound":
            raise RepositoryException("User not found")
        # Если пароль неверный, генерируем NotFoundError
        if password != "secret":
            raise NotFoundError("Wrong password")
        return DomainUser(id=1, username=username, hashed_password="fake_hashed")

    async def update_password(self, username: str, old_password: str, new_password: str) -> DomainUser:
        # Если старый пароль неверный, генерируем RepositoryException
        if old_password != "oldsecret":
            raise RepositoryException("Wrong old password")
        # Иначе возвращаем пользователя с обновленным хешем
        return DomainUser(id=1, username=username, hashed_password="new_fake_hashed")

# Создаем приложение FastAPI и подключаем роутер
app = FastAPI()
app.include_router(user_router.router)

# Переопределяем зависимость get_user_service для использования фиктивного сервиса
def override_get_user_service() -> UserService:
    return cast(UserService, FakeUserService())

app.dependency_overrides[user_router.get_user_service] = override_get_user_service

# Переопределяем зависимость check_token, чтобы она возвращала тестового пользователя
async def fake_check_token() -> DomainUser:
    return DomainUser(id=1, username="test", hashed_password="fake_hashed")

app.dependency_overrides[check_token] = fake_check_token

client = TestClient(app)

def test_create_user_success():
    payload = {"username": "newuser", "password": "secret"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data

def test_create_user_double_found():
    payload = {"username": "exists", "password": "secret"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 422
    assert "already exists" in response.text

def test_login_success():
    payload = {"username": "test", "password": "secret"}
    response = client.post("/users/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test"
    # Проверяем, что в ответе есть токен
    assert "token" in data

def test_login_wrong_password():
    payload = {"username": "test", "password": "wrong"}
    response = client.post("/users/login", json=payload)
    assert response.status_code == 422

def test_read_user_success():
    # Поскольку fake_check_token всегда возвращает пользователя с id=1, запрос с id=1 должен пройти успешно.
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1

def test_read_user_wrong_id():
    # Если запрашиваем id, отличный от id тестового пользователя, роутер должен вернуть ошибку.
    response = client.get("/users/2")
    assert response.status_code == 422
    assert "Wrong user id" in response.text

def test_update_password_success():
    payload = {"old_password": "oldsecret", "new_password": "newsecret"}
    # check_token вернет пользователя с username "test"
    response = client.post("/users/update_password", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test"

def test_update_password_wrong_old_password():
    payload = {"old_password": "wrong", "new_password": "newsecret"}
    response = client.post("/users/update_password", json=payload)
    # В случае неверного старого пароля FakeUserService генерирует RepositoryException,
    # который роутер обрабатывает и возвращает 422.
    assert response.status_code == 422
    assert "Wrong old password" in response.text
