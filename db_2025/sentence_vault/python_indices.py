from random import choice
from string import ascii_lowercase

from black.trans import defaultdict

from db_2025.common.general import ts, duration


def gen_random_string(n_strings: int, length: int) -> list[str]:
    return [''.join(choice(ascii_lowercase) for _ in range(length))
            for _ in range(n_strings)]


def find_in_file(prefix: str, db: list[str]) -> str | None:
    for s in db:
        if s.startswith(prefix):
            return s
    else:
        return None


def extract_bigrams(db: list[str]):
    """
    Gather all bigrams; for each -- remember rows where it appears
    :param db:
    :return:
    """
    result: dict[tuple[str, str], set[int]] = defaultdict(lambda: set())

    for idx, s in enumerate(db):
        for i in range(len(s) - 1):
            bigram = (s[i], s[i + 1])
            result[bigram].add(idx)
    return result


if __name__ == '__main__':
    db = gen_random_string(3 * 10 ** 6, 4)  # 12 MB tekstu
    # for s in db:
    #     print(s)
    st = ts()
    x = find_in_file('fsk.', db)
    print('----')
    print(f'found: {x}, duration:{duration(st)}')
    bgrams = extract_bigrams(db)  # tworzenie indeksu

    # szukanie
    st = ts()
    fs = bgrams[("f", "s")]
    sk = bgrams[("s", "k")]
    kf = bgrams[("k", "f")]
    print(f'found: {fs & sk & kf}, duration:{duration(st)}')
    print(f'bigrams positions for (fs): {len(fs)}')  # len ~= 13k
    print(f'bigrams positions for (sk): {len(sk)}')
    print(f'bigrams positions for (kf): {len(kf)}')
    # łącznie bgrams ma ~26 * 26 * 13000 ~= 9mln elementów ... 72MB ...
    print('-----------')
    print(f'common: {fs & sk & kf}')
