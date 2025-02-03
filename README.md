# Files Lister
[![codecov](https://codecov.io/gh/michalsi/lister/graph/badge.svg?token=MXS5ETIC8Q)](https://codecov.io/gh/michalsi/lister)

Files Lister is a Python utility for recursively listing and saving the content of source code files in a directory structure.
It provides flexible options for including or excluding files based on various criteria.

## Features

- Recursively list files in a directory structure
- Include or exclude hidden files and directories
- Filter files by extension
- Skip specified directories and files
- Output full or relative file paths
- Save file contents to an output file

## Installation

To install Files Lister, ensure you have Python 3.9 or later installed. Then, clone this repository:

```bash
git clone https://github.com/yourusername/files_lister.git
cd files_lister
```
This project uses UV (Python packaging in Rust) for dependency management.
If you don't have UV installed, you can install it following the instructions at [UV's official repository](https://github.com/astral-sh/uv).

## Usage
To use Files Lister, run the following command:

```
uv run list_and_save.py [OPTIONS]
```

Options:
- `-f, --files_and_dirs`: File/directory or list of them to process (required)
- `-i, --include_hidden`: Include hidden files and directories
- `-x, --include_extension`: Include only files with specified extensions (e.g., '.txt' '.py')
- `-d, --skip_dirs`: Additional directories to skip
- `-s, --skip_files`: Files or file patterns to skip
- `-q, --quiet`: Do not print output to console
- `--full_path`: Print full path instead of relative path

### Example:
```
uv run list_and_save.py -f "." -x ".py" -d "venv" "build" -s "__init__.py"
```
This command will list all Python files in the current directory, excluding the "venv" and "build" directories, 
and skipping "init.py" files.

## Output
The script generates a file named files_output in the current directory, containing the list of files and their contents.

## Development

UV automatically manages the project environment. To set it up:

```
uv sync
```
This command will create a .venv directory (if it doesn't exist) and install all project dependencies specified in pyproject.toml.

### Running tests
To run the test suite:

```
uv run pytest --basetemp=test_tmp_dir
```
#### Why --basetemp=test_tmp_dir?
The `--basetemp` option is used to specify a custom directory for temporary test files. 
This is particularly important for this project to avoid issues with the default .tmp folder created by `pytest`,
which is typically hidden and would otherwise be excluded by the script's logic.
By using `--basetemp=test_tmp_di`r, we ensure that temporary files do not interfere with the script's file listing and processing behavior.

### Code coverage
To generate a code coverage report:

```
uv run coverage run -m pytest --basetemp=test_tmp_dir
uv run coverage html
```

### Adding Dependencies
To add a new dependency to the project:
```uv add [package_name]```
This will update both `pyproject.toml` and `uv.lock`.

This will create an HTML coverage report in the htmlcov directory.
