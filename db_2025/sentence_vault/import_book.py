import asyncio
import os
import sys
from asyncio import run, create_task

from asyncpg import UniqueViolationError
from dotenv import load_dotenv
from loguru import logger

from db_2025.common.db import get_db_connection_pool
from db_2025.common.general import *
from db_2025.sentence_vault.repo import Repo
from db_2025.sentence_vault.model import *
from db_2025.sentence_vault.sentence_analysis import extract_verbs, is_simple_declarative, infer_tense, extract_sentences, \
    classify_sentences


async def save_sentence(repo: Repo, sentence: Sentence):
    """
    Sentence has book_id, main_type and verbatim filled

    :param repo:
    :param sentence: partially filled Sentence object;
    :return:
    """
    existing = await repo.get_sentence_by_verbatim(sentence.verbatim)
    if existing:
        return
    verbs = extract_verbs(sentence.verbatim)

    is_simple = is_simple_declarative(sentence.verbatim)
    sentence.exact_type = 'simple' if is_simple else 'N/A'
    sentence.tense = infer_tense(sentence.verbatim)

    saved = await repo.create_sentence(sentence)

    logger.debug(f'saved sentence {saved}')
    for verb in verbs:
        await save_verb(repo, verb, saved.id)


async def save_verb(repo, verb: Word, sentence_id: int):
    try:
        saved = await repo.create_word(verb)
    except UniqueViolationError as e:
        saved = await repo.get_word_by_verbatim(verb.word)
    if not saved:
        logger.info(f'could not save verb {verb}')
        return

    try:
        await repo.create_sentence_words(SentenceWords(sentence_id=sentence_id, word_id=saved.id))
    except UniqueViolationError as e:
        pass


async def test_zero():
    load_dotenv()
    pool = await get_db_connection_pool()
    repo = Repo(pool)
    logger.info('pool created')
    sentence = "I did not seem to understand."

    stc = Sentence(book_id=1, main_type='declarative', verbatim=sentence)
    await save_sentence(repo, stc)


async def import_book(pool, file_name: str, file_path: str):
    full_path = os.path.join(file_path, file_name)
    if not os.path.isfile(full_path):
        logger.warning('book {file_name} not found.')
        return

    repo = Repo(pool)
    start_ts = ts()

    book = await repo.get_book_by_title(title=file_name)
    if not book:
        book = Book(id=-1, title=file_name)
        book = await repo.create_book(book)
    else:
        logger.info(f'book {book.id} already exists')
        return

    sentences = extract_sentences(full_path)
    x = classify_sentences(sentences)
    types = ['declarative', 'imperative', 'interrogative', 'exclamatory']
    saved = 0
    tasks = []
    for t in types:
        logger.info(f'processing {t}')
        for s in x[t]:
            stc = Sentence(book_id=book.id, main_type=t, verbatim=s)
            tasks.append(create_task(save_sentence(repo, stc)))
            saved += 1
        await asyncio.gather(*tasks)
    duration_s = ts() - start_ts
    logger.info(f'saved {saved} sentences in {duration(start_ts)} ({duration_s/saved * 1000:.2f}sec/1k sentences);')


async def main():
    load_dotenv()
    st = ts()
    logger.info(f'running {st}')
    DIR = '/nfs1/datasets/books_first_1000'

    pool = await get_db_connection_pool()
    MAX_BOOKS = 500

    for idx, filename in enumerate(os.listdir(DIR)):
        if idx >= MAX_BOOKS:
            logger.info(f'processed {MAX_BOOKS} books')
            break
        logger.warning(f'processing {filename}')
        await import_book(pool=pool, file_name=filename, file_path=DIR)
    logger.info(f'imported book in {duration(st)}')


def adjust_logger():
    logger.remove()  # Remove default handler
    logger.add(sink=sys.stderr, level="INFO")  # Only log INFO, WARNING, ERROR, and above


if __name__ == '__main__':
    adjust_logger()
    run(main())
