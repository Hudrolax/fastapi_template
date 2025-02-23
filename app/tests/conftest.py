import pytest
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool

Base = declarative_base()


# Фикстура для асинхронного движка с использованием StaticPool для in-memory SQLite
@pytest.fixture(scope="module")
async def async_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

# Фикстура для асинхронной сессии, корректно закрывающая сессию
@pytest.fixture
async def async_session(async_engine):
    async_session_factory = sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session_factory() as session:  # type: ignore
        yield session
