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
    previous_value = 0
    previous_value_power = 0
    new_value = 0

    for i in ints:
        if i == 0:
            previous_value = ints[i]
            previous_value_power = previous_value**2
            ints[i] = previous_value_power
            continue

        new_value = ints[i]**2 - (previous_value_power - previous_value)
        previous_value = ints[i]
        previous_value_power = previous_value**2
        ints[i] = new_value
