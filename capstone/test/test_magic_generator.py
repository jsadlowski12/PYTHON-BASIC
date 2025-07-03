import pytest
import os
import uuid
import random

from capstone.src import magic_generator

class TestValidationFunctions:
    @pytest.mark.parametrize("path_input", [".", ""])
    def test_validate_path_to_save_files_current_dir(self, tmp_path, monkeypatch, path_input):
        monkeypatch.chdir(tmp_path)
        result = magic_generator.validate_path_to_save_files(path_input)
        assert result == tmp_path.as_posix()

    def test_validate_path_to_save_files_absolute_path(self, tmp_path):
        result = magic_generator.validate_path_to_save_files(tmp_path.as_posix())
        assert result == tmp_path.as_posix()

    @pytest.mark.parametrize("bad_input", ["/this/path/does/not/exist"])
    def test_validate_path_to_save_files_invalid_path(self, bad_input):
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_path_to_save_files(bad_input)
        assert system_info.value.code == 1

    def test_validate_path_to_save_files_file_is_not_directory(self, tmp_path):
        file_path = tmp_path.joinpath("data.txt")
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_path_to_save_files(file_path.as_posix())
        assert system_info.value.code == 1

    def test_validate_files_count_negative_number(self):
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_files_count(-1)
        assert system_info.value.code == 1

    @pytest.mark.parametrize(
        "files_count, expected_result",
        [(0, 0), (1, 1), (2, 2),]
    )
    def test_validate_files_count_zero_and_greater(self, files_count, expected_result):
        result = magic_generator.validate_files_count(files_count)
        assert result == expected_result

    @pytest.mark.parametrize("data_lines", [-1, 0])
    def test_validate_data_lines_negative_number_or_zero(self, data_lines):
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_data_lines(data_lines)
        assert system_info.value.code == 1

    @pytest.mark.parametrize(
        "data_lines, expected_result",
        [(1, 1), (5, 5), (1000, 1000),]
    )
    def test_validate_data_lines_positive_number(self, data_lines, expected_result):
        result = magic_generator.validate_data_lines(data_lines)
        assert result == expected_result

    def test_validate_multiprocessing_negative_number(self):
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_multiprocessing(-1)
        assert system_info.value.code == 1

    def test_validate_multiprocessing_valid(self):
        result = magic_generator.validate_multiprocessing(2)
        assert result == 2

    def test_validate_multiprocessing_above_cpu_count(self, monkeypatch):
        monkeypatch.setattr(os, "cpu_count", lambda: 4)
        result = magic_generator.validate_multiprocessing(10)
        assert result == 4

class TestGenerateFileName:
    def test_generate_file_name_single_file(self):
        result = magic_generator.generate_file_name("test", "any", 1, 0)
        assert result == "test.json"

    def test_count_prefix(self):
        result = magic_generator.generate_file_name("test", "count", 5, 2)
        assert result == "test_2"

    def test_random_prefix(self, monkeypatch):
        monkeypatch.setattr(random, 'randint', lambda x, y: 5678)
        result = magic_generator.generate_file_name("test", "random", 5, 2)
        assert result == "test_5678.json"

    def test_uuid_prefix(self, monkeypatch):
        monkeypatch.setattr(uuid, "uuid4", lambda: uuid.UUID("12345678-1234-5678-1234-567812345678"))
        result = magic_generator.generate_file_name("data", "uuid", 5, 3)
        assert result == "data_12345678-1234-5678-1234-567812345678.json"

    def test_default_case(self):
        result = magic_generator.generate_file_name("test", "unknown", 5, 3)
        assert result == "test_3.json"