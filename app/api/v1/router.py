"""Versioned API router configuration."""

from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.api.pdf_controller import router as pdf_controller_router

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"], prefix="/health")
api_router.include_router(pdf_controller_router, tags=["pdf"], prefix="/pdf")

# from fastapi import FastAPI
# from app.api.v1.api import api_router   # 여기서 api_router import

# app = FastAPI()

# # 핵심: 전체 버전 라우터 등록
# app.include_router(api_router, prefix="/api/v1")
