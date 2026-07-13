from fastapi import APIRouter, Request, Response

from src.rabbit import RabbitRPCResponse, rpc_handler

from .constants import REFRESH_COOKIE_NAME
from .schemas import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    RegisterRequest,
    RevokeRequest,
    TokenPair,
)
from .utils import clear_auth_cookies, set_auth_cookies

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(request: RegisterRequest, response: Response) -> AuthResponse:
    """Зарегистрировать пользователя. Возвращаются access и refresh токены в http-only куках"""

    tokens = await rpc_handler(
        request,
        "auth_consumer.POST.register",
        RabbitRPCResponse[TokenPair],
        "Auth service",
        timeout=10,
    )

    set_auth_cookies(response, tokens)

    return AuthResponse(token_type=tokens.token_type, expires_at=tokens.expires_at)


@router.post("/login")
async def login(request: LoginRequest, response: Response) -> AuthResponse:
    """Авторизоваться, используя логин и пароль. Возвращаются access и refresh токены в http-only куках"""

    tokens = await rpc_handler(
        request,
        "auth_consumer.POST.login",
        RabbitRPCResponse[TokenPair],
        "Auth service",
        timeout=5,
    )

    set_auth_cookies(response, tokens)

    return AuthResponse(token_type=tokens.token_type, expires_at=tokens.expires_at)


@router.post("/logout")
async def logout(
    logout_request: LogoutRequest, request: Request, response: Response
) -> None:
    """Выйти: отозвать refresh-токен и очистить куки."""

    clear_auth_cookies(response)

    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)

    if refresh_token:
        revoke_request = RevokeRequest(
            refresh_token=refresh_token,
            all_sessions=logout_request.all_sessions,
        )

        await rpc_handler(
            revoke_request,
            "auth_consumer.POST.revoke",
            RabbitRPCResponse,
            "Auth service",
            timeout=5,
            data_expected=False,
            raise_http_error=False,
        )
