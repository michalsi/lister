from argparse import Namespace

import os
import pytest

from ..list_and_save import is_hidden_path, should_skip_file, should_include_file, should_skip_element, \
    is_skippable_dir, DIRS_TO_SKIP


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


def test_should_skip_element():
    # Test regular file
    args = Namespace(include_hidden=False, skip_dirs=[], skip_files=[], include_extension=None)
    assert should_skip_element('/path/to/file.txt', args) == False

    # Test hidden file
    assert should_skip_element('/path/to/.hiddenfile.txt', args) == True

    # Test including hidden files
    args.include_hidden = True
    assert should_skip_element('/path/to/.hiddenfile.txt', args) == False

    # Test skipping specific directories
    args = Namespace(include_hidden=False, skip_dirs=['skip_me'], skip_files=[], include_extension=None)
    assert should_skip_element('/path/to/skip_me/file.txt', args) == True
    assert should_skip_element('/path/to/dont_skip/file.txt', args) == False

    # Test skipping specific files
    args = Namespace(include_hidden=False, skip_dirs=[], skip_files=['skip.txt'], include_extension=None)
    assert should_skip_element('/path/to/skip.txt', args) == True
    assert should_skip_element('/path/to/dont_skip.txt', args) == False

    # Test file extension filter
    args = Namespace(include_hidden=False, skip_dirs=[], skip_files=[], include_extension='.py')
    assert should_skip_element('/path/to/script.py', args) == False
    assert should_skip_element('/path/to/script.txt', args) == True

    # Test combination of filters
    args = Namespace(include_hidden=True, skip_dirs=['node_modules'], skip_files=['*.log'], include_extension='.js')
    assert should_skip_element('/path/to/node_modules/script.js', args) == True  # in skip_dirs
    assert should_skip_element('/path/to/.hidden/script.js', args) == False  # hidden but included
    assert should_skip_element('/path/to/script.log', args) == True  # in skip_files
    assert should_skip_element('/path/to/script.py', args) == True  # not .js extension
    assert should_skip_element('/path/to/script.js', args) == False  # meets all criteria
