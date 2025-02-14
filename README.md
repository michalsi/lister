# Files Lister
[![codecov](https://codecov.io/gh/michalsi/lister/graph/badge.svg?token=MXS5ETIC8Q)](https://codecov.io/gh/michalsi/lister)
[![Worker CI](https://github.com/michalsi/lister/actions/workflows/ci.yml/badge.svg)](https://github.com/michalsi/lister/actions/workflows/ci.yml)

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

### Using pipx

To install Files Lister using `pipx`, ensure you have Python 3.9 or later and `pipx` installed. You can install `pipx` with:

```bash
brew install pipx
pipx ensurepath
```

Then, install Files Lister:

```bash
pipx install files-lister
```

This will make the list_files command available globally on your system.

## Usage
To use Files Lister, run the following command:
```bash
files-lister [OPTIONS]
```

### Options:
`-f`, `--files_and_dirs`: File/directory or list of them to process (required)

`-i`, `--include_hidden`: Include hidden files and directories

`-x`, `--include_extension`: Include only files with specified extensions (e.g., '.txt' '.py')

`-d`, `--skip_dirs`: Additional directories to skip

`-s`, `--skip_files`: Files or file patterns to skip

`-q`, `--quiet`: Do not print output to console

`--full_path`: Print full path instead of relative path

### Example:
```bash
files-lister -f "." -x ".py" -d "venv" "build" -s "__init__.py"
```
This command will list all Python files in the current directory, excluding the "venv" and "build" directories, and skipping "init.py" files.

## Output
The script generates a file named files_output in the current directory, containing the list of files and their contents.

## Development
For development purposes, if you are using UV (Python packaging in Rust) for dependency management, you can set up the environment with:

```bash
uv sync
```

## Running tests
To run the test suite with UV:
```bash
uv run pytest --basetemp=test_tmp_dir
```

### Why `--basetemp=test_tmp_dir`?

The `--basetemp` option specifies a custom directory for temporary test files. This prevents issues with the default `.tmp` folder created by pytest, ensuring temporary files do not interfere with the script's logic.

## Code coverage
To generate a code coverage report:

```bash
uv run coverage run -m pytest --basetemp=test_tmp_dir
uv run coverage html
```

## Adding Dependencies
To add a new dependency to the project using UV:
```bash
uv add [package_name]
```

This will update both pyproject.toml and uv.lock.

## Building and Publishing
To build your project and prepare it for distribution, run:

```bash
uv build
```
This command will generate the necessary distribution files in the dist directory.

To upload your package to PyPI, ensure you have twine installed, and then execute:

```bash
uv run twine upload dist/*
```
This will upload your package to PyPI, making it available for others to install.