import pytest

from capstone.src import magic_generator

class TestValidationFunctions:
    def test_validate_path_to_save_files_dot_returns_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert magic_generator.validate_path_to_save_files('.') == tmp_path.as_posix()

    def test_validate_path_to_save_files_absolute_path(self, tmp_path):
        result = magic_generator.validate_path_to_save_files(tmp_path.as_posix())
        assert result == tmp_path.as_posix()

    @pytest.mark.parametrize(
        "bad_input", ["", "/this/path/does/not/exist"]
    )
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