import uuid
from asyncio import run, sleep

from asyncpg import UniqueViolationError
from loguru import logger

from db_2025.basics.common import get_db_connection_pool
from repositories import *


async def main():
    pool = await get_db_connection_pool()

    model_repo = ModelRepository(pool)
    provider_repo = ProviderRepository(pool)

    xmodel = Model(id=uuid.uuid4(), name='grok 4.3', description='future grok model')

    try:
        zz = await model_repo.create(name=xmodel.name, description=xmodel.description)
        logger.info(f'created: {zz}')
    except UniqueViolationError as e:
        logger.warning('could not create model -- name already exists!')

    providers = await provider_repo.get_all()
    for p in providers:
        logger.info(f'provider {p.id}, {p}')


if __name__ == '__main__':
    run(main())
