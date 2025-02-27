import pytest

from sqlalchemy import Integer, String, select, delete
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from conftest import Base
from repositories.user_repo import UserSQLAlchemyRepo
from domain.exceptions import NotFoundError, DoubleFoundError
from domain.base_domain_model import BaseDomainModel

# Определяем фиктивную ORM-модель, используя Base из conftest.py,
# чтобы таблица создавалась автоматически в in-memory БД.
class DummyUserORM(Base):
    __tablename__ = "dummy_user"
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username:Mapped[str] = mapped_column(String)

# Фиктивная доменная модель с методом model_validate, используемая миксинами.
class DummyDomainUser(BaseDomainModel):
    id: int
    username: str


# Создаем репозиторий, комбинирующий все миксины.
class DummyUserRepo(
    UserSQLAlchemyRepo[DummyDomainUser, DummyUserORM]
):
    def __init__(self, db: AsyncSession):
        super().__init__(db, DummyDomainUser, DummyUserORM)

# Вспомогательная функция для очистки таблицы перед каждым тестом.
async def clear_table(session: AsyncSession):
    await session.execute(delete(DummyUserORM))
    await session.commit()

@pytest.mark.asyncio
async def test_exists(async_session: AsyncSession):
    await clear_table(async_session)
    repo = DummyUserRepo(async_session)
    data = {"username": "test"}
    await repo.create(data)

    exists = await repo.exists(username='fake_user')
    assert exists == False
    exists = await repo.exists(username='test')
    assert exists == True

