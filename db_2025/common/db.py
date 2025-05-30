import os

import asyncpg
from dotenv import load_dotenv
from loguru import logger
from asyncpg.pool import Pool


async def get_db_connection_pool() -> Pool:
    """
    Creates connection pool to the DB; DB_URL is taken from envvar (and also .env).
    :return: connection pool or RuntimeError if connecting to the DB is not possible
    """
    load_dotenv()
    db_url = os.getenv('DB_URL')
    if db_url is None:
        raise RuntimeError('DB_URL is not set')
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
        return pool
    except Exception as e:
        logger.error(f"Error connecting to DB, {e}")
        raise RuntimeError('meh...')
