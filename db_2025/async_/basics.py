import time
from asyncio import run, sleep, current_task, create_task, gather

from loguru import logger


async def fn1(x):
    # logger.info(f'entering fn, {x=}')
    await sleep(0.1)
    #  user = await repo.get_by_id(user_id)
    return x * x


async def launch_many_sequential():
    logger.info('many - enter')
    xx = await fn1(2)
    yy = await fn1(3)

    logger.info(f'results: {xx=}, {yy=}')
    logger.info('many - exit')


async def launch_many_parallel():
    logger.info('many - enter')
    t1 = create_task(fn1(2))
    t2 = create_task(fn1(3))
    xx, yy = await gather(t1, t2)

    logger.info(f'results: {xx=}, {yy=}')
    logger.info('many - exit')


async def launch_ddos():
    logger.info('many - enter')
    tasks = []
    for i in range(10**5):
        tasks.append(create_task(fn1(i)))
    results = await gather(*tasks)


async def main():
    logger.info(f'in async context task={current_task().get_name()}')
    # await sleep(0.1)
    # xx = await fn1(2)
    # await launch_many_sequential()
    # await launch_many_parallel()
    await launch_ddos()
    logger.info(f'sleep done; ')


if __name__ == '__main__':
    logger.info('main begins')
    run(main())  # uruchamia event loop
    logger.info('main done')
