from asyncio import run
from uuid import UUID, uuid4

from db_2025.basics.common import get_db_connection_pool
from user_repo import UserRepository


async def main():
    pool = await get_db_connection_pool()
    repo = UserRepository(pool)

    # z = await repo.update(user_id=UUID('eafd6645-bbcf-4c91-81e8-9db8941811e6'), age=99)
    #
    # users = await repo.get_all(limit=10 ** 9)
    # for u in users:
    #     await repo.update(user_id=u.id, age=u.age + 1)
    #
    # print(z)
    zz = await repo.delete(user_id=uuid4()) # no such user
    print(f'removed? {zz}')


if __name__ == '__main__':
    run(main())
