from fastapi import APIRouter, HTTPException

from src.base_schemas import RabbitRPCResponse
from src.rabbit import rpc_call
from src.schemas.auth import RegisterRequest, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(request: RegisterRequest) -> UserRead:
    """Зарегистрировать пользователя"""

    response = await rpc_call(
        request,
        "auth_consumer.POST.register",
        RabbitRPCResponse[UserRead],
        timeout=10,
    )

    if response is None or response.data is None:
        raise HTTPException(status_code=500, detail="Auth service is unavailable")

    if response.status >= 300:
        raise HTTPException(status_code=response.status, detail=response.message)

    return response.data
