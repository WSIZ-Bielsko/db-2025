from asyncpg import Pool, Connection
from loguru import logger

from db_2025.sentence_vault.model import *


"""
AI prompt:

Using pydantic 2, and asyncpg (python, postgres database) create a class Repo, taking connection pool in constructor arg, 
with methods corresponding to full CRUD operations for each of the relevant database tables specified below. 
For each of the data classes the database tables are named as plurals of the data class names. 

Technically: 
- there should be independent methods for each of the data classess,
- relevant functions must return full objects, and should use union types as return types where needed,
- in the read operations select's should use * and not list columns; 
- code shoul use modern python, e.g. 3.12+, e.g. using union types and avoid importing from typing package, such as using Optional 
- in the "get_all" method allow for pagination, while sorting by the natural parameters for each of the classes; 
all id's in create operations should be created by the database.
- update operations should take full objects as arguments
- for the get operations, create also get_count methods
- output code only

(paste model.py here)

"""

class Repo:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def _execute_query(self, conn: Connection, query: str, *args):
        try:
            return await conn.fetch(query, *args)
        except Exception as e:
            # logger.error(f"Query execution failed: {query}, Error: {str(e)}")
            raise

    async def _execute_non_query(self, conn: Connection, query: str, *args):
        try:
            await conn.execute(query, *args)
        except Exception as e:
            logger.error(f"Non-query execution failed: {query}, Error: {str(e)}")
            raise

    # Book CRUD
    async def create_book(self, book: Book) -> Book:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO books (title) VALUES ($1) RETURNING *",
                book.title
            )
            return Book(**row)

    async def get_book(self, id: int) -> Book | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM books WHERE id = $1", id)
            return Book(**row) if row else None

    async def get_all_books(self, offset: int = 0, limit: int = 10) -> list[Book]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM books ORDER BY title OFFSET $1 LIMIT $2",
                offset, limit
            )
            return [Book(**row) for row in rows]

    async def get_books_count(self) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM books")

    async def update_book(self, book: Book) -> Book | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE books SET title = $1 WHERE id = $2 RETURNING *",
                book.title, book.id
            )
            return Book(**row) if row else None

    async def delete_book(self, id: int) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute("DELETE FROM books WHERE id = $1", id)
            return result != "DELETE 0"

    # Sentence CRUD Operations
    async def create_sentence(self, sentence: Sentence) -> Sentence:
        query = """
                INSERT INTO sentences (book_id, main_type, exact_type, tense, verbatim)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING * \
                """
        async with self.pool.acquire() as conn:
            record = await self._execute_query(
                conn,
                query,
                sentence.book_id,
                sentence.main_type,
                sentence.exact_type,
                sentence.tense,
                sentence.verbatim
            )
            return Sentence(**record[0])

    async def get_sentence(self, sentence_id: int) -> Sentence | None:
        query = "SELECT * FROM sentences WHERE id = $1"
        async with self.pool.acquire() as conn:
            records = await self._execute_query(conn, query, sentence_id)
            return Sentence(**records[0]) if records else None

    async def get_all_sentences(self, offset: int = 0, limit: int = 100) -> list[Sentence]:
        query = """
                SELECT *
                FROM sentences
                ORDER BY book_id, main_type, tense, id
                OFFSET $1 LIMIT $2 \
                """
        async with self.pool.acquire() as conn:
            records = await self._execute_query(conn, query, offset, limit)
            return [Sentence(**record) for record in records]

    async def update_sentence(self, sentence_id: int, sentence: Sentence) -> Sentence | None:
        query = """
                UPDATE sentences
                SET book_id    = $1,
                    main_type  = $2,
                    exact_type = $3,
                    tense      = $4,
                    verbatim   = $5
                WHERE id = $6
                RETURNING * \
                """
        async with self.pool.acquire() as conn:
            records = await self._execute_query(
                conn,
                query,
                sentence.book_id,
                sentence.main_type,
                sentence.exact_type,
                sentence.tense,
                sentence.verbatim,
                sentence_id
            )
            return Sentence(**records[0]) if records else None

    async def delete_sentence(self, sentence_id: int) -> bool:
        query = "DELETE FROM sentences WHERE id = $1"
        async with self.pool.acquire() as conn:
            await self._execute_non_query(conn, query, sentence_id)
            return True

    # Word CRUD Operations
    async def create_word(self, word: Word) -> Word:
        query = """
                INSERT INTO words (word, nltk_token)
                VALUES ($1, $2)
                RETURNING * \
                """
        async with self.pool.acquire() as conn:
            record = await self._execute_query(
                conn,
                query,
                word.word,
                word.nltk_token
            )
            return Word(**record[0])

    async def get_word(self, word_id: int) -> Word | None:
        query = "SELECT * FROM words WHERE id = $1"
        async with self.pool.acquire() as conn:
            records = await self._execute_query(conn, query, word_id)
            return Word(**records[0]) if records else None

    async def get_all_words(self, offset: int = 0, limit: int = 100) -> list[Word]:
        query = """
                SELECT *
                FROM words
                ORDER BY word, id
                OFFSET $1 LIMIT $2 \
                """
        async with self.pool.acquire() as conn:
            records = await self._execute_query(conn, query, offset, limit)
            return [Word(**record) for record in records]

    async def update_word(self, word_id: int, word: Word) -> Word | None:
        query = """
                UPDATE words
                SET word       = $1,
                    nltk_token = $2
                WHERE id = $3
                RETURNING * \
                """
        async with self.pool.acquire() as conn:
            records = await self._execute_query(
                conn,
                query,
                word.word,
                word.nltk_token,
                word_id
            )
            return Word(**records[0]) if records else None

    async def delete_word(self, word_id: int) -> bool:
        query = "DELETE FROM words WHERE id = $1"
        async with self.pool.acquire() as conn:
            await self._execute_non_query(conn, query, word_id)
            return True

    # SentenceWords CRUD Operations
    async def create_sentence_words(self, sentence_words: SentenceWords) -> SentenceWords:
        query = """
                INSERT INTO sentence_words (sentence_id, word_id)
                VALUES ($1, $2)
                RETURNING * \
                """
        async with self.pool.acquire() as conn:
            record = await self._execute_query(
                conn,
                query,
                sentence_words.sentence_id,
                sentence_words.word_id
            )
            return SentenceWords(**record[0])

    async def get_sentence_words(self, sentence_id: int, word_id: int) -> SentenceWords | None:
        query = "SELECT * FROM sentence_words WHERE sentence_id = $1 AND word_id = $2"
        async with self.pool.acquire() as conn:
            records = await self._execute_query(conn, query, sentence_id, word_id)
            return SentenceWords(**records[0]) if records else None

    async def get_all_sentence_words(self, offset: int = 0, limit: int = 100) -> list[SentenceWords]:
        query = """
                SELECT *
                FROM sentence_words
                ORDER BY sentence_id, word_id
                OFFSET $1 LIMIT $2 \
                """
        async with self.pool.acquire() as conn:
            records = await self._execute_query(conn, query, offset, limit)
            return [SentenceWords(**record) for record in records]

    async def delete_sentence_words(self, sentence_id: int, word_id: int) -> bool:
        query = "DELETE FROM sentence_words WHERE sentence_id = $1 AND word_id = $2"
        async with self.pool.acquire() as conn:
            await self._execute_non_query(conn, query, sentence_id, word_id)
            return True

    # extra

    async def get_word_by_verbatim(self, word_verbatim: str) -> Word | None:
        query = "SELECT * FROM words WHERE word = $1"
        async with self.pool.acquire() as conn:
            records = await self._execute_query(conn, query, word_verbatim)
            return Word(**records[0]) if records else None

    async def get_sentence_by_verbatim(self, sentence_verbatim: str) -> Sentence | None:
        query = "SELECT * FROM sentences WHERE verbatim = $1 AND MD5(verbatim) = MD5($1);"
        async with self.pool.acquire() as conn:
            records = await self._execute_query(conn, query, sentence_verbatim)
            return Sentence(**records[0]) if records else None

    async def get_book_by_title(self, title: str) -> Book | None:
        query = "SELECT * FROM books WHERE title = $1"
        async with self.pool.acquire() as conn:
            records = await self._execute_query(conn, query, title)
            return Book(**records[0]) if records else None
