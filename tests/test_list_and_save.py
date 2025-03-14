import io
import sys
import os
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import pytest

from ..src.lister.main import format_file_output, is_skippable_path, should_include_file, get_files_recursively, \
    parse_arguments, SkipDirs, main, remove_empty_lines

SCRIPT_NAME = "list_and_save.py"


def test_skip_dirs_enum():
    assert SkipDirs.PYCACHE.value == "__pycache__"
    assert SkipDirs.GIT.value == ".git"
    assert SkipDirs.NODE_MODULES.value == "node_modules"


@pytest.mark.parametrize("test_input,expected", [
    (Path("/home/user/__pycache__"), True),
    (Path("/home/user/.git"), True),
    (Path("/home/user/node_modules"), True),
    (Path("/home/user/my_project"), False),
    (Path("/home/user/git"), False),
    (Path("/home/user/__pycache__/somefile.py"), True),
    (Path("/home/user/.git/config"), True),
    (Path("__pycache__"), True),
    (Path(".git"), True),
    (Path("node_modules"), True),
    (Path("regular_folder"), False),
    (Path(""), False),
])
def test_is_skippable_path_dirs(test_input, expected):
    assert is_skippable_path(test_input, set(), False) == expected


@pytest.mark.parametrize("test_input,expected", [
    (Path(".hidden_file"), True),
    (Path(".hidden_directory"), True),
    (Path("normal_file.txt"), False),
    (Path("normal_directory"), False),
    (Path("/home/user/.hidden_file"), True),
    (Path("/home/user/.hidden_directory"), True),
    (Path("/home/user/visible_file.txt"), False),
    (Path("/home/user/visible_directory"), False),
    (Path("/home/.user/visible_file.txt"), True),
    (Path("/.hidden/visible_file.txt"), True),
    (Path("."), False),
    (Path(".."), False),
    (Path("./"), False),
    (Path("../"), False),
    (Path("/home/user/./file.txt"), False),
    (Path("/home/user/../file.txt"), False),
    (Path(""), False),
    (Path("/"), False)
])
def test_is_skippable_path_hidden(test_input, expected):
    assert is_skippable_path(test_input, set(), False) == expected


@pytest.mark.parametrize("file_name, skip_patterns, expected", [
    ("example.txt", ["example"], False),
    ("example.txt", [".txt"], False),
    ("example.txt", ["ex", ".txt"], False),
    ("example.txt", ["sample"], True),
    ("example.txt", [".py"], True),
    ("example.txt", [], True),
    ("__init__.py", ["__init__"], False),
    ("__init__.py", [".pyc"], True),
    ("file.pyc", [".pyc"], False),
    ("file.py", ["file", ".pyc"], False),
    ("some_directory/example.txt", ["example"], False),
    ("some_directory/example.txt", ["some_directory"], True),
    ("", ["empty"], True),
    ("file.txt", [""], False),  # Empty string in skip_patterns matches everything
    ("file.TXT", [".txt"], True),  # Case-sensitive
    ("file.txt", ["FILE"], True),  # Case-sensitive
])
def test_should_include_file(file_name, skip_patterns, expected):
    path = Path(file_name)
    assert should_include_file(path, set(), set(skip_patterns)) == expected


def test_get_files_recursively_nested(tmp_path):
    # Create a nested directory structure
    subdir1 = tmp_path / "subdir1"
    subdir1.mkdir()
    subdir2 = subdir1 / "subdir2"
    subdir2.mkdir()
    (tmp_path / "file1.txt").touch()
    (subdir1 / "file2.txt").touch()
    (subdir2 / "file3.txt").touch()
    args = Namespace(include_hidden=False, skip_dirs=[], skip_files=[], include_extension=[".txt"])
    files = list(get_files_recursively(tmp_path, args))
    expected_files = [
        tmp_path / "file1.txt",
        subdir1 / "file2.txt",
        subdir2 / "file3.txt",
    ]
    assert sorted(files) == sorted(expected_files)


