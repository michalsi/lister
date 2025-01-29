import argparse
import os

DIRS_TO_SKIP = {
    "__pycache__",
    ".git",
    "node_modules",
}

def is_skippable_dir(path):
    path_parts = os.path.normpath(path).split(os.sep)
    return any(part in DIRS_TO_SKIP for part in path_parts)

def is_hidden_path(path):
    parts = os.path.normpath(path).split(os.sep)
    return any(part.startswith('.') and part not in ['.', '..'] for part in parts)

def should_include_file(file_path, include_extension):
    if not include_extension:
        return True
    return file_path.endswith(include_extension)

def should_skip_file(file_name, skip_patterns):
    return any(pattern in file_name for pattern in skip_patterns)

def should_skip_element(item, args):
    if os.path.isdir(item):
        return (not args.include_hidden and is_hidden_path(item)) or \
            is_skippable_dir(item) or \
            any(skip_dir in item.split(os.sep) for skip_dir in args.skip_dirs)
    elif os.path.isfile(item):
        return (not args.include_hidden and is_hidden_path(item)) or \
            should_skip_file(os.path.basename(item), args.skip_files) or \
            any(skip_dir in os.path.dirname(item).split(os.sep) for skip_dir in args.skip_dirs) or \
            (args.include_extension is not None and not item.endswith(args.include_extension))
    return False

def get_files_recursively(path, args):
    files = []
    for root, dirs, filenames in os.walk(path):
        dirs[:] = [d for d in dirs if not should_skip_element(os.path.join(root, d), args)]
        for filename in filenames:
            full_path = os.path.join(root, filename)
            if not should_skip_element(full_path, args) and should_include_file(full_path, args.include_extension):
                files.append(full_path)
    return files

def parse_arguments():
    parser = argparse.ArgumentParser(description="List and save content of source code files.")
    parser.add_argument("-f", "--files_and_dirs", nargs="+", required=True, help="File/dir or list them to process")
    parser.add_argument("-i", "--include_hidden", action="store_true", help="Include hidden files (default is to exclude)")
    parser.add_argument("-x", "--include_extension", type=str, help="Include only files with this extension (e.g., '.txt')")
    parser.add_argument("--skip_dirs", nargs="+", default=[], help="Additional directories to skip")
    parser.add_argument("--skip_files", nargs="+", default=[], help="Files or file patterns to skip (e.g., '__init__.py' or '.pyc')")
    return parser.parse_args()

def main():
    args = parse_arguments()
    files_to_parse = []
    for item in args.files_and_dirs:
        abs_item = os.path.abspath(item)
        print(f"Processing item: {abs_item}")  # Debugging line
        if not should_skip_element(abs_item, args):
            retrieved_files = get_files_recursively(abs_item, args)
            print(f"Retrieved files: {retrieved_files}")  # Debugging line
            files_to_parse.extend(retrieved_files)
    print(files_to_parse)  # Final output

if __name__ == "__main__":
    main()