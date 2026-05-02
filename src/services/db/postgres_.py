"""
Async Postgres DB implementation using psycopg3.

Implements async get_schedules and get_chats using an AsyncConnectionPool.
DSN is read from constructor or environment variable DATABASE_DSN / DATABASE_URL.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional
import os
import logging
import uuid

try:
    # psycopg3 provides psycopg_pool for connection pooling
    from psycopg_pool import AsyncConnectionPool
except Exception as e:
    raise ImportError("psycopg3 and psycopg_pool are required for async Postgres support: pip install 'psycopg[binary]'") from e

from services.db.base import Base
from services.db.models import Schedule, Chat

logger = logging.getLogger(__name__)


class Postgres(Base):
    """Asynchronous Postgres implementation of services.db.base.Base.

    Notes:
    - Uses psycopg_pool.AsyncConnectionPool.
    - Exposes async get_schedules and get_chats methods.
    - DSN is taken from constructor or environment variables DATABASE_DSN / DATABASE_URL.
    """

    def __init__(self, dsn: Optional[str] = None, min_size: int = 1, max_size: int = 10) -> None:
        self._dsn = dsn or os.getenv("DATABASE_DSN") or os.getenv("DATABASE_URL")
        if not self._dsn:
            raise ValueError("Postgres DSN must be provided via constructor or DATABASE_DSN / DATABASE_URL env var")

        # Create an async connection pool
        self._pool = AsyncConnectionPool(conninfo=self._dsn, min_size=min_size, max_size=max_size)

    async def close(self) -> None:
        """Close the underlying pool."""
        await self._pool.close()

    async def _fetch_rows(self, query: str, params: tuple = ()) -> List[tuple]:
        """Helper to run a query and return fetched rows."""
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                rows = await cur.fetchall()
                return rows

    async def get_schedules(self, date: datetime) -> Optional[List[Schedule]]:
        """Return schedules for the given date (UTC or timezone-aware date expected).

        Returns None when no rows found to follow Base contract.
        """
        # normalize to start of day using provided date's tzinfo (if any)
        start = datetime(date.year, date.month, date.day, tzinfo=date.tzinfo)
        end = start + timedelta(days=1)

        query = (
            "SELECT id, title, description, status_cd, location, start_at, end_at, is_all_day "
            "FROM schedules "
            "WHERE start_at >= %s AND start_at < %s"
        )

        try:
            rows = await self._fetch_rows(query, (start, end))
        except Exception as e:
            logger.exception("Failed to fetch schedules: %s", e)
            raise

        if not rows:
            return None

        schedules: List[Schedule] = []
        for row in rows:
            # row order: id, title, description, status_cd, location, start_at, end_at, is_all_day
            schedules.append(
                Schedule(
                    id=row[0],
                    title=row[1],
                    description=row[2],
                    status_cd=row[3],
                    location=row[4],
                    start_at=row[5],
                    end_at=row[6],
                    is_all_day=row[7],
                )
            )

        return schedules

    async def get_chats(self, session_id: uuid.UUID) -> Optional[List[Chat]]:
        """Return chat history for a session, ordered by created_at ascending.

        Returns None when no rows found to follow Base contract.
        """
        query = (
            "SELECT id, session_id, role, content, created_at "
            "FROM chats "
            "WHERE session_id = %s "
            "ORDER BY created_at ASC"
        )

        try:
            rows = await self._fetch_rows(query, (session_id,))
        except Exception as e:
            logger.exception("Failed to fetch chats: %s", e)
            raise

        if not rows:
            return None

        chats: List[Chat] = []
        for row in rows:
            chats.append(
                Chat(
                    id=row[0],
                    session_id=row[1],
                    role=row[2],
                    content=row[3],
                    created_at=row[4],
                )
            )

        return chats
