from asyncio import run
import asyncpg
from loguru import logger
from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime


from db_2025.u2.common import get_db_connection_pool
from db_2025.u2.model import Category


# Repository class for Category
class CategoryRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.table_name = "category"

    async def create(self, category: Category) -> Category:
        query = f"""
            INSERT INTO {self.table_name} (name, przedmiot_id, is_public, comment)
            VALUES ($1, $2, $3, $4)
            RETURNING *;
        """
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(
                query,
                category.name,
                category.przedmiot_id,
                category.is_public,
                category.comment
            )
            return Category(**record)

    async def get_by_id(self, id: UUID) -> Category | None:
        query = f"SELECT * FROM {self.table_name} WHERE id = $1;"
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(query, id)
            if record is None:
                return None
            return Category(**record)

    async def get_all(self, limit: int = 10, offset: int = 0) -> list[Category]:
        query = f"""
            SELECT * FROM {self.table_name}
            ORDER BY name ASC
            LIMIT $1 OFFSET $2;
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(query, limit, offset)
            return [Category(**record) for record in records]

    async def update(self, id: UUID, category: Category) -> Category | None:
        query = f"""
            UPDATE {self.table_name}
            SET name = $1, przedmiot_id = $2, is_public = $3, comment = $4
            WHERE id = $5
            RETURNING *;
        """
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(
                query,
                category.name,
                category.przedmiot_id,
                category.is_public,
                category.comment,
                id
            )
            if record is None:
                return None
            return Category(**record)

    async def delete(self, id: UUID) -> bool:
        query = f"DELETE FROM {self.table_name} WHERE id = $1 RETURNING id;"
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(query, id)
            return record is not None


async def main():
    pool = await get_db_connection_pool()
    repo = CategoryRepository(pool)
    # cat = Category(id=uuid4(), name='testowa1', przedmiot_id=1, is_public=True, comment='uploader testing')
    # c1 = await repo.create(cat)
    c1 = await repo.get_by_id(UUID('b77a255a-0d9a-4c5a-87d5-4171fb3f7067'))
    logger.info(c1)




if __name__ == '__main__':
    run(main())
