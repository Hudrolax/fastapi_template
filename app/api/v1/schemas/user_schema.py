from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserToken(UserRead):
    token: str

class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str
