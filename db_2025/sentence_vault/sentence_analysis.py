import re
from nltk import pos_tag, word_tokenize
import nltk

from db_2025.sentence_vault.model import Word


def setup_nltk():
    # Download required NLTK data (run once)
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('averaged_perceptron_tagger_eng')


def extract_sentences(file_path: str) -> list[str]:
    """
    Extracts and returns sentences from a text file. This function reads the content
    of a specified file, processes the text to normalize spacing, and tokenizes it
    into individual sentences.

    :param file_path: The file path of the text file from which sentences
                      are to be extracted.
    :type file_path: str
    :return: A list of sentences extracted from the file.
    :rtype: list[str]
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    # Replace newlines and multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text).strip()

    # Tokenize into sentences
    sentences = nltk.sent_tokenize(text)
    return sentences


def classify_sentences(sentences: list[str]) -> dict[str, list[str]]:
    """
    Classifies a list of sentences into various grammatical categories. The function
    analyzes each sentence in the input list and categorizes it based on its ending
    punctuation or structural characteristics. Sentences are grouped into the
    following categories: declarative, interrogative, imperative, exclamatory,
    and simple declarative. Sentences shorter than 20 characters are ignored.

    :param sentences: A list of sentences to be classified
    :type sentences: list[str]

    :return: A dictionary where the keys are sentence types ('declarative',
             'interrogative', 'imperative', 'exclamatory', and 'simple'),
             and the values are lists of sentences belonging to each category
    :rtype: dict[str, list[str]]
    """
    declarative = []
    interrogative = []
    imperative = []
    exclamatory = []
    simple = []

    for sentence in sentences:
        if len(sentence) < 20:
            continue
        sentence = sentence.strip()
        # Interrogative: Ends with '?'
        if sentence.endswith('?'):
            interrogative.append(sentence)
        # Exclamatory: Ends with '!'
        elif sentence.endswith('!'):
            exclamatory.append(sentence)
        # Imperative: Starts with a verb or lacks a subject (heuristic)
        elif (sentence.split()[0].lower() in [
            'go', 'come', 'stop', 'run', 'look', 'listen', 'do', 'be', 'take', 'give']
              or len(sentence.split()) < 3):
            imperative.append(sentence)
        # Declarative: Default for sentences ending with '.'
        else:
            declarative.append(sentence)
            if is_simple_declarative(sentence):
                simple.append(sentence)

    return {
        'declarative': declarative,
        'interrogative': interrogative,
        'imperative': imperative,
        'exclamatory': exclamatory,
        'simple': simple,
    }


def is_simple_declarative(input_str):
    """
    Check if a string is a simple declarative statement.
    Returns True if the string meets all conditions, False otherwise.
    """
    # Ensure input is a non-empty string
    if not isinstance(input_str, str) or not input_str.strip():
        return False

    # Remove extra whitespace and ensure string ends with a period
    input_str = input_str.strip()
    if not input_str.endswith('.'):
        return False

    # Tokenize and POS tag
    tokens = word_tokenize(input_str[:-1])  # Remove period for processing
    tagged = pos_tag(tokens)

    # 1. Express a complete thought (has subject and predicate)
    has_subject = False
    has_verb = False
    for word, tag in tagged:
        if tag.startswith('NN') or tag.startswith('PRP'):  # Noun or pronoun (subject)
            has_subject = True
        if tag.startswith('VB'):  # Verb
            has_verb = True

    if not (has_subject and has_verb):
        return False

    # 2. Convey a fact/assertion and 4. Be in indicative mood
    # Check for non-declarative indicators (question words, imperative mood)
    if input_str.startswith(('who', 'what', 'where', 'when', 'why', 'how')) or '?' in input_str:
        return False

    # Check for imperative mood (starts with verb, no subject)
    if tagged[0][1].startswith('VB') and not has_subject:
        return False

    # 5. No subordinate clauses or conjunctions linking multiple clauses
    # Check for subordinating conjunctions or relative pronouns
    subordinators = {'that', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how'}
    coordinators = {'and', 'but', 'or', 'nor', 'for', 'yet', 'so'}

    # Check for commas or conjunctions indicating multiple clauses
    if ',' in input_str or any(word.lower() in subordinators.union(coordinators) for word, _ in tagged):
        return False

    # Basic check for clause structure using regex (simplified)
    # Ensure one subject-verb pair, no embedded clauses
    pattern = r'^\w+\s+\w+\s*.*\.$'
    if not re.match(pattern, input_str):
        return False

    return True


def extract_verbs(sentence: str) -> list[Word]:
    # Tokenize the sentence into words
    tokens = nltk.word_tokenize(sentence)
    # Perform POS tagging
    tagged = nltk.pos_tag(tokens)

    # List to store verb objects
    verbs = []
    # Verb tags in NLTK start with 'VB' (e.g., VB, VBD, VBG, VBN, VBP, VBZ)
    verb_tags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

    for i, (word, tag) in enumerate(tagged):
        if tag in verb_tags:
            verbs.append(Word(id=-1, word=word, nltk_token=tag))

    return verbs


def infer_tense(sentence: str) -> str:
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)

    # Initialize tense indicators
    past = False
    present = False
    future = False

    # Common verb tags
    verb_tags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

    for word, tag in tagged:
        if tag in verb_tags:
            if tag == 'VBD' or tag == 'VBN':  # Past tense verbs
                past = True
            elif tag == 'VBP' or tag == 'VBZ':  # Present tense verbs
                present = True
            elif word.lower() in ['will', 'shall']:  # Future tense indicators
                future = True

    # Determine tense based on indicators
    if future:
        return "Future"
    elif past and not present:
        return "Past"
    elif present and not past:
        return "Present"
    else:
        return "Mixed or unclear"


if __name__ == '__main__':
    setup_nltk() # run this function once upon installing nltk to download word data

    # Example usage
    test_sentences = [
        "The cat sleeps and eats.",  # False (coordinator 'and')
        "Is the cat sleeping?",  # False (question)
        "Sleep now.",  # False (imperative)
        "The cat that runs jumps.",  # False (subordinate clause)
        "Cats.",  # False (incomplete)
        "I did not seem to understand.",  # True
        "Turn off these damn lights.",  # True
        "I interrupted the informational speech."  # True
    ]

    for sentence in test_sentences:
        print(f"'{sentence}' -> {extract_verbs(sentence)}")
