import argparse
from enum import Enum
from pathlib import Path
from typing import Set, List, Iterator, Tuple


class SkipDirs(Enum):
    PYCACHE = "__pycache__"
    GIT = ".git"
    NODE_MODULES = "node_modules"
    VENV = "venv"


SKIP_DIRS_VALUES = frozenset(skip_dir.value for skip_dir in SkipDirs)


def is_skippable_path(path: Path, skip_dirs: Set[str], include_hidden: bool) -> bool:
    """Determine if a given path should be skipped based on the directory and visibility criteria."""

    def is_special_directory(name: str) -> bool:
        """Check if the directory is a special directory (i.e., '.' or '..')."""
        return name in {'.', '..'}

    def contains_skip_directories(path_parts: Tuple[str, ...]) -> bool:
        """Check if any part of the path matches the directories to skip."""
        return any(part in SKIP_DIRS_VALUES or part in skip_dirs for part in path_parts)

    def is_hidden(name: str) -> bool:
        """Check if a file or directory is hidden."""
        return name.startswith('.') and not is_special_directory(name)

    def has_hidden_parents(path_parts: Tuple[str, ...]) -> bool:
        """Check if any parent directory in the path is hidden."""
        return any(is_hidden(part) for part in path_parts[:-1])

    if is_special_directory(path.name):
        return False

    path_parts = path.parts

    if contains_skip_directories(path_parts):
        return True

    if not include_hidden:
        if is_hidden(path.name) or has_hidden_parents(path_parts):
            return True

    return False


def should_include_file(file_path: Path, include_extensions: Set[str], skip_files: Set[str]) -> bool:
    """Check if a file should be included based on extension and skip patterns."""
    return (
            (not include_extensions or file_path.suffix in include_extensions)
            and not any(pattern in file_path.name for pattern in skip_files)
    )


def get_files_recursively(path: Path, args: argparse.Namespace) -> Iterator[Path]:
    """Recursively get files from a directory based on given criteria."""
    skip_dirs = set(args.skip_dirs)
    include_extensions = set(args.include_extension or [])
    skip_files = set(args.skip_files)

    for item in path.rglob('*'):
        if item.is_file():
            if not is_skippable_path(item, skip_dirs, args.include_hidden) and \
                    should_include_file(item, include_extensions, skip_files):
                yield item
    # Add this line for debugging


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="List and save content of source code files.")
    parser.add_argument("-f", "--files_and_dirs", nargs="+", required=True, help="File/dir or list them to process")
    parser.add_argument("-i", "--include_hidden", action="store_true",
                        help="Include hidden files and directories (by default, they are excluded)")
    parser.add_argument("-x", "--include_extension", nargs="+", type=str,
                        help="Include only files with these extensions (e.g., '.txt' '.py')")
    parser.add_argument("-d", "--skip_dirs", nargs="+", default=[], help="Additional directories to skip")
    parser.add_argument("-s", "--skip_files", nargs="+", default=[],
                        help="Files or file patterns to skip (e.g., '__init__.py' or '.pyc')")
    parser.add_argument("-r", "--remove_empty_lines", action="store_false",
                        help="Keep empty lines in output (by default, empty lines are removed)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Do not print output to console")
    parser.add_argument("--full_path", action="store_true", help="Print full path instead of relative path")

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    files_to_parse: List[Path] = []
    output_lines: List[str] = []

    for item in args.files_and_dirs:
        path = Path(item).resolve()
        if path.is_file():
            files_to_parse.append(path)
        elif path.is_dir():
            files_to_parse.extend(get_files_recursively(path, args))

    for file in files_to_parse:
        formatted_output = format_file_output(file, args.full_path, args.remove_empty_lines)
        output_lines.append(formatted_output)
        if not args.quiet:
            print(formatted_output)

    with open("files_output", "w", encoding='utf-8') as output_file:
        output_file.writelines(output_lines)


def format_file_output(file: Path, full_path: bool, remove_empty_lines_enabled: bool) -> str:
    """Format the output for each file including its name, path, and content."""
    try:
        content = file.read_text(encoding='utf-8')
        if remove_empty_lines_enabled:
            content = remove_empty_lines(content)
    except UnicodeDecodeError:
        content = "[Binary or Non-UTF-8 encoded file, content not displayed]"

    try:
        path_display = file.relative_to(Path.cwd())
    except ValueError:
        path_display = file.resolve()

    if full_path:
        path_display = file.resolve()

    return f"File Name: {file.name}, Path: {path_display}\nContent:\n```\n{content}\n```\n{'-' * 40}\n"

def remove_empty_lines(content: str) -> str:
    """Remove empty lines from the content while preserving line endings."""
    return '\n'.join(line for line in content.splitlines() if line.strip())

if __name__ == "__main__":
    main()
