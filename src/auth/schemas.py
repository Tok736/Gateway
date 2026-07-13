from pydantic import BaseModel, EmailStr, Field, SecretStr, field_serializer

from .enums import BasicRole

# fmt: off


class AuthResponse(BaseModel):
    token_type:      str = "Bearer"
    expires_at:      int


class RegisterRequest(BaseModel):
    email:           EmailStr
    password:        SecretStr = Field(min_length=8, max_length=128)
    nickname:        str
    basic_role:      BasicRole

    @field_serializer("password", when_used='always')
    def dump_password_plain(self, value: SecretStr) -> str:
        return value.get_secret_value()


class LoginRequest(BaseModel):
    email:           EmailStr
    password:        SecretStr = Field(min_length=1, max_length=128)

    @field_serializer("password", when_used='always')
    def dump_password_plain(self, value: SecretStr) -> str:
        return value.get_secret_value()


class TokenPair(BaseModel):
    access_token:    str
    refresh_token:   str
    token_type:      str = "Bearer"
    expires_at:      int


class RevokeRequest(BaseModel):
    refresh_token:   str
    all_sessions:    bool = False


class LogoutRequest(BaseModel):
    all_sessions:    bool = False


# fmt: on
