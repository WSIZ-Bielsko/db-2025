from pydantic import BaseModel


class Migration(BaseModel):
    start_version: int
    produces_version: int
    description: str
    up_sql: str
    down_sql: str


class MigrationError(RuntimeError):
    pass
