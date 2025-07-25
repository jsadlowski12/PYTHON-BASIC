"""
Write tests for python_part_2/task_read_write_2.py task.
To write files during tests use temporary files:
https://docs.python.org/3/library/tempfile.html
https://docs.pytest.org/en/6.2.x/tmpdir.html
"""
from practice.python_part_2.task_read_write_2 import write_to_file_in_cp1252_encoding, write_to_file_in_utf8_encoding

TEST_INPUT = ['abc', 'def', 'xyz']

def test_write_to_file_in_utf8_encoding(tmpdir):
    temp_file = tmpdir.join("utf8.txt")
    content = TEST_INPUT

    write_to_file_in_utf8_encoding(temp_file, content)

    with open(str(temp_file), 'r') as file:
        content = file.read()

    assert content == "abc\\ndef\\nxyz"

def test_write_to_file_in_cp1252_encoding(tmpdir):
    temp_file = tmpdir.join("cp1252.txt")
    content = TEST_INPUT

    write_to_file_in_cp1252_encoding(temp_file, content)

    with open(str(temp_file), 'r') as file:
        content = file.read()

    assert content == "xyz,def,abc"