from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


# fmt: off
class RabbitRPCResponse(BaseModel, Generic[T]):
    """Классический формат для ответов от rabbit RPC сервисов"""

    status:   int      = 200
    message:  str      = "Ok"
    data:     T | None = None
# fmt: on
