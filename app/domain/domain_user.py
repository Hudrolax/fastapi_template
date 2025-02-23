from .base_domain_model import BaseDomainModel


class DomainUser(BaseDomainModel):
    id: int
    username: str
    hashed_password: str
