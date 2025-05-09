from db_2025.u2.migrations.model import Migration, MigrationError

migrations_ = [
    Migration(
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
    ),
    Migration(
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
]


def get_migration_by_start_version(start_version: int) -> Migration:
    for m in migrations_:
        if m.start_version == start_version:
            return m
    else:
        raise MigrationError(f'migration with {start_version=} does not exist')


def get_migration_by_produces_version(produces_version: int) -> Migration:
    if produces_version == 1:
        raise MigrationError(f'already at first migation')

    for m in migrations_:
        if m.produces_version == produces_version:
            return m
    else:
        raise MigrationError(f'migration with {produces_version=} does not exist')
