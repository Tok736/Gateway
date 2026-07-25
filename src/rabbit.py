import asyncio
from typing import Any, Generic, Literal, NamedTuple, TypeVar, overload
from uuid import uuid4

from fastapi import HTTPException
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitQueue
from pydantic import BaseModel

from src.config import settings
from src.logger import logger

broker = RabbitBroker(settings.rabbit.rabbit_url, logger=logger)

T_response = TypeVar("T_response", bound=BaseModel)


class Pending(NamedTuple):
    """Ожидающий ответа запрос: future + схема для валидации ответа."""

    future: asyncio.Future[Any]
    response_schema: type[BaseModel]


class RabbitRPCManager:
    """
    Менеджер RPC-запросов поверх RabbitMQ.

    Обязанности:
      * лениво создать единственную callback-очередь (при первом запросе)
        и держать её живой до конца жизни процесса;
      * сопоставлять ответы с запросами по correlation_id;
      * валидировать ответ в переданную pydantic-схему.
    """

    def __init__(self, broker: RabbitBroker) -> None:
        self.broker = broker
        self.pending: dict[str, Pending] = {}
        self.callback_queue: RabbitQueue | None = None
        self.subscriber: Any = None
        self.setup_lock = asyncio.Lock()

    async def get_callback_queue(self) -> RabbitQueue:
        """Идемпотентно создаёт callback-очередь и подписчика"""

        if self.callback_queue is not None:
            return self.callback_queue

        async with self.setup_lock:
            if self.callback_queue is not None:
                return self.callback_queue

            callback_queue = RabbitQueue(f"Gateway_Callback_{uuid4().hex[:16]}", exclusive=True)
            subscriber = self.broker.subscriber(callback_queue)

            @subscriber
            async def _callback(body: dict[str, Any], message: RabbitMessage) -> None:
                await self._on_response(body, message)

            await subscriber.start()

            self.subscriber = subscriber
            self.callback_queue = callback_queue
            logger.debug(f"[RabbitRPCManager] Callback queue '{callback_queue.name}' is ready")
            return callback_queue

    async def _on_response(self, body: dict[str, Any], message: RabbitMessage) -> None:
        correlation_id = message.correlation_id

        if correlation_id is None:
            logger.warning("[RabbitRPCManager] Response without correlation_id dropped")
            return

        pending = self.pending.pop(correlation_id, None)
        if pending is None:
            logger.warning(f"[RabbitRPCManager] Unknown correlation_id '{correlation_id}' dropped")
            return

        if pending.future.done():
            return

        try:
            pending.future.set_result(pending.response_schema.model_validate(body))
        except Exception as exc:
            pending.future.set_exception(exc)

    async def call(
        self,
        request: BaseModel,
        queue: str,
        response_schema: type[T_response],
        *,
        timeout: float = 60,
        ttl: float = 3600,
    ) -> T_response | None:

        callback_queue = await self.get_callback_queue()
        correlation_id = uuid4().hex
        future: asyncio.Future[T_response] = asyncio.get_running_loop().create_future()
        self.pending[correlation_id] = Pending(future, response_schema)

        try:
            logger.debug(f"[RabbitRPCManager] -> '{queue}' (cid={correlation_id})")
            await self.broker.publish(
                request.model_dump(),
                queue,
                correlation_id=correlation_id,
                reply_to=callback_queue.name,
                timeout=timeout,
                expiration=ttl,
            )
            return await asyncio.wait_for(future, timeout=timeout)
        except TimeoutError:
            logger.warning(f"[RabbitRPCManager] Timeout waiting for response (cid={correlation_id})")
        except Exception as e:
            logger.warning(f"[RabbitRPCManager] Error on request (cid={correlation_id}): {e}")
        finally:
            self.pending.pop(correlation_id, None)

        return None


manager = RabbitRPCManager(broker)


async def rpc_call(
    request: BaseModel,
    queue: str,
    response_schema: type[T_response],
    *,
    timeout: float = 60,
    ttl: float = 3600,
) -> T_response | None:
    """Выполнить RPC-запрос по RabbitMQ"""

    result = await manager.call(request, queue, response_schema, timeout=timeout, ttl=ttl)

    if result is not None:
        try:
            logger.debug(f"[rpc_call] Answer from rpc call to {queue}:\n{result.model_dump()}")
        except Exception:
            logger.debug(f"[rpc_call] Got answer from rpc call to {queue}. No content")

    return result


T = TypeVar("T", bound=BaseModel)


# fmt: off
class RabbitRPCResponse(BaseModel, Generic[T]):
    """Классический формат для ответов от rabbit RPC сервисов"""

    status:   int      = 200
    message:  str      = "Ok"
    data:     T | None = None

    @property
    def ok(self) -> bool:
        return self.status < 300
# fmt: on


@overload
async def rpc_handler(
    request: BaseModel,
    queue: str,
    response_schema: type[RabbitRPCResponse[T]],
    service_name: str,
    *,
    timeout: float = 60,
    ttl: float = 3600,
    data_expected: Literal[True] = True,
    raise_http_error: bool = True,
) -> T: ...


@overload
async def rpc_handler(
    request: BaseModel,
    queue: str,
    response_schema: type[RabbitRPCResponse[T]],
    service_name: str,
    *,
    timeout: float = 60,
    ttl: float = 3600,
    data_expected: Literal[False],
    raise_http_error: bool = True,
) -> None: ...


async def rpc_handler(
    request: BaseModel,
    queue: str,
    response_schema: type[RabbitRPCResponse[T]],
    service_name: str,
    *,
    timeout: float = 60,
    ttl: float = 3600,
    data_expected: bool = True,
    raise_http_error: bool = True,
) -> T | None:
    """RPC запрос по RabbitMQ с дополнительной обработкой исключений"""

    response = await rpc_call(
        request,
        queue,
        response_schema,
        timeout=timeout,
        ttl=ttl,
    )

    if raise_http_error:
        if response is None:
            raise HTTPException(status_code=500, detail=f"{service_name} is unavailable")

        if response.status >= 300:
            raise HTTPException(status_code=response.status, detail=response.message)

        if data_expected and response.data is None:
            raise HTTPException(status_code=500, detail=f"{service_name} unexpected behavior")

    return response.data if response else None  # pyright: ignore[reportOptionalMemberAccess]
