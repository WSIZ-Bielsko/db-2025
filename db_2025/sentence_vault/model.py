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
    id: int
    book_id: int
    main_type: str  # (declarative, interrogative, imperative, exclamatory)
    exact_type: str  # eg: Noun Clause Sentences
    tense: str
    verbatim: str


class Word(BaseModel):
    id: int
    word: str
    nltk_token: str


class NLTK_Tokens(BaseModel):
    token: str
    description: str


class SentenceWords(BaseModel):
    sentence_id: int
    verb_id: int
