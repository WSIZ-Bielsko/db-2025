from db_2025.u2.migrations.model import Migration


migrations = [
    Migration(
        start_version=1,
        produces_version=2,
        description='create tables for metafiles, categories, and relations between them and authors',
        up_sql="""
            CREATE TABLE file_meta (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                original_file_name TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                owner_name_short TEXT NOT NULL,
                size_mb INTEGER NOT NULL,
                upload_date TIMESTAMP NOT NULL,
                public BOOLEAN NOT NULL,
                frozen BOOLEAN NOT NULL
            );
            
            CREATE TABLE category (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name TEXT NOT NULL,
                przedmiot_id INTEGER,
                public BOOLEAN NOT NULL,
                comment TEXT NOT NULL
            );
            
            -- relations
            
            -- Table for FileCategory (many-to-many relation between FileMeta and Category)
            CREATE TABLE file_category (
                file_id UUID NOT NULL REFERENCES file_meta(id) ON DELETE CASCADE,
                cat_id UUID NOT NULL REFERENCES category(id) ON DELETE CASCADE,
                UNIQUE(file_id, cat_id)
            );
            
            -- Table for FileAuthor (many-to-many relation between FileMeta and authors)
            CREATE TABLE file_author (
                file_id UUID NOT NULL REFERENCES file_meta(id) ON DELETE CASCADE,
                author_id INTEGER NOT NULL,
                UNIQUE(file_id, author_id)
            );
        """,
        down_sql="""
            drop table file_author;
            drop table file_category;
            drop table category;
            drop table file_meta;
        """
    ),
    Migration(
        start_version=2,
        produces_version=3,
        description='rename public -> is_public',
        up_sql="""

alter table category
    rename column public to is_public;



""",
        down_sql="""
        
        

alter table category
    rename column is_public to public;


        """
    )

]