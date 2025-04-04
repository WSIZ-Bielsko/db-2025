from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    name: str
    age: int


# C R U D