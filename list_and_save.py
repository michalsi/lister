import argparse
from pathlib import Path
from typing import Set, List, Iterator
from enum import Enum

class SkipDirs(Enum):
    PYCACHE = "__pycache__"
    GIT = ".git"
    NODE_MODULES = "node_modules"

SKIP_DIRS_VALUES = frozenset(skip_dir.value for skip_dir in SkipDirs)

def is_skippable_path(path: Path, skip_dirs: Set[str], include_hidden: bool) -> bool:
    """Check if a path should be skipped based on given criteria."""
    return (
            any(part in SKIP_DIRS_VALUES or part in skip_dirs for part in path.parts)
            or (not include_hidden and any(part.startswith('.') and part not in {'.', '..'} for part in path.parts))
    )

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
            if not is_skippable_path(item.parent, skip_dirs, args.include_hidden) and \
                    should_include_file(item, include_extensions, skip_files):
                yield item

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="List and save content of source code files.")
    parser.add_argument("-f", "--files_and_dirs", nargs="+", required=True, help="File/dir or list them to process")
    parser.add_argument("-i", "--include_hidden", action="store_true", help="Include hidden files (default is to exclude)")
    parser.add_argument("-x", "--include_extension", nargs="+", type=str, help="Include only files with these extensions (e.g., '.txt' '.py')")
    parser.add_argument("-d", "--skip_dirs", nargs="+", default=[], help="Additional directories to skip")
    parser.add_argument("-s", "--skip_files", nargs="+", default=[], help="Files or file patterns to skip (e.g., '__init__.py' or '.pyc')")
    return parser.parse_args()

def main() -> None:
    args = parse_arguments()
    files_to_parse: List[Path] = []

    for item in args.files_and_dirs:
        path = Path(item).resolve()
        print(f"Processing item: {path}")  # Debugging line
        if path.is_file():
            files_to_parse.append(path)
        elif path.is_dir():
            files_to_parse.extend(get_files_recursively(path, args))

    print("Files to parse:")
    for file in files_to_parse:
        print(file)

if __name__ == "__main__":
    main()