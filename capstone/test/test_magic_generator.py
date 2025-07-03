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
        with pytest.raises(SystemExit) as excinfo:
            magic_generator.validate_path_to_save_files(bad_input)
        assert excinfo.value.code == 1

    def test_validate_path_to_save_files_file_is_not_directory(self, tmp_path):
        file_path = tmp_path / "data.txt"
        file_path.write_text("hello")
        with pytest.raises(SystemExit):
            magic_generator.validate_path_to_save_files(file_path.as_posix())