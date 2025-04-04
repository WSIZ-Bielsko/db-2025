from random import sample


def randomize_strings_interior(word: str) -> str:
    return word[0] + ''.join(sample(list(word[1:-1]), len(word)-2)) + word[-1] if len(word) > 1 else word


if __name__ == '__main__':
    z = 'kadabra'
    for _ in range(10):
        print(randomize_strings_interior('aaabbbcccddd'))

    print(sample('aaabbbcccddd', k=10))
