import os
import sys
from argparse import Namespace
import logging
from io import StringIO
from unittest.mock import patch

import pytest

from ..list_and_save import is_hidden_path, should_skip_file, should_include_file, should_skip_element, \
    is_skippable_dir, DIRS_TO_SKIP, get_files_recursively, parse_arguments, main

SCRIPT_NAME = "list_and_save.py"

@pytest.mark.parametrize("test_input,expected", [
    ("/home/user/__pycache__", True),
    ("/home/user/.git", True),
    ("/home/user/node_modules", True),
    ("/home/user/my_project", False),
    ("/home/user/git", False),
    ("/home/user/__pycache__/somefile.py", True),
    ("/home/user/.git/config", True),
    ("__pycache__", True),
    (".git", True),
    ("node_modules", True),
    ("regular_folder", False),
    ("", False),
])
def test_is_skippable_dir(test_input, expected):
    assert is_skippable_dir(test_input) == expected


def test_dirs_to_skip_content():
    assert "__pycache__" in DIRS_TO_SKIP
    assert ".git" in DIRS_TO_SKIP
    assert "node_modules" in DIRS_TO_SKIP


def test_is_skippable_dir_with_custom_dir():
    from ..list_and_save import DIRS_TO_SKIP  # Import DIRS_TO_SKIP at the beginning of the function
    custom_dir = "custom_skip_dir"
    original_dirs_to_skip = DIRS_TO_SKIP.copy()

    assert not is_skippable_dir(custom_dir)

    DIRS_TO_SKIP.add(custom_dir)
    assert is_skippable_dir(custom_dir)

    DIRS_TO_SKIP.clear()
    DIRS_TO_SKIP.update(original_dirs_to_skip)


@pytest.mark.parametrize("test_input,expected", [
    (".hidden_file", True),
    (".hidden_directory", True),
    ("normal_file.txt", False),
    ("normal_directory", False),
    ("/home/user/.hidden_file", True),
    ("/home/user/.hidden_directory", True),
    ("/home/user/visible_file.txt", False),
    ("/home/user/visible_directory", False),
    ("/home/.user/visible_file.txt", True),
    ("/.hidden/visible_file.txt", True),
    (".", False),
    ("..", False),
    ("./", False),
    ("../", False),
    ("/home/user/./file.txt", False),
    ("/home/user/../file.txt", False),
    ("", False),
    ("/", False)
])
def test_is_hidden_path(test_input, expected):
    assert is_hidden_path(test_input) == expected


def test_is_hidden_path_with_os_specific_paths():
    # Create a list of test cases with both Unix and Windows style paths
    test_cases = [
        (".hidden_file", True),
        ("visible_file", False),
        (os.path.join("visible_dir", ".hidden_file"), True),
        (os.path.join(".hidden_dir", "visible_file"), True),
        (os.path.join("visible_dir", "visible_file"), False),
        (os.path.join(".", "visible_file"), False),
        (os.path.join("..", "visible_file"), False),
    ]
    for path, expected in test_cases:
        assert is_hidden_path(path) == expected, f"Failed for path: {path}"


def test_is_hidden_path_with_absolute_paths():
    root = os.path.abspath(os.sep)
    test_cases = [
        (os.path.join(root, ".hidden_file"), True),
        (os.path.join(root, "visible_file"), False),
        (os.path.join(root, "visible_dir", ".hidden_file"), True),
        (os.path.join(root, ".hidden_dir", "visible_file"), True),
        (os.path.join(root, "visible_dir", "visible_file"), False),
    ]
    for path, expected in test_cases:
        assert is_hidden_path(path) == expected, f"Failed for path: {path}"


def test_should_include_file():
    test_cases = [
        ("example.txt", ".txt", True),
        ("example.py", ".py", True),
        ("example.txt", ".py", False),
        ("example.txt", None, True),
        ("example", ".txt", False),
        ("example.txt.bak", ".txt", False),
        ("/path/to/example.txt", ".txt", True),
        ("/path/to/example.py", ".txt", False),
        ("", ".txt", False),
        ("example.TXT", ".txt", False),  # Case-sensitive
        ("example.txt", "", True),
        ("example.txt", ".", False),
    ]
    for file_path, include_extension, expected in test_cases:
        result = should_include_file(file_path, include_extension)
        assert result == expected, f"Failed for file: {file_path}, extension: {include_extension}"


def test_should_skip_file():
    test_cases = [
        # (file_name, skip_patterns, expected_result)
        ("example.txt", ["example"], True),
        ("example.txt", [".txt"], True),
        ("example.txt", ["ex", ".txt"], True),
        ("example.txt", ["sample"], False),
        ("example.txt", [".py"], False),
        ("example.txt", [], False),
        ("__init__.py", ["__init__"], True),
        ("__init__.py", [".pyc"], False),
        ("file.pyc", [".pyc"], True),
        ("file.py", ["file", ".pyc"], True),
        ("some_directory/example.txt", ["example"], True),
        ("some_directory/example.txt", ["some_directory"], True),
        ("", ["empty"], False),
        ("file.txt", [""], True),  # Empty string in skip_patterns matches everything
        ("file.TXT", [".txt"], False),  # Case-sensitive
        ("file.txt", ["FILE"], False),  # Case-sensitive
    ]

    for file_name, skipp_patterns, expected in test_cases:
        result = should_skip_file(file_name, skipp_patterns)
        assert result == expected, f"Failed for file: {file_name}, patterns: {skipp_patterns}"


