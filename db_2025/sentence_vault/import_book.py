import asyncio
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


async def import_book(file_name: str, file_path: str):
    # todo: check if book imported (by title)
    #  - if yes -- skip import
    #  - if no  -- save to books, then have book_id; import whole book
    pool = await get_db_connection_pool()
    repo = Repo(pool)

    book = await repo.get_book_by_title(title=file_name)
    print(book)

    # sentences = extract_sentences(file_path)
    # x = classify_sentences(sentences)
    # types = ['declarative', 'imperative', 'interrogative', 'exclamatory']
    # saved = 0
    # tasks = []
    # for t in types:
    #     logger.info(f'processing {t}')
    #     for s in x[t]:
    #         stc = Sentence(book_id=1, main_type=t, verbatim=s)
    #         tasks.append(create_task(save_sentence(repo, stc)))
    #         saved += 1
    #     await asyncio.gather(*tasks)
    # logger.info(f'saved {saved} sentences')


async def main():
    load_dotenv()
    st = ts()
    DIR = '/nfs1/datasets/books_4'
    # await import_book(f'{DIR}/orphans-of-time-space.epub.txt', 4)
    await import_book(file_name="psychology-for-social-workers.epub.txt", file_path=DIR)
    logger.info(f'imported book in {duration(st)}')

if __name__ == '__main__':
    run(main())
