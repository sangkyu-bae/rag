"""Shared dependencies for API routes."""

from typing import Generator

from contextlib import contextmanager


@contextmanager
def get_db() -> Generator[None, None, None]:
    """
    Dependency placeholder for database session handling.

    Replace this implementation with your actual database session manager.
    """
    try:
        yield
    finally:
        # Close DB connection here when a real session is used.
        ...

