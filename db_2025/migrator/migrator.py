from asyncio import run

from asyncpg import Pool
from loguru import logger

from db_2025.u2.common import get_db_connection_pool
from db_2025.u2.migrations.model import MigrationError, Migration


async def get_current_version(pool: Pool) -> int:
    async with pool.acquire() as conn:
        x = await conn.fetchval('SELECT version from version limit 1');
        return int(x)


def get_migration_by_start_version(start_version: int, migrations: list[Migration]) -> Migration:
    for m in migrations:
        if m.start_version == start_version:
            return m
    else:
        raise MigrationError(f'migration with {start_version=} does not exist')


def get_migration_by_produces_version(produces_version: int, migrations: list[Migration]) -> Migration:
    if produces_version == 1:
        raise MigrationError(f'already at first migation')

    for m in migrations:
        if m.produces_version == produces_version:
            return m
    else:
        raise MigrationError(f'migration with {produces_version=} does not exist')


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
    current_version = await get_current_version(pool)

    if up:
        if current_version != m.start_version:
            raise MigrationError('start version of DB does not match')
        logger.info(f'Versions match; executing migration {m.start_version}->{m.produces_version}')
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(m.up_sql)
                await conn.execute(
                    f'delete from version where true; insert into version(version) values ({m.produces_version})')
        logger.info('Migration completed')

    else:
        if current_version != m.produces_version:
            raise MigrationError(f'cant revert migration; {current_version} != produces version = {m.produces_version}')

        logger.info(f'Versions match; executing migration {m.produces_version}->{m.start_version}')
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(m.down_sql)
                await conn.execute(
                    f'delete from version where true; insert into version(version) values ({m.start_version})')
        logger.info('Migration completed')


async def migrate_to(pool: Pool, final_migration_version: int, migrations: list[Migration]):
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
    current_version = await get_current_version(pool)

    if current_version < final_migration_version:
        while True:
            current_version = await get_current_version(pool)
            if current_version == final_migration_version:
                logger.info(f'Executed all migrations up to version {current_version}')
                return
            try:
                to_execute = get_migration_by_start_version(current_version, migrations)
                await execute_migration(pool, to_execute, up=True)
            except MigrationError:
                logger.info(f'Executed all possible migrations; final version {current_version}')
                return

    else:
        while True:
            current_version = await get_current_version(pool)
            if current_version == 1:
                logger.info('Reached version=1 of the DB; exiting')
                return
            if current_version == final_migration_version:
                logger.info(f'Reached version={current_version} of the DB; exiting')
                return
            try:
                to_execute = get_migration_by_produces_version(produces_version=current_version,
                                                               migrations=migrations)
                await execute_migration(pool, to_execute, up=False)
            except MigrationError:
                logger.info(f'Executed all possible migrations; final version {current_version}')
                return