def test_should_skip_element(tmp_path):

    # Create temporary files and directories
    regular_file = tmp_path / "file.txt"
    regular_file.touch()  # Create the file
    args = Namespace(include_hidden=False, skip_dirs=[], skip_files=[], include_extension=None)
    assert not should_skip_element(str(regular_file), args)

    hidden_file = tmp_path / ".hiddenfile.txt"
    hidden_file.touch()  # Create the hidden file
    assert should_skip_element(str(hidden_file), args)

    args.include_hidden = True
    assert not should_skip_element(str(hidden_file), args)

    # Test skipping specific directories
    skip_me_dir = tmp_path / "skip_me"
    skip_me_dir.mkdir()  # Create the directory
    file_in_skip_me = skip_me_dir / "file.txt"
    file_in_skip_me.touch()  # Create the file
    dont_skip_dir = tmp_path / "dont_skip"
    dont_skip_dir.mkdir()  # Create the directory
    file_in_dont_skip = dont_skip_dir / "file.txt"
    file_in_dont_skip.touch()  # Create the file

    args = Namespace(include_hidden=False, skip_dirs=['skip_me'], skip_files=[], include_extension=None)
    assert should_skip_element(str(file_in_skip_me), args)
    assert not should_skip_element(str(file_in_dont_skip), args)

    # Test skipping specific files
    skip_file = tmp_path / "skip.txt"
    skip_file.touch()  # Create the file
    args = Namespace(include_hidden=False, skip_dirs=[], skip_files=['skip.txt'], include_extension=None)
    assert should_skip_element(str(skip_file), args)
    assert not should_skip_element(str(regular_file), args)

    # Test file extension filter
    script_py = tmp_path / "script.py"
    script_py.touch()  # Create the file
    script_txt = tmp_path / "script.txt"
    script_txt.touch()  # Create the file
    args = Namespace(include_hidden=False, skip_dirs=[], skip_files=[], include_extension='.py')
    assert not should_skip_element(str(script_py), args)
    assert should_skip_element(str(script_txt), args)

    # Test combination of filters
    args = Namespace(include_hidden=True, skip_dirs=['node_modules'], skip_files=['*.log'], include_extension='.js')
    node_modules_dir = tmp_path / "node_modules"
    node_modules_dir.mkdir()  # Create the directory
    script_js = node_modules_dir / "script.js"
    script_js.touch()  # Create the file
    hidden_script_js = tmp_path / ".hidden" / "script.js"
    hidden_script_js.parent.mkdir()  # Create the hidden directory
    hidden_script_js.touch()  # Create the file
    script_log = tmp_path / "script.log"
    script_log.touch()  # Create the file

    assert should_skip_element(str(script_js), args)  # in skip_dirs
    assert not should_skip_element(str(hidden_script_js), args)  # hidden but included
    assert should_skip_element(str(script_log), args)  # in skip_files
    assert should_skip_element(str(script_py), args)  # not .js extension


def test_get_files_recursively_nested(tmp_path):
    # Create a nested directory structure
    subdir1 = tmp_path / "subdir1"
    subdir1.mkdir()
    subdir2 = subdir1 / "subdir2"
    subdir2.mkdir()
    (tmp_path / "file1.txt").touch()
    (subdir1 / "file2.txt").touch()
    (subdir2 / "file3.txt").touch()
    args = Namespace(include_hidden=False, skip_dirs=[], skip_files=[], include_extension=".txt")
    files = get_files_recursively(str(tmp_path), args)
    expected_files = [
        str(tmp_path / "file1.txt"),
        str(subdir1 / "file2.txt"),
        str(subdir2 / "file3.txt"),
    ]
    assert sorted(files) == sorted(expected_files)

def test_get_files_recursively_nonexistent_path():
    args = Namespace(include_hidden=False, skip_dirs=[], skip_files=[], include_extension=".txt")
    files = get_files_recursively("nonexistent_path", args)
    assert files == []  # Assert that the returned list is empty


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
    test_args = [SCRIPT_NAME, "-f", "file1", "-i", "-x", ".py", "--skip_dirs", "dir_to_skip", "--skip_files", "file_to_skip"]
    mocker.patch('sys.argv', test_args)
    args = parse_arguments()
    assert args.files_and_dirs == ["file1"]
    assert args.include_hidden
    assert args.include_extension == ".py"
    assert args.skip_dirs == ["dir_to_skip"]
    assert args.skip_files == ["file_to_skip"]

def test_parse_arguments_missing_required(mocker):
    test_args = [SCRIPT_NAME]
    mocker.patch('sys.argv', test_args)
    with pytest.raises(SystemExit):
        parse_arguments()