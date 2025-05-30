from db_2025.u2.migrations.model import Migration

migrations_example = [
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
    ),
    Migration(
        start_version=3,
        produces_version=4,
        description='create association between files and categories',
        up_sql="""
        create table up.file_categories(
            file_id uuid references up.files(id) on delete cascade ,
            cat_id uuid references up.cats(id) on delete cascade,
            unique (file_id,cat_id)
        );
        
        """,
        down_sql='drop table up.file_categories;',
    )
]

