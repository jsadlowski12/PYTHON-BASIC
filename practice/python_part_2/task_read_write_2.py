"""
Use function 'generate_words' to generate random words.
Write them to a new file encoded in UTF-8. Separator - '\n'.
Write second file encoded in CP1252, reverse words order. Separator - ','.

Example:
    Input: ['abc', 'def', 'xyz']

    Output:
        file1.txt (content: "abc\ndef\nxyz", encoding: UTF-8)
        file2.txt (content: "xyz,def,abc", encoding: CP1252)
"""


def generate_words(n=20):
    import string
    import random

    words = list()
    for _ in range(n):
        word = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
        words.append(word)

    reversed_words = words[::-1]

    write_to_file_in_utf8_encoding("file1.txt", words)
    write_to_file_in_cp1252_encoding("file2.txt", reversed_words)

    return words

def write_to_file_in_utf8_encoding(filename: str, content: list[str]) -> None:
    with open(filename, 'w', encoding='utf8') as file:
        file.write('\\n'.join(map(str, content)))

def write_to_file_in_cp1252_encoding(filename: str, content: list[str]) -> None:
    with open(filename, 'w', encoding='cp1252') as file:
        file.write(','.join(map(str, content)))

if __name__ == "__main__":
    generate_words()