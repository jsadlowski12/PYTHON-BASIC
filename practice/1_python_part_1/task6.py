"""
Write function which receives filename and reads file line by line and returns min and mix integer from file.
Restriction: filename always valid, each line of file contains valid integer value
Examples:
    # file contains following lines:
        10
        -2
        0
        34
    >>> get_min_max('filename')
    (-2, 34)

Hint:
To read file line-by-line you can use this:
with open(filename) as opened_file:
    for line in opened_file:
        ...
"""
from typing import Tuple


def get_min_max(filename: str) -> Tuple[int, int]:
    min_number = 0
    max_number = 0

    with open("data.txt", 'r') as opened_file:
        for line in opened_file:
            number = int(line)

            if number < min_number:
                min_number = number
            elif number > max_number:
                max_number = number

    return min_number, max_number