def test_get_files_recursively_nonexistent_path():
    args = Namespace(include_hidden=False, skip_dirs=[], skip_files=[], include_extension=[".txt"])
    files = list(get_files_recursively(Path("nonexistent_path"), args))
    assert files == []


def test_parse_arguments_required(mocker):
    test_args = [SCRIPT_NAME, "-f", "file1", "dir1"]
    mocker.patch('sys.argv', test_args)
    args = parse_arguments()
    assert args.files_and_dirs == ["file1", "dir1"]
    assert not args.include_hidden
    assert args.include_extension is None
    assert args.skip_dirs == []
    assert args.skip_files == []


def test_parse_arguments_optional(mocker):
    test_args = [SCRIPT_NAME, "-f", "file1", "-i", "-x", ".py", "--skip_dirs", "dir_to_skip", "--skip_files",
                 "file_to_skip"]
    mocker.patch('sys.argv', test_args)
    args = parse_arguments()
    assert args.files_and_dirs == ["file1"]
    assert args.include_hidden
    assert args.include_extension == [".py"]
    assert args.skip_dirs == ["dir_to_skip"]
    assert args.skip_files == ["file_to_skip"]


def test_parse_arguments_missing_required(mocker):
    test_args = [SCRIPT_NAME]
    mocker.patch('sys.argv', test_args)
    with pytest.raises(SystemExit):
        parse_arguments()


def test_main_output_full_path(tmp_path):
    # Create a temporary directory structure
    file1 = tmp_path / "file1.txt"
    file1.touch()
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    file2 = subdir / "file2.py"
    file2.touch()
    # Redirect stdout to capture print output
    captured_output = io.StringIO()
    sys.stdout = captured_output
    # Mock sys.argv to simulate command line arguments with --full_path
    with patch('sys.argv', ['list_and_save.py', '-f', str(tmp_path), '--full_path']):
        main()
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    # Check for full path in the output
    assert f"File Name: file1.txt, Path: {file1.resolve()}" in output
    assert f"File Name: file2.py, Path: {file2.resolve()}" in output


def test_format_file_output_relative_path_within_cwd(tmp_path, monkeypatch):
    file = tmp_path / "file.txt"
    file.write_text("Sample content")

    monkeypatch.chdir(tmp_path)

    result = format_file_output(file, full_path=False, remove_empty_lines_enabled=False)

    expected_output = f"File Name: file.txt, Path: {file.relative_to(tmp_path)}"
    assert expected_output in result
    
   
def test_format_file_output_full_path(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("Sample content")

    result = format_file_output(file, full_path=True,remove_empty_lines_enabled=False)

    expected_output = f"File Name: file.txt, Path: {file.resolve()}"
    assert expected_output in result

def test_remove_empty_lines():
    content = "line1\n\nline2\n  \nline3\n\n"
    expected = "line1\nline2\nline3"
    assert remove_empty_lines(content) == expected


def test_format_file_output_empty_lines(tmp_path):
    # Create a test file with empty lines
    file = tmp_path / "test.txt"
    content = "line1\n\nline2\n  \nline3\n\n"
    file.write_text(content)

    # Test with remove_empty_lines enabled (default)
    result = format_file_output(file, full_path=False, remove_empty_lines_enabled=True)
    assert "line1\nline2\nline3" in result

    # Test with remove_empty_lines disabled
    result = format_file_output(file, full_path=False, remove_empty_lines_enabled=False)
    assert content in result


@pytest.mark.parametrize("content,expected", [
    ("", ""),  # Empty file
    ("\n\n\n", ""),  # Only empty lines
    ("  \n\t\n ", ""),  # Only whitespace
    ("line1", "line1"),  # Single line without newline
    ("line1\nline2", "line1\nline2"),  # No empty lines
    ("line1\n  \nline2", "line1\nline2"),  # Whitespace line
])
def test_remove_empty_lines_edge_cases(content, expected):
    assert remove_empty_lines(content) == expected