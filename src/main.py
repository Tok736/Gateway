from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.logger import logger
from src.rabbit import broker
from src.user.router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Старт и завершение проекта"""

    logger.info("[lifespan] Starting main tasks...")
    await broker.start()

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
