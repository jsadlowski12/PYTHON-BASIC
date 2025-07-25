"""
Write function which receives list of integers. Calculate power of each integer and
subtract difference between original previous value and it's power. For first value subtract nothing.
Restriction:
Examples:
    >>> calculate_power_with_difference([1, 2, 3])
    [1, 4, 7]  # because [1^2, 2^2 - (1^2 - 1), 3^2 - (2^2 - 2)]
"""
from typing import List


def calculate_power_with_difference(ints: List[int]) -> List[int]:
    result = []

    for idx, val in enumerate(ints):
        power = val ** 2
        if idx == 0:
            result.append(power)
        else:
            prev_val = ints[idx - 1]
            prev_power = prev_val ** 2
            adjusted = power - (prev_power - prev_val)
            result.append(adjusted)

    return result