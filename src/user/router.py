from fastapi import APIRouter, Depends, Response, status

from src.auth.dependency import get_access_token
from src.auth.utils import clear_auth_cookies
from src.rabbit import RabbitRPCResponse, rpc_handler

from .schemas import (
    DeleteProfileRequest,
    ReadProfileRequest,
    UpdateProfileRequest,
    UserRead,
    UserUpdate,
)

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me")
async def get_me(access_token: str = Depends(get_access_token)) -> UserRead:
    """Получить пользователя на основе данных access_token"""

    return await rpc_handler(
        ReadProfileRequest(access_token=access_token),
        "GET-user_service/profile/me",
        RabbitRPCResponse[UserRead],
        "User service",
        timeout=10,
        data_expected=True,
    )


@router.put("/me")
async def update_me(
    user: UserUpdate, access_token: str = Depends(get_access_token)
) -> UserRead:
    """Получить пользователя на основе данных access_token"""

    return await rpc_handler(
        UpdateProfileRequest(
            access_token=access_token, **user.model_dump(exclude_unset=True)
        ),
        "PUT-user_service/profile/me",
        RabbitRPCResponse[UserRead],
        "User service",
        timeout=10,
        data_expected=True,
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    response: Response,
    access_token: str = Depends(get_access_token),
) -> None:
    """Получить пользователя на основе данных access_token"""

    await rpc_handler(
        DeleteProfileRequest(access_token=access_token),
        "DELETE-user_service/profile/me",
        RabbitRPCResponse,
        "User service",
        timeout=10,
        data_expected=False,
    )

    clear_auth_cookies(response)
