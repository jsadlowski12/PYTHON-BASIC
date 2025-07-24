import pytest
import os
import uuid
import random
import json

from capstone.src import main

class TestValidatePathToSaveFilesArgument:
    @pytest.mark.parametrize("path_input", [".", ""])
    def test_current_dir(self, tmp_path, monkeypatch, path_input):
        monkeypatch.chdir(tmp_path)
        result = main.validate_path_to_save_files(path_input)
        assert result == tmp_path.as_posix()

    def test_absolute_path(self, tmp_path):
        result = main.validate_path_to_save_files(tmp_path.as_posix())
        assert result == tmp_path.as_posix()

    def test_invalid_path(self):
        with pytest.raises(SystemExit) as system_info:
            main.validate_path_to_save_files("/this/path/does/not/exist")
        assert system_info.value.code == 1

    def test_is_not_a_directory(self, tmp_path):
        file_path = tmp_path.joinpath("data.txt")
        file_path.touch()  # Create the file
        with pytest.raises(SystemExit) as system_info:
            main.validate_path_to_save_files(file_path.as_posix())
        assert system_info.value.code == 1


class TestValidateFilesCountArgument:
    def test_negative_count(self):
        with pytest.raises(SystemExit) as system_info:
            main.validate_files_count(-1)
        assert system_info.value.code == 1

    @pytest.mark.parametrize("files_count", [0, 1, 2, 10])
    def test_valid_counts(self, files_count):
        result = main.validate_files_count(files_count)
        assert result == files_count


class TestValidateDataLinesArgument:
    @pytest.mark.parametrize("data_lines", [-1, 0])
    def test_invalid_data_lines(self, data_lines):
        with pytest.raises(SystemExit) as system_info:
            main.validate_data_lines(data_lines)
        assert system_info.value.code == 1

    @pytest.mark.parametrize("data_lines", [1, 5, 1000])
    def test_valid_data_lines(self, data_lines):
        result = main.validate_data_lines(data_lines)
        assert result == data_lines


class TestValidateMultiprocessingArgument:
    def test_negative_number(self):
        with pytest.raises(SystemExit) as system_info:
            main.validate_multiprocessing(-1)
        assert system_info.value.code == 1

    def test_valid_input(self):
        result = main.validate_multiprocessing(2)
        assert result == 2

    def test_above_cpu_count(self, monkeypatch):
        monkeypatch.setattr(os, "cpu_count", lambda: 4)
        result = main.validate_multiprocessing(10)
        assert result == 4


class TestValidateDataSchemaArgument:
    @pytest.mark.parametrize("schema,should_pass", [
        ({"name": "str:rand", "age": "int:rand(1, 100)"}, True),
        ({"id": "int:rand", "status": "str:['active', 'inactive']"}, True),
        ({"timestamp": "timestamp:", "value": "int:42"}, True),
        ({"email": "str:user@example.com"}, True),
        ({"scores": "int:[10, 20, 30, 40, 50]"}, True),
        ({"name": "str:rand", "empty_field": "str:"}, True),
        ({"name": "strrand"}, False),  # Missing colon
        ({"date": "timestamp:rand"}, False),  # Invalid timestamp instruction
        ({"score": "int:rand(100, 10)"}, False),  # Invalid range bounds
        ({"role": "str:[admin, user]"}, False),  # Invalid JSON in list
        ({"level": "int:[1, '2', 3]"}, False),  # Mixed types in list
        ({}, False),  # Empty schema
    ])
    def test_schema_validation(self, schema, should_pass):
        if should_pass:
            main.validate_data_schema(schema)
        else:
            with pytest.raises(SystemExit):
                main.validate_data_schema(schema)

    def test_schema_not_dict(self):
        with pytest.raises(SystemExit) as system_info:
            main.validate_data_schema("not_a_dict")
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
            main.validate_data_schema(schema)
        assert system_info.value.code == 1

    def test_invalid_constant_int(self):
        schema = {"count": "int:forty"}
        with pytest.raises(SystemExit) as system_info:
            main.validate_data_schema(schema)
        assert system_info.value.code == 1

    def test_rand_range_invalid_type(self):
        schema = {"username": "str:rand(1, 3)"}
        with pytest.raises(SystemExit) as system_info:
            main.validate_data_schema(schema)
        assert system_info.value.code == 1


class TestJSONSchemaLoader:
    @pytest.fixture
    def valid_schema_file(self, tmp_path):
        schema_data = {
            "user_id": "int:rand(1, 1000)",
            "username": "str:rand",
            "email": "str:user@domain.com",
            "status": "str:['active', 'inactive', 'pending']",
            "created_at": "timestamp:"
        }
        schema_file = tmp_path.joinpath("valid_schema.json")
        schema_file.write_text(json.dumps(schema_data))
        return str(schema_file), schema_data

    @pytest.fixture
    def invalid_json_file(self, tmp_path):
        invalid_file = tmp_path.joinpath("invalid_schema.json")
        invalid_file.write_text('{"name": "str:rand", "age": invalid_json}')
        return str(invalid_file)

    def test_correct_schema(self, valid_schema_file):
        file_path, expected_data = valid_schema_file
        result = main.load_json_data_schema(file_path)
        assert result == expected_data

    def test_file_not_found(self, tmp_path):
        fake_file = tmp_path.joinpath("non_existent_schema.json")
        with pytest.raises(SystemExit) as system_info:
            main.load_json_data_schema(str(fake_file))
        assert system_info.value.code == 1

    def test_invalid_json_file(self, invalid_json_file):
        with pytest.raises(SystemExit) as system_info:
            main.load_json_data_schema(invalid_json_file)
        assert system_info.value.code == 1


