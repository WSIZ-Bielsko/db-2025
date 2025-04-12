import os
from asyncio import gather, create_task

import pytest
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel, PositiveInt, ValidationError
from uuid import UUID
import asyncpg
from fastapi.middleware.cors import CORSMiddleware

from db_2025.basics.model import User as UserModel
from user_repo import UserRepository  # Assuming the provided code is in user_repo.py

app = FastAPI()


# Pydantic models for request/response validation
class UserCreate(BaseModel):
    name: str
    age: PositiveInt
    active: bool = True


class UserUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    active: bool = True


class PaginationParams(BaseModel):
    limit: int = 10
    offset: int = 0


# Define the origins that should be allowed (e.g., your Next.js frontend)
origins = [
    "http://localhost:3000",  # Your Next.js frontend
    # Add more origins if needed, e.g., "http://localhost:8000" for testing
]
# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies or auth headers (if needed)
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# in full app, introduce startup/shutdown logic
repo: UserRepository = None


# Startup/shutdown events
@app.on_event("startup")
async def startup():
    global repo

    load_dotenv()
    db_url = os.getenv('DB_URL')

    try:
        db_pool: asyncpg.pool.Pool = await asyncpg.create_pool(
            db_url,
            min_size=5,
            max_size=10,
            timeout=30,
            command_timeout=5,
        )
        logger.info("database connected!")
        repo = UserRepository(db_pool)
    except Exception as e:
        logger.error(f"Error connecting to DB, {e}")
        raise RuntimeError('meh...')


@app.on_event("shutdown")
async def shutdown():
    logger.info("shutting down...")
    # close connection pool somehow...


# Health endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# CRUD Endpoints
@app.post("/users", response_model=UserModel)
async def create_user(user: UserCreate):
    created_user = await repo.create(user.name, user.age, user.active)
    return created_user


@app.get("/users/{user_id}", response_model=UserModel)
async def get_user(user_id: UUID):
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users", response_model=dict)
async def get_all_users(limit: int = 10, offset: int = 0):
    t1 = create_task(repo.get_all(limit=limit, offset=offset))
    t2 = create_task(repo.get_user_count())

    users, n_users = await gather(t1, t2)

    # users = await repo.get_all(limit=limit, offset=offset)
    # n_users = await repo.get_user_count()
    return {'users': users, 'total': n_users}


@app.put("/users/{user_id}", response_model=UserModel)
async def update_user(user_id: UUID, user: UserUpdate):
    updated_user = await repo.update(user_id, user.name, user.age, user.active)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@app.delete("/users/{user_id}")
async def delete_user(user_id: UUID):
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}



def test_user_age_positive():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(name="John Doe", age=-1)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
