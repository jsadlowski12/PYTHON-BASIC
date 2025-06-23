from task_4 import print_name_address
from unittest.mock import Mock, patch
import io
import argparse


def test_print_name_address_one_value():
    expected = {'fake-address': 'address', 'some_name': 'name'}

    m = Mock()
    m.print_name_address.return_value = expected

    assert m.print_name_address() == expected

@patch('sys.stdout', new_callable=io.StringIO)
def test_print_name_address(mock_stdout):
    test_data = {
        "test1": argparse.Namespace(NUMBER=2, **{'--fake-address': 'address', '--some_name': 'name'}),
        "test2": argparse.Namespace(NUMBER=3, **{'--fake_company': 'company', '--fake-color': 'color'}),
    }

    for test_name, args in test_data.items():
        print_name_address(args)
        output = mock_stdout.getvalue().strip().split('\n')

        assert len(output) == args.NUMBER, f"{test_name}: Number of lines mismatch"

        for line in output:
            assert line.startswith('{') and line.endswith('}'), f"{test_name}: Line format error"
            for field in vars(args):
                if field.startswith('--'):
                    key = field.replace('--', '')
                    assert f"'{key}':" in line, f"{test_name}: Missing key {key} in output"

        mock_stdout.truncate(0)
        mock_stdout.seek(0)
