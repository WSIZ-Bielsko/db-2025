from asyncio import run, sleep

from asyncpg import Pool
from loguru import logger

from db_2025.u2.common import get_db_connection_pool
from db_2025.u2.migrations.model import Migration, m1, m2


async def get_current_version(pool: Pool) -> int:
    async with pool.acquire() as conn:
        x = await conn.fetchval('SELECT version from up.version limit 1');
        return int(x)


class MigrationError(RuntimeError):
    pass

async def execute_migration(pool: Pool, m: Migration, up: bool = True):
    """
    Checks current version of the DB;
    for up: must match m.start_version,
    for down: must match m.produces_version,

    executes the migration
    on the DB, and sets the version to m.produces_version.

    :param pool:
    :param m:
    :return:
    """

    if up:
        pass
        current_version = await get_current_version(pool)
        if current_version != m.start_version:
            raise MigrationError('start version of DB does not match')
        logger.info(f'Versions match; executing migration {m.start_version}->{m.produces_version}')
        async with pool.acquire() as conn:
            await conn.execute(m.up_sql)
            await conn.execute(f'delete from up.version where true; insert into up.version(version) values ({m.produces_version})')
        logger.info('Migration completed')

    else:
        # todo: your code
        pass


async def migrate_to(pool: Pool, final_migration_version: int):
    """
    Start with current version; if final_migration_version > current_version, go up,
    else: go down.

    UP:
    - get current version
    - find migration which starts with this version
    - execute it (producing new version)
    - check if this is the final_migration_version; if yes exit, if not repeat

    DN:
    - get current version
    - find migration which produces this version
    - execute the "down_sql"
    - update the version to start_version of this migration
    - if this final version == final_migration_version, exit; else repeat


    :param pool:
    :param final_migration_version:
    :return:
    """


async def main():
    pool = await get_db_connection_pool()
    logger.info('connection acquired')

    ver = await get_current_version(pool)
    logger.info(f'current version: {ver}')
    # await execute_migration(pool, m1, up=True)
    # await execute_migration(pool, m2, up=True)
    logger.info('closing connection')
    await pool.close()



if __name__ == '__main__':
    run(main())