import pytest
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from repositories.sqlalchemy_repo import SQLAlchemyRepository
from domain.exceptions import NotFoundError
from domain.base_domain_model import BaseDomainModel
from conftest import Base


# ORM-модель для тестирования
class DummyORM(Base):
    __tablename__ = "dummy"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

# Доменная модель для тестирования
class DummyDomain(BaseDomainModel):
    id: int
    name: str

# Фикстура для создания репозитория
@pytest.fixture
def repository(async_session):
    repo = SQLAlchemyRepository(
        db=async_session,
        orm_class=DummyORM,
        domain_model=DummyDomain,
    )
    return repo

@pytest.mark.asyncio
async def test_create_and_read(repository, async_session):
    data = {"name": "Test Name"}
    # Создание записи
    created = await repository.create(data)
    await async_session.commit()

    # Чтение записи по фильтру
    read_obj = await repository.read(filters={"name": "Test Name"})
    assert read_obj.name == "Test Name"
    assert read_obj.id == created.id

@pytest.mark.asyncio
async def test_list(repository, async_session):
    # Добавляем новую запись
    data = {"name": "List Test"}
    await repository.create(data)
    await async_session.commit()

    # Получаем список записей по фильтру
    items = await repository.list(filters={"name": "List Test"})
    assert isinstance(items, list)
    assert len(items) >= 1
    for item in items:
        assert item.name == "List Test"

@pytest.mark.asyncio
async def test_update(repository, async_session):
    # Создаем запись
    data = {"name": "Update Test"}
    created = await repository.create(data)
    await async_session.commit()

    # Обновляем запись
    updated_list = await repository.update(filters={"id": created.id}, data={"name": "Updated Name"})
    await async_session.commit()
    assert len(updated_list) == 1
    updated = updated_list[0]
    assert updated.name == "Updated Name"

    # Проверяем обновление через read
    read_obj = await repository.read(filters={"id": created.id})
    assert read_obj.name == "Updated Name"

@pytest.mark.asyncio
async def test_delete(repository, async_session):
    # Создаем запись
    data = {"name": "Delete Test"}
    created = await repository.create(data)
    await async_session.commit()

    # Удаляем запись
    count_deleted = await repository.delete(filters={"id": created.id})
    await async_session.commit()
    assert count_deleted == 1

    # Проверяем, что запись удалена
    with pytest.raises(NotFoundError):
        await repository.read(filters={"id": created.id})
