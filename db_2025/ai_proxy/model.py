from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# Providers class
class Provider(BaseModel):
    id: UUID
    name: str
    url: str


# Models class
class Model(BaseModel):
    id: UUID
    name: str
    description: str | None = None


# Users class
class User(BaseModel):
    id: int
    name: str
    active: bool
    created_at: datetime


# Keys class
class Key(BaseModel):
    id: UUID
    api_key: str
    model_id: UUID
    provider_id: UUID
    created_at: datetime
    cost_per_query: float
