from typing import Annotated
from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError

from services.user_service import UserService

from .dependencies import get_user_service
from domain.domain_user import DomainUser
from domain.exceptions import RepositoryException
from config import SECRET


api_key_header = APIKeyHeader(name="TOKEN", auto_error=False)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 356 * 99


def create_jwt_token(
    data: dict,
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
):
    """Create new JWT token"""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str) -> tuple[str, str]:
    """Verify JWT token

    Args:
        token (str): token

    Returns:
        tupe[str, str]: username, password
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str | None = payload.get("username")
        password: str | None = payload.get("password")
        if username is None or password is None:
            raise credentials_exception

        expiration = payload.get("exp")
        if expiration is not None and datetime.fromtimestamp(
            expiration, UTC
        ) < datetime.now(UTC):
            raise HTTPException(status_code=401, detail="Token is expired")
        return username, password
    except (JWTError, AttributeError):
        raise credentials_exception


# authentication
async def check_token(
    service: Annotated[UserService, Depends(get_user_service)],
    JWT_token: str = Security(api_key_header),
) -> DomainUser:
    """Check token in the Headers and return a user or raise 401 exception"""
    try:
        username, password = verify_jwt_token(JWT_token)
        return await service.verify_password(username, password)
    except RepositoryException:
        raise HTTPException(401)

