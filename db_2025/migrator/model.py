from pydantic import BaseModel


class Migration(BaseModel):
    start_version: int
    produces_version: int
    description: str
    up_sql: str
    down_sql: str


class MigrationError(RuntimeError):
    pass


if __name__ == '__main__':
    m = Migration(start_version=1, produces_version=2, description='test', up_sql='test', down_sql='test')
