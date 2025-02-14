# Files Lister

Files Lister is a Python utility designed to recursively list and save the content of source code files in a directory structure. It offers flexible options for including or excluding files based on various criteria, making it a handy tool for developers who need to manage and review project files efficiently.

## Features

- Recursively list files within directory structures
- Option to include or exclude hidden files and directories
- Filter files by specific extensions (e.g., `.txt`, `.py`)
- Skip specified directories and file patterns
- Output full or relative file paths
- Save file contents to an output file

## Installation

To install Files Lister, ensure you have Python 3.9 or later and `pipx` installed. You can install `pipx` via:

```bash
brew install pipx
pipx ensurepath
```

Then, install Files Lister:

```bash
pipx install files-lister
```

This will make the files-lister command available globally on your system.

## Usage
To use Files Lister, execute the following command:

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


## Example Command:
To list all Python files in the current directory, excluding venv and build directories, and skipping __init__.py files:

```bash
files-lister -f "." -x ".py" -d "venv" "build" -s "__init__.py"
```

### Output
The command generates a file named files_output in the current directory, containing the list of files and their contents.

## License
Files Lister is licensed under the MIT License. See the LICENSE file for more details.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request on [GitHub](https://github.com/michalsi/lister).