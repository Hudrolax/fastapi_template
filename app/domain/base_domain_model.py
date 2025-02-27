from typing import TypeVar
from abc import ABC

from pydantic import BaseModel, ConfigDict


class BaseDomainModel(BaseModel, ABC):
    model_config = ConfigDict(from_attributes=True)


TDomain = TypeVar("TDomain", bound=BaseDomainModel, covariant=True)
