from db_2025.u2.migrations.model import Migration

migrations = [
    Migration(
        start_version=1,
        produces_version=2,
        description='create initial tables',
        up_sql="""

-- Create tables for the book categorization and sentence analysis system

-- Books table
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL
);

-- Categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Book-Category many-to-many relationship
CREATE TABLE book_categories (
    book_id INTEGER NOT NULL,
    cat_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, cat_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (cat_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- NLTK tokens lookup table
CREATE TABLE nltk_tokens (
    token VARCHAR(50) PRIMARY KEY,
    description TEXT
);

-- Words table
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    word VARCHAR(100) NOT NULL,
    nltk_token VARCHAR(50),
    FOREIGN KEY (nltk_token) REFERENCES nltk_tokens(token)
);

-- Sentences table
CREATE TABLE sentences (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    main_type VARCHAR(50) NOT NULL CHECK (main_type IN ('declarative', 'interrogative', 'imperative', 'exclamatory')),
    exact_type VARCHAR(100),
    tense VARCHAR(50),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- Sentence-Words relationship (assuming verb_id refers to word_id)
CREATE TABLE sentence_words (
    sentence_id INTEGER NOT NULL,
    verb_id INTEGER NOT NULL,
    PRIMARY KEY (sentence_id, verb_id),
    FOREIGN KEY (sentence_id) REFERENCES sentences(id) ON DELETE CASCADE,
    FOREIGN KEY (verb_id) REFERENCES words(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_book_categories_book_id ON book_categories(book_id);
CREATE INDEX idx_book_categories_cat_id ON book_categories(cat_id);
CREATE INDEX idx_sentences_book_id ON sentences(book_id);
CREATE INDEX idx_sentence_words_sentence_id ON sentence_words(sentence_id);
CREATE INDEX idx_words_nltk_token ON words(nltk_token);

    """,
        down_sql="""
        
        -- Drop all tables and structures (down migration)
-- Order matters due to foreign key constraints

DROP TABLE IF EXISTS sentence_words CASCADE;
DROP TABLE IF EXISTS sentences CASCADE;
DROP TABLE IF EXISTS words CASCADE;
DROP TABLE IF EXISTS nltk_tokens CASCADE;
DROP TABLE IF EXISTS book_categories CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS books CASCADE;

-- Drop indexes (if they weren't automatically dropped with tables)
DROP INDEX IF EXISTS idx_book_categories_book_id;
DROP INDEX IF EXISTS idx_book_categories_cat_id;
DROP INDEX IF EXISTS idx_sentences_book_id;
DROP INDEX IF EXISTS idx_sentence_words_sentence_id;
DROP INDEX IF EXISTS idx_words_nltk_token;

        
        
        """,
    ),

]

