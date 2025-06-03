from asyncio import run

from dotenv import load_dotenv
from loguru import logger

from db_2025.common.db import get_db_connection_pool
from db_2025.migrator.migrator import get_current_version, migrate_to
from db_2025.sentence_vault.migration_list import migrations


async def main():
    load_dotenv()

    pool = await get_db_connection_pool()
    ver = await get_current_version(pool)
    logger.info(f'current version: {ver}')

    await migrate_to(pool, final_migration_version=6, migrations=migrations)

    logger.info('closing connection')
    await pool.close()


if __name__ == '__main__':
    run(main())
