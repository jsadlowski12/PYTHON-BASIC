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

def parse_command_line() -> argparse.Namespace:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("NUMBER", type=int, help="How many fake records to generate.")
    argument_parser.add_argument('--FIELD=PROVIDER', type=str, nargs="+")

    parsed_args, remaining_args = argument_parser.parse_known_args()

    for argument in remaining_args:
        if "=" in argument:
            field_name, provider_name = argument.split("=", 1)
            setattr(parsed_args, field_name, provider_name)

    return parsed_args


def print_name_address(args: argparse.Namespace) -> None:
    faker_instance = Faker()
    argument_dict = vars(args)

    for record_number in range(args.NUMBER):
        fake_record = {}

        for field_key, provider_value in argument_dict.items():
            if field_key.startswith("--"):
                sanitized_key = field_key[2:]
                generated_data = getattr(faker_instance, provider_value)()
                fake_record[sanitized_key] = generated_data

        print(fake_record)

if __name__ == "__main__":
    command_args = parse_command_line()
    print_name_address(command_args)

"""
Write test for print_name_address function
Use Mock for mocking args argument https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock
Example:
    >>> m = Mock()
    >>> m.method.return_value = 123
    >>> m.method()
    123
"""
