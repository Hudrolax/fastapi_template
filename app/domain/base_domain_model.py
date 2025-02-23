from pydantic import BaseModel, ConfigDict
from typing import TypeVar
from abc import ABC

class BaseDomainModel(BaseModel, ABC):
    model_config = ConfigDict(from_attributes=True)


TDomain = TypeVar("TDomain", bound=BaseDomainModel)

