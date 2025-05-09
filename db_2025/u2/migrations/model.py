from pydantic import BaseModel


class Migration(BaseModel):
    start_version: int
    produces_version: int
    description: str
    up_sql: str
    down_sql: str


m1 = Migration(
    start_version=1,
    produces_version=2,
    description='create table files',
    up_sql="""

            create table up.files(
            id uuid default gen_random_uuid() primary key ,
            name text not null,
            owner_id int not null
        );

    """,
    down_sql='drop table up.files;',
)


m2 = Migration(
    start_version=2,
    produces_version=3,
    description='create table categories',
    up_sql="""

            create table up.cats(
            id uuid default gen_random_uuid() primary key ,
            name text not null
        );

    """,
    down_sql='drop table up.cats;',
)