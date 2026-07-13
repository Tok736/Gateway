from fastapi import Response

from src.config import settings
from src.enums import Environment

from .constants import (
    ACCESS_COOKIE_NAME,
    ACCESS_COOKIE_PATH,
    REFRESH_COOKIE_NAME,
    REFRESH_COOKIE_PATH,
)
from .schemas import TokenPair


def set_auth_cookies(response: Response, tokens: TokenPair) -> None:
    """Записать access/refresh токены в http-only куки."""

    if settings.project.environment == Environment.prod:
        cookie_samesite = "strict"
        cookie_secure = True
    else:
        cookie_samesite = "lax"
        cookie_secure = False

    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=tokens.access_token,
        max_age=settings.auth.access_token_ttl,
        path=ACCESS_COOKIE_PATH,
        domain=settings.auth.cookie_domain,
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=tokens.refresh_token,
        max_age=settings.auth.refresh_token_ttl,
        path=REFRESH_COOKIE_PATH,
        domain=settings.auth.cookie_domain,
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
    )


def clear_auth_cookies(response: Response) -> None:
    """Удалить куки с токенами (для logout)."""

    if settings.project.environment == Environment.prod:
        cookie_samesite = "strict"
        cookie_secure = True
    else:
        cookie_samesite = "lax"
        cookie_secure = False

    for name, path in (
        (ACCESS_COOKIE_NAME, ACCESS_COOKIE_PATH),
        (REFRESH_COOKIE_NAME, REFRESH_COOKIE_PATH),
    ):
        response.delete_cookie(
            key=name,
            path=path,
            domain=settings.auth.cookie_domain,
            httponly=True,
            secure=cookie_secure,
            samesite=cookie_samesite,
        )
