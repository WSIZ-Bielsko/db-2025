import asyncpg
from pydantic import BaseModel
from uuid import UUID

from db_2025.basics.model import User



"""
prompt:

Using pydantic 2, and asyncpg (python) create a UserRepository class, taking pool in constructor arg, 
and allowing for full CRUD operations on the users table; relevant functions must return User objects, 
and select's should use `*` and not list columns; use python 3.12 (and avoid importing from `typing`). 
In the "get_all" method allow for pagination, while sorting by user.name

class User(BaseModel):
    id: UUID
    name: str
    age: int


"""

class UserRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, name: str, age: int, active: bool = True) -> User:
        query = """
            INSERT INTO users (name, age, active)
            VALUES ($1, $2, $3)
            RETURNING *
        """
        async with self.pool.acquire() as connection:
            record = await connection.fetchrow(query, name, age, active)
            return User(**record)

    async def get_by_id(self, user_id: UUID) -> User | None:
        query = "SELECT * FROM users WHERE id = $1"
        async with self.pool.acquire() as connection:
            record = await connection.fetchrow(query, user_id)
            return User(**record) if record else None

    async def get_all(self, limit: int = 10, offset: int = 0) -> list[User]:
        query = """
            SELECT * FROM users 
            ORDER BY name 
            LIMIT $1 OFFSET $2
        """
        async with self.pool.acquire() as connection:
            records = await connection.fetch(query, limit, offset)
            return [User(**record) for record in records]


    async def update(self, user_id: UUID, name: str | None = None, age: int | None = None, active: bool | None = True) -> User | None:
        # Build the SET clause dynamically based on provided parameters
        # todo: better --> just pass instance of User as arg
        updates = []
        params = [user_id]
        param_count = 2

        if name is not None:
            updates.append(f"name = ${param_count}")
            params.append(name)
            param_count += 1
        if age is not None:
            updates.append(f"age = ${param_count}")
            params.append(age)
            param_count += 1
        if active is not None:
            updates.append(f"active = ${param_count}")
            params.append(active)

        if not updates:
            return await self.get_by_id(user_id)

        query = f"""
            UPDATE users 
            SET {', '.join(updates)}
            WHERE id = $1
            RETURNING *
        """

        async with self.pool.acquire() as connection:
            record = await connection.fetchrow(query, *params)
            return User(**record) if record else None

    async def delete(self, user_id: UUID) -> bool:
        query = "DELETE FROM users WHERE id = $1 RETURNING id"
        async with self.pool.acquire() as connection:
            record = await connection.fetchrow(query, user_id)
            return bool(record)

    # non-generated

    async def get_user_count(self) -> int:
        async with self.pool.acquire() as connection:
            total = await connection.fetchval("SELECT COUNT(*) FROM users")
            return total
