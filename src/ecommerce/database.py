"""Database connection and session management.

Uses shop_core utilities with a locally configured DATABASE_URL.
"""

from typing import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine

from shop_core.database import (
    create_engine_from_url,
    init_db as _init_db,
    get_session as _get_session,
)

DATABASE_URL = "sqlite+aiosqlite:///./ecommerce.db"

engine: AsyncEngine = create_engine_from_url(DATABASE_URL)


async def init_db() -> None:
    """Initialize database tables."""
    await _init_db(engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database sessions."""
    async for session in _get_session(engine):
        yield session
