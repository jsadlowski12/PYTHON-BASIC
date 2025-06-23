"""
Create virtual environment and install Faker package only for this venv.
Write command line tool which will receive int as a first argument and one or more named arguments
 and generates defined number of dicts separated by new line.
Exec format:
`$python task_4.py NUMBER --FIELD=PROVIDER [--FIELD=PROVIDER...]`
where:
NUMBER - positive number of generated instances
FIELD - key used in generated dict
PROVIDER - name of Faker provider
Example:
`$python task_4.py 2 --fake-address=address --some_name=name`
{"some_name": "Chad Baird", "fake-address": "62323 Hobbs Green\nMaryshire, WY 48636"}
{"some_name": "Courtney Duncan", "fake-address": "8107 Nicole Orchard Suite 762\nJosephchester, WI 05981"}
"""

import argparse
from faker import Faker


def print_name_address(args: argparse.Namespace) -> None:
    fake = Faker()
    fields = vars(args)

    for i in range(args.NUMBER):
        fake_dict = {}
        for f, v in fields.items():
            if f.startswith("--"):
                fake_dict[f.replace("--", "")] = eval(f"fake.{v}()")
        print(fake_dict)

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('NUMBER', type=int)
    parser.add_argument('--FIELD=PROVIDER', type=str, nargs="+")

    known_args, keys_vals = parser.parse_known_args()

    for kv in keys_vals:
        key, value = kv.split("=")
        setattr(known_args, key, value)

    return known_args


if __name__ == '__main__':
    parsed_args = get_args()
    print_name_address(parsed_args)

"""
Write test for print_name_address function
Use Mock for mocking args argument https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock
Example:
    >>> m = Mock()
    >>> m.method.return_value = 123
    >>> m.method()
    123
"""
