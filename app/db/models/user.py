from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from passlib.context import CryptContext
from .base_model import BaseORMModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserORM(BaseORMModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
