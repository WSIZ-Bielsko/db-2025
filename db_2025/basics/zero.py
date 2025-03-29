import os
from asyncio import run
from uuid import UUID, uuid4

import asyncpg
from asyncpg import Record
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    name: str
    age: int


async def get_users(pool, page: int, limit: int) -> list[User]:
    query = "select * from users ORDER BY name, age LIMIT $1 OFFSET $2"
    async with pool.acquire() as c:
        rows = await c.fetch(query, limit, page * limit)
        users: list[User] = [User(**row) for row in rows]
    return users


async def main():
    load_dotenv()
    db_url = os.getenv('DB_URL')
    logger.info(f'using {db_url=}')

    try:
        pool: asyncpg.pool.Pool = await asyncpg.create_pool(
            db_url,
            min_size=5,
            max_size=10,
            timeout=30,
            command_timeout=5,
        )
        logger.info("database connected!")
    except Exception as e:
        logger.error(f"Error connecting to DB, {e}")
        raise RuntimeError('meh...')

    async with pool.acquire() as c:
        # rows: list[Record] = await c.fetch("select * from users")
        # users: list[User] = [User(**row) for row in rows]
        users = await get_users(pool, 2, 10)

    for u in users:
        print(u)


if __name__ == '__main__':
    # u = User(id=uuid4(), name='Xi', age=12, zzz=False)
    run(main())
    # print(u)
