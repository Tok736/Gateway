from pydantic import BaseModel, EmailStr, Field, SecretStr

from .enums import BasicRole

# fmt: off


class UserRead(BaseModel):
    id:              int
    email:           str
    is_active:       bool


class RegisterRequest(BaseModel):
    email:           EmailStr
    password:        SecretStr = Field(min_length=8, max_length=128)
    nickname:        str
    basic_role:      BasicRole

# fmt: on
