import asyncpg
from typing import Optional, List, Dict, Any
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL


class Database:
    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def init_pool(cls):
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
        print("✅ Database pool created.")

    @classmethod
    async def close_pool(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
        print("🛑 Database pool closed.")

    @classmethod
    async def fetch_all(
        cls, query: str, params: Optional[List[Any]] = None
    ) -> List[asyncpg.Record]:
        async with cls._pool.acquire() as conn:
            return await conn.fetch(query, *(params or []))
