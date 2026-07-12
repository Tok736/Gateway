from pydantic import BaseModel, EmailStr, Field

# fmt: off


class UserRead(BaseModel):
    id:              int
    email:           str
    is_active:       bool


class RegisterRequest(BaseModel):
    email:           EmailStr
    password:        str = Field(min_length=8, max_length=128)


# fmt: on
