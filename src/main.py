from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.logger import logger
from src.rabbit import broker
from src.routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Старт и завершение проекта"""

    logger.info("[lifespan] Starting main tasks...")
    await broker.start()

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