class TestGenerateFileName:
    def test_generate_file_name_single_file(self):
        result = main.generate_file_name("test", "any", 1, 0)
        assert result == "test.json"

    def test_count_prefix(self):
        result = main.generate_file_name("test", "count", 5, 2)
        assert result == "test_2"

    def test_random_prefix(self, monkeypatch):
        monkeypatch.setattr(random, 'randint', lambda x, y: 5678)
        result = main.generate_file_name("test", "random", 5, 2)
        assert result == "test_5678.json"

    def test_uuid_prefix(self, monkeypatch):
        monkeypatch.setattr(uuid, "uuid4", lambda: uuid.UUID("12345678-1234-5678-1234-567812345678"))
        result = main.generate_file_name("data", "uuid", 5, 3)
        assert result == "data_12345678-1234-5678-1234-567812345678.json"

    def test_default_case(self):
        result = main.generate_file_name("test", "unknown", 5, 3)
        assert result == "test_3.json"


class TestGenerateValue:
    @pytest.mark.parametrize("data_type,instruction,expected_type", [
        ("str", "rand", str),
        ("int", "rand", int),
        ("str", "constant_value", str),
        ("int", "42", int),
        ("str", '["option1", "option2"]', str),
        ("int", "[1, 2, 3]", int),
        ("str", "", str),
        ("timestamp", "", float),
    ])
    def test_generate_value_different_types(self, data_type, instruction, expected_type):
        result = main.generate_value(data_type, instruction)
        if result is not None:
            assert isinstance(result, expected_type)

    def test_empty_instruction_behaviors(self):
        result = main.generate_value("str", "")
        assert result == ""

        result = main.generate_value("int", "")
        assert result is None

    def test_rand_instruction_behaviors(self):
        result = main.generate_value("str", "rand")
        assert isinstance(result, str)
        uuid.UUID(result)

        result = main.generate_value("int", "rand")
        assert isinstance(result, int)
        assert 0 <= result <= 10000

    @pytest.mark.parametrize("instruction,expected_range", [
        ("rand(10, 20)", (10, 20)),
        ("rand( 5 , 15 )", (5, 15)),
    ])
    def test_rand_range_instruction(self, instruction, expected_range):
        result = main.generate_value("int", instruction)
        assert isinstance(result, int)
        assert expected_range[0] <= result <= expected_range[1]

    @pytest.mark.parametrize("data_type,instruction,options", [
        ("str", '["apple", "banana", "cherry"]', ["apple", "banana", "cherry"]),
        ("int", "[10, 20, 30, 42]", [10, 20, 30, 42]),
        ("str", '["only_option"]', ["only_option"]),
        ("str", '["hello world", "test-123", ""]', ["hello world", "test-123", ""]),
    ])
    def test_list_instruction(self, data_type, instruction, options):
        result = main.generate_value(data_type, instruction)
        assert result in options

    @pytest.mark.parametrize("data_type,instruction,expected", [
        ("str", "hello world", "hello world"),
        ("str", "123", "123"),
        ("int", "123", 123),
        ("int", "-456", -456),
        ("int", "0", 0),
    ])
    def test_constant_instruction(self, data_type, instruction, expected):
        result = main.generate_value(data_type, instruction)
        assert result == expected


class TestGenerateDataRecord:
    def test_single_field_string(self, monkeypatch):
        monkeypatch.setattr("capstone.src.main.generate_value",
                            lambda t, i: "test_string")

        schema = {"name": "string:random"}
        record = main.generate_data_record(schema)

        assert record == {"name": "test_string"}


class TestOutputOperations:
    def test_print_data_to_console(self, capfd):
        data = [{"name": "Jacob"}, {"name": "Bob"}]
        main.print_data_to_console(data)

        out, err = capfd.readouterr()
        assert '"name": "Jacob"' in out
        assert '"name": "Bob"' in out

    def test_saves_data_successfully(self, tmp_path):
        data = [{"city": "Cracow"}, {"city": "London"}]
        file_path = tmp_path.joinpath("output.json")

        main.save_data_to_file(data, str(file_path))

        with open(file_path) as f:
            saved = json.load(f)

        assert saved == data


class TestMultiprocessingLogic:
    def test_single_file_and_process(self):
        result = main.distribute_files_across_processes(1, 1)
        expected = [[1]]
        assert result == expected

    def test_even_distribution(self):
        result = main.distribute_files_across_processes(10, 5)
        expected = [
            [1, 2],
            [3, 4],
            [5, 6],
            [7, 8],
            [9, 10]
        ]
        assert result == expected

    def test_uneven_distribution(self):
        result = main.distribute_files_across_processes(10, 3)
        expected = [
            [1, 2, 3, 4],
            [5, 6, 7],
            [8, 9, 10]
        ]
        assert result == expected