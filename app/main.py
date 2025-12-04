"""FastAPI application entry point."""

import logging
from fastapi import FastAPI
import sys

from app.api.v1.router import api_router
from app.core.config import settings


def create_application() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)  # stdout 사용
    ]
)

logger = logging.getLogger(__name__)

app = create_application()
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")

