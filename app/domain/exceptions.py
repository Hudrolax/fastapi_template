class DomainException(Exception):
    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.message = message


class RepositoryException(DomainException):
    pass


class NotFoundError(RepositoryException):
    pass


class DoubleFoundError(RepositoryException):
    pass
