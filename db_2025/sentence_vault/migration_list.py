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
    Migration(start_version=2, produces_version=3, description='add column sentence.verbatim', up_sql="""
    ALTER TABLE sentences ADD COLUMN verbatim TEXT not null;
    """, down_sql="""
    ALTER TABLE sentences DROP COLUMN verbatim;
                  """),
    Migration(start_version=3, produces_version=4, description='rename column verb_id to word_id', up_sql="""
    ALTER TABLE sentence_words RENAME COLUMN verb_id TO word_id;
    """, down_sql="""
    ALTER TABLE sentence_words RENAME COLUMN word_id TO verb_id;"""),
    Migration(start_version=4, produces_version=5, description='add nltk tokens',
              up_sql="""
INSERT INTO nltk_tokens (token, description) VALUES ('CC', 'Coordinating conjunction'), ('CD', 'Cardinal number'), ('DT', 'Determiner'), ('EX', 'Existential there'), ('FW', 'Foreign word'), ('IN', 'Preposition or subordinating conjunction'), ('JJ', 'Adjective'), ('JJR', 'Adjective, comparative'), ('JJS', 'Adjective, superlative'), ('LS', 'List item marker'), ('MD', 'Modal'), ('NN', 'Noun, singular or mass'), ('NNS', 'Noun, plural'), ('NNP', 'Proper noun, singular'), ('NNPS', 'Proper noun, plural'), ('PDT', 'Predeterminer'), ('POS', 'Possessive ending'), ('PRP', 'Personal pronoun'), ('PRP$', 'Possessive pronoun'), ('RB', 'Adverb'), ('RBR', 'Adverb, comparative'), ('RBS', 'Adverb, superlative'), ('RP', 'Particle'), ('SYM', 'Symbol'), ('TO', '''to'''), ('UH', 'Interjection'), ('VB', 'Verb, base form'), ('VBD', 'Verb, past tense'), ('VBG', 'Verb, gerund or present participle'), ('VBN', 'Verb, past participle'), ('VBP', 'Verb, non-3rd person singular present'), ('VBZ', 'Verb, 3rd person singular present'), ('WDT', 'Wh-determiner'), ('WP', 'Wh-pronoun'), ('WP$', 'Possessive wh-pronoun'), ('WRB', 'Wh-adverb');
              """,
              down_sql='delete from nltk_tokens where true'),
    Migration(start_version=5, produces_version=6, description='make words unique in word table',
              up_sql="ALTER TABLE words ADD CONSTRAINT unique_word UNIQUE (word);",
              down_sql="ALTER TABLE words DROP CONSTRAINT unique_word;"),


]

