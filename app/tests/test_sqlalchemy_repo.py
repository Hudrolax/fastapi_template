import pytest

from sqlalchemy import Integer, String, select, delete
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from conftest import Base
from repositories.sqlalchemy_repo import CreateMixin, ReadMixin, ListMixin, UpdateMixin, DeleteMixin, CountMixin
from domain.exceptions import NotFoundError, DoubleFoundError
from domain.base_domain_model import BaseDomainModel

# Определяем фиктивную ORM-модель, используя Base из conftest.py,
# чтобы таблица создавалась автоматически в in-memory БД.
class DummyORM(Base):
    __tablename__ = "dummy"
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:Mapped[str] = mapped_column(String)

# Фиктивная доменная модель с методом model_validate, используемая миксинами.
class DummyDomain(BaseDomainModel):
    id: int
    name: str


# Создаем репозиторий, комбинирующий все миксины.
class DummyRepo(
    CreateMixin[DummyDomain, DummyORM],
    ReadMixin[DummyDomain, DummyORM],
    ListMixin[DummyDomain, DummyORM],
    UpdateMixin[DummyDomain, DummyORM],
    DeleteMixin[DummyDomain, DummyORM],
    CountMixin[DummyDomain, DummyORM],
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DummyDomain, DummyORM)

# Вспомогательная функция для очистки таблицы перед каждым тестом.
async def clear_table(session: AsyncSession):
    await session.execute(delete(DummyORM))
    await session.commit()

@pytest.mark.asyncio
async def test_create(async_session: AsyncSession):
    await clear_table(async_session)
    repo = DummyRepo(async_session)
    data = {"name": "test_create"}
    domain_obj = await repo.create(data)
    assert domain_obj.name == "test_create"

    # Проверка через прямой запрос к базе
    result = await async_session.execute(
        select(DummyORM).where(DummyORM.name == "test_create")
    )
    orm_obj = result.scalar_one()
    assert orm_obj.name == "test_create"

@pytest.mark.asyncio
async def test_read(async_session: AsyncSession):
    await clear_table(async_session)
    repo = DummyRepo(async_session)

    # Создаем запись и затем читаем её
    await repo.create({"name": "test_read"})
    read_obj = await repo.read(filters={"name": "test_read"})
    assert read_obj.name == "test_read"

    # Если запись не найдена, должно выброситься исключение NotFoundError
    with pytest.raises(NotFoundError):
        await repo.read(filters={"name": "nonexistent"})

    # Проверка DoubleFoundError — создаем две записи с одинаковым именем
    await repo.create({"name": "duplicate"})
    await repo.create({"name": "duplicate"})
    with pytest.raises(DoubleFoundError):
        await repo.read(filters={"name": "duplicate"})

@pytest.mark.asyncio
async def test_list(async_session: AsyncSession):
    await clear_table(async_session)
    repo = DummyRepo(async_session)
    names = ["Alice", "Bob", "Charlie"]
    for name in names:
        await repo.create({"name": name})
    # Получаем список объектов, упорядоченных по имени
    domain_list = await repo.list(filters={}, order_columns=[DummyORM.name])
    listed_names = [d.name for d in domain_list]
    assert listed_names == sorted(names)

@pytest.mark.asyncio
async def test_update(async_session: AsyncSession):
    await clear_table(async_session)
    repo = DummyRepo(async_session)
    # Создаем запись
    domain_obj = await repo.create({"name": "old_name"})
    # Обновляем запись
    updated_objs = await repo.update({"name": "new_name"}, filters={"id": domain_obj.id})
    assert len(updated_objs) == 1
    assert updated_objs[0].name == "new_name"

    # Проверяем, что обновление применилось (чтением из базы)
    read_obj = await repo.read(filters={"id": domain_obj.id})
    assert read_obj.name == "new_name"

@pytest.mark.asyncio
async def test_delete(async_session: AsyncSession):
    await clear_table(async_session)
    repo = DummyRepo(async_session)
    # Создаем две записи
    await repo.create({"name": "to_delete"})
    await repo.create({"name": "to_keep"})

    # Удаляем запись с именем "to_delete"
    deleted_count = await repo.delete(filters={"name": "to_delete"})
    assert deleted_count == 1

    # Проверяем, что удаленная запись не находится
    with pytest.raises(NotFoundError):
        await repo.read(filters={"name": "to_delete"})

    # Остальная запись должна присутствовать
    remaining_obj = await repo.read(filters={"name": "to_keep"})
    assert remaining_obj.name == "to_keep"

@pytest.mark.asyncio
async def test_count(async_session: AsyncSession):
    await clear_table(async_session)
    repo = DummyRepo(async_session)

    # Создаем запись и затем читаем её
    await repo.create({"name": "first"})
    await repo.create({"name": "second"})
    count = await repo.count(filters={"name": "first"})
    assert count == 1

    count_zero = await repo.count(filters={"name": "nonexistent"})
    assert count_zero == 0

    count2 = await repo.count()
    assert count2 == 2
