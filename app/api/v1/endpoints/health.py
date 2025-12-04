"""Health check endpoint."""

from fastapi import APIRouter, status

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_health() -> dict[str, str]:
    """Return a simple health check payload."""
    return {"status": "ok"}

