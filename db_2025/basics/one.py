import os
from asyncio import run
from uuid import UUID

import asyncpg
from dotenv import load_dotenv
from loguru import logger
from user_repo import UserRepository


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
        raise RuntimeError('meh...')

    repo = UserRepository(pool)

    z = await repo.update(user_id=UUID('eafd6645-bbcf-4c91-81e8-9db8941811e6'), age=99)

    users = await repo.get_all(limit=10 ** 9)
    for u in users:
        await repo.update(user_id=u.id, age=u.age + 1)

    print(z)


if __name__ == '__main__':
    run(main())
