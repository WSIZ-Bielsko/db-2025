from db_2025.ai_proxy.model import *



"""
prompt:
Using pydantic 2, and asyncpg (python, postgres database) create repository classes, taking pool in constructor arg, 
and allowing for full CRUD operations on all relevant tables (which are just plurals of the class name); 
relevant functions must return full objects, 
and in the read operations select's should use * and not list columns; use python 3.12 (and avoid importing from typing). 
In the "get_all" method allow for pagination, while sorting by the natural parameters for each of the classes; 
all id's in create operations should be created by the database.



{content of model.py here}


"""


from datetime import datetime
from uuid import UUID
import asyncpg
from pydantic import BaseModel

# Base Models (as provided)
class Provider(BaseModel):
    id: UUID
    name: str
    url: str

class Model(BaseModel):
    id: UUID
    name: str
    description: str | None = None

class User(BaseModel):
    id: int
    name: str
    active: bool
    created_at: datetime

class Key(BaseModel):
    id: UUID
    api_key: str
    model_id: UUID
    provider_id: UUID
    created_at: datetime
    cost_per_query: float

# Repository Classes
class ProviderRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, name: str, url: str) -> Provider:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO ai.providers (name, url) VALUES ($1, $2) RETURNING *",
                name, url
            )
            return Provider(**row)

    async def get_by_id(self, id: UUID) -> Provider | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM ai.providers WHERE id = $1",
                id
            )
            return Provider(**row) if row else None

    async def get_all(self, limit: int = 10, offset: int = 0) -> list[Provider]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM providers ORDER BY name LIMIT $1 OFFSET $2",
                limit, offset
            )
            return [Provider(**row) for row in rows]

    async def update(self, id: UUID, name: str, url: str) -> Provider | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE providers SET name = $2, url = $3 WHERE id = $1 RETURNING *",
                id, name, url
            )
            return Provider(**row) if row else None

    async def delete(self, id: UUID) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM providers WHERE id = $1",
                id
            )
            return result != "DELETE 0"

class ModelRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, name: str, description: str | None = None) -> Model:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO models (name, description) VALUES ($1, $2) RETURNING *",
                name, description
            )
            return Model(**row)

    async def get_by_id(self, id: UUID) -> Model | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM models WHERE id = $1",
                id
            )
            return Model(**row) if row else None

    async def get_all(self, limit: int = 10, offset: int = 0) -> list[Model]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM models ORDER BY name LIMIT $1 OFFSET $2",
                limit, offset
            )
            return [Model(**row) for row in rows]

    async def update(self, id: UUID, name: str, description: str | None = None) -> Model | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE models SET name = $2, description = $3 WHERE id = $1 RETURNING *",
                id, name, description
            )
            return Model(**row) if row else None

    async def delete(self, id: UUID) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM models WHERE id = $1",
                id
            )
            return result != "DELETE 0"

class UserRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, name: str, active: bool) -> User:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO users (name, active) VALUES ($1, $2) RETURNING *",
                name, active
            )
            return User(**row)

    async def get_by_id(self, id: int) -> User | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                id
            )
            return User(**row) if row else None

    async def get_all(self, limit: int = 10, offset: int = 0) -> list[User]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2",
                limit, offset
            )
            return [User(**row) for row in rows]

    async def update(self, id: int, name: str, active: bool) -> User | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE users SET name = $2, active = $3 WHERE id = $1 RETURNING *",
                id, name, active
            )
            return User(**row) if row else None

    async def delete(self, id: int) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM users WHERE id = $1",
                id
            )
            return result != "DELETE 0"

class KeyRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, api_key: str, model_id: UUID, provider_id: UUID,
                    cost_per_query: float) -> Key:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO keys (api_key, model_id, provider_id, cost_per_query) "
                "VALUES ($1, $2, $3, $4) RETURNING *",
                api_key, model_id, provider_id, cost_per_query
            )
            return Key(**row)

    async def get_by_id(self, id: UUID) -> Key | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM keys WHERE id = $1",
                id
            )
            return Key(**row) if row else None

    async def get_all(self, limit: int = 10, offset: int = 0) -> list[Key]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM keys ORDER BY created_at DESC LIMIT $1 OFFSET $2",
                limit, offset
            )
            return [Key(**row) for row in rows]

    async def update(self, id: UUID, api_key: str, model_id: UUID,
                    provider_id: UUID, cost_per_query: float) -> Key | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE keys SET api_key = $2, model_id = $3, provider_id = $4, "
                "cost_per_query = $5 WHERE id = $1 RETURNING *",
                id, api_key, model_id, provider_id, cost_per_query
            )
            return Key(**row) if row else None

    async def delete(self, id: UUID) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM keys WHERE id = $1",
                id
            )
            return result != "DELETE 0"