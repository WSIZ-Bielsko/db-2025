import os
from asyncio import run
from uuid import UUID

import asyncpg
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    name: str
    age: int


async def main():
    load_dotenv()
    db_url = os.getenv('DB_URL')
    logger.info(f'using {db_url=}')

    try:
        pool = await asyncpg.create_pool(
            db_url,
            min_size=5,
            max_size=10,
            timeout=30,
            command_timeout=5,
        )
        logger.info("database connected!")
    except Exception as e:
        logger.error(f"Error connecting to DB, {e}")

    async with pool.acquire() as c:
        rows = await c.fetch("select * from users")
        users = [User(**row) for row in rows]

    for u in users:
        print(u)


if __name__ == '__main__':
    run(main())
