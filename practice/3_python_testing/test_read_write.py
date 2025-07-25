"""
Write tests for python_part_2/task_read_write.py task.
To write files during tests use temporary files:
https://docs.python.org/3/library/tempfile.html
https://docs.pytest.org/en/6.2.x/tmpdir.html
"""

import pytest

from practice.python_part_2.task_read_write import read_files, write_to_file

@pytest.fixture
def mock_files(tmpdir):
    file_1 = tmpdir.join("file_1.txt")
    file_2 = tmpdir.join("file_2.txt")

    file_1.write("Content of file 1")
    file_2.write("Content of file 2")

    return [str(file_1), str(file_2)]

def test_read_files(mock_files):
    result = read_files(mock_files)
    assert result == ["Content of file 1", "Content of file 2"]


def test_write_to_file(tmpdir):
    content = ["Hello", "World"]
    output_file = tmpdir.join("output.txt")

    write_to_file(str(output_file), content)

    with open(str(output_file), 'r') as file:
        content = file.read()

    assert content == "Hello,World"