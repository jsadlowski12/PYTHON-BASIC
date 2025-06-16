"""
Write function which receives line of space sepparated words.
Remove all duplicated words from line.
Restriction:
Examples:
    >>> remove_duplicated_words('cat cat dog 1 dog 2')
    'cat dog 1 2'
    >>> remove_duplicated_words('cat cat cat')
    'cat'
    >>> remove_duplicated_words('1 2 3')
    '1 2 3'
"""


def remove_duplicated_words(line: str) -> str:
    result = []

    for i in line:
        words = line.split()
        seen = set()
        unique_words = []

        for word in words:
            if word not in seen:
                seen.add(word)
                unique_words.append(word)

            if word not in result:
                result.append(word)

    return ' '.join(result)
