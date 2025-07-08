import pytest
import os
import uuid
import random
import json

from capstone.src import magic_generator

class TestValidatePathToSaveFilesArgument:
    @pytest.mark.parametrize("path_input", [".", ""])
    def test_current_dir(self, tmp_path, monkeypatch, path_input):
        monkeypatch.chdir(tmp_path)
        result = magic_generator.validate_path_to_save_files(path_input)
        assert result == tmp_path.as_posix()

    def test_absolute_path(self, tmp_path):
        result = magic_generator.validate_path_to_save_files(tmp_path.as_posix())
        assert result == tmp_path.as_posix()

    @pytest.mark.parametrize("bad_input", ["/this/path/does/not/exist"])
    def test_invalid_path(self, bad_input):
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_path_to_save_files(bad_input)
        assert system_info.value.code == 1

    def test_is_not_a_directory(self, tmp_path):
        file_path = tmp_path.joinpath("data.txt")
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_path_to_save_files(file_path.as_posix())
        assert system_info.value.code == 1

class TestValidateFilesCountArgument:
    def test_negative_count(self):
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_files_count(-1)
        assert system_info.value.code == 1

    @pytest.mark.parametrize(
        "files_count, expected_result",
        [(0, 0), (1, 1), (2, 2),]
    )
    def test_count_zero_and_greater(self, files_count, expected_result):
        result = magic_generator.validate_files_count(files_count)
        assert result == expected_result

class TestValidateDataLinesArgument:
    @pytest.mark.parametrize("data_lines", [-1, 0])
    def test_negative_number_or_zero(self, data_lines):
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_data_lines(data_lines)
        assert system_info.value.code == 1

    @pytest.mark.parametrize(
        "data_lines, expected_result",
        [(1, 1), (5, 5), (1000, 1000),]
    )
    def test_valid_number(self, data_lines, expected_result):
        result = magic_generator.validate_data_lines(data_lines)
        assert result == expected_result

class TestValidateMultiprocessingArgument:
    def test_negative_number(self):
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_multiprocessing(-1)
        assert system_info.value.code == 1

    def test_valid_input(self):
        result = magic_generator.validate_multiprocessing(2)
        assert result == 2

    def test_above_cpu_count(self, monkeypatch):
        monkeypatch.setattr(os, "cpu_count", lambda: 4)
        result = magic_generator.validate_multiprocessing(10)
        assert result == 4

class TestValidateDataSchemaArgument:
    def test_schema_not_dict(self):
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_data_schema("not_a_dict")
        assert system_info.value.code == 1

    def test_empty_schema(self):
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_data_schema({})
        assert system_info.value.code == 1

    def test_missing_colon(self):
        schema = {"name": "strrand"}
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_data_schema(schema)
        assert system_info.value.code == 1

    def test_rand_invalid_type(self):
        schema = {"date": "timestamp:rand"}
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_data_schema(schema)
        assert system_info.value.code == 1

    def test_rand_range_invalid_type(self):
        schema = {"username": "str:rand(1, 3)"}
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_data_schema(schema)
        assert system_info.value.code == 1

    def test_rand_range_bounds_invalid(self):
        schema = {"score": "int:rand(100, 10)"}
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_data_schema(schema)
        assert system_info.value.code == 1

    @pytest.mark.parametrize("value", [
        "int:rand(5)",
        "int:rand(a, b)",
        "int:rand(1, 2, 3)",
        "int:rand()"
    ])
    def test_rand_range_bad_format(self, value):
        schema = {"score": value}
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_data_schema(schema)
        assert system_info.value.code == 1

    def test_invalid_list_json(self):
        schema = {"role": "str:[admin, user]"}
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_data_schema(schema)
        assert system_info.value.code == 1

    def test_list_wrong_element_type(self):
        schema = {"level": "int:[1, '2', 3]"}
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_data_schema(schema)
        assert system_info.value.code == 1

    def test_invalid_constant_int(self):
        schema = {"count": "int:forty"}
        with pytest.raises(SystemExit) as system_info:
            magic_generator.validate_data_schema(schema)
        assert system_info.value.code == 1

class TestJSONSchemaLoader:
    def test_correct_schema(self, tmp_path):
        schema_data = {"date":"timestamp:", "name": "str:rand",
                       "type":"str:['client', 'partner', 'government']", "age": "int:rand(1, 90)"}
        schema_file = tmp_path.joinpath("schema.json")
        schema_file.write_text(json.dumps(schema_data))

        result = magic_generator.load_json_data_schema(str(schema_file))
        assert result == schema_data

    def test_file_not_found(self, tmp_path):
        fake_file = tmp_path / "non_existent_schema.json"
        assert not fake_file.exists()

        with pytest.raises(SystemExit) as system_info:
            magic_generator.load_json_data_schema(str(fake_file))

        assert system_info.value.code == 1

    def test_invalid_json_string(self):
        invalid_json = '{"foo": "bar", "baz": qux}'

        with pytest.raises(SystemExit) as system_info:
            magic_generator.load_json_data_schema(invalid_json)

        assert system_info.value.code == 1

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