from pydantic import BaseModel


class Book(BaseModel):
    id: int
    title: str


class Category(BaseModel):
    id: int
    name: str


class BookCategories(BaseModel):
    book_id: int
    cat_id: int


class Sentence(BaseModel):
    id: int = -1
    book_id: int
    main_type: str = 'N/A'  # (declarative, interrogative, imperative, exclamatory)
    exact_type: str = 'N/A' # eg: Noun Clause Sentences
    tense: str = 'N/A'
    verbatim: str

# tense = 'Present', 'Past', 'Future','Mixed or unclear'

class Word(BaseModel):
    id: int
    word: str
    nltk_token: str


class NLTK_Tokens(BaseModel):
    token: str
    description: str


class SentenceWords(BaseModel):
    sentence_id: int
    word_id: int
