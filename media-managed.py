import os
import re
import sys
import argparse
import shutil

"""
media-managed.py

A flexible tool for batch renaming and organizing media files.

Features:
- Recursively rename files in a directory, with options to strip prefixes, postfixes, or remove substrings.
- Optionally clean up filenames by removing common media tags and replacing underscores, dashes, and dots with spaces.
- Optionally, after renaming, create a folder for each file (named after the file, minus extension) and move the file into its new folder.

Usage Example:
    python media-managed.py /home/awesome/yourtargetfolder --prefix "DRAFT-" --clean --mkfolders
"""

def move_files_to_individual_folders(target_folder, dry_run=False):
    """
    For each file in the target folder (non-recursive), create a folder named after the file (minus extension),
    and move the file into its corresponding folder.
    """
    print(f"Scanning target folder for file-to-folder organization: {target_folder}\n")

    try:
        all_items = os.listdir(target_folder)
    except FileNotFoundError:
        print(f"Error: The folder '{target_folder}' does not exist.")
        return

    for filename in all_items:
        original_file_path = os.path.join(target_folder, filename)

        # Only process files (skip directories)
        if os.path.isfile(original_file_path):
            print(f"Processing file: {filename}")
            folder_name, file_extension = os.path.splitext(filename)
            new_folder_path = os.path.join(target_folder, folder_name)

            if not os.path.exists(new_folder_path):
                if dry_run:
                    print(f"  - [DRY RUN] Would create folder: {new_folder_path}")
                else:
                    try:
                        os.makedirs(new_folder_path)
                        print(f"  -> Created folder: {new_folder_path}")
                    except OSError as e:
                        print(f"  -> Error creating folder {new_folder_path}: {e}")
                        continue
            else:
                print(f"  -> Folder '{folder_name}' already exists.")

            if dry_run:
                print(f"  - [DRY RUN] Would move '{filename}' into '{new_folder_path}'\n")
            else:
                try:
                    shutil.move(original_file_path, new_folder_path)
                    print(f"  -> Moved '{filename}' into '{new_folder_path}'\n")
                except Exception as e:
                    print(f"  -> Error moving file {filename}: {e}\n")
        else:
            print(f"Skipping directory: {filename}\n")
    print("Move-to-folder operation complete!")


def process_filename(filename, prefix=None, postfix=None, remove_str=None, perform_clean=False):
    """
    Modifies a filename by stripping text or cleaning characters.
    Order of operations: 1. Prefix, 2. Postfix, 3. Remove, 4. Clean.

    Args:
        filename (str): The original filename.
        prefix (str, optional): Prefix to remove from the start.
        postfix (str, optional): Postfix to remove from the end.
        remove_str (str, optional): Substring to remove from anywhere.
        perform_clean (bool): Whether to do global cleanup.

    Returns:
        str: The new, processed filename.
    """
    name_part, extension = os.path.splitext(filename)
    new_name_part = name_part

    # 1. Strip the prefix (from the beginning)
    if prefix and new_name_part.startswith(prefix):
        new_name_part = new_name_part[len(prefix):]

    # 2. Strip the postfix (from the end)
    if postfix and new_name_part.endswith(postfix):
        new_name_part = new_name_part[:-len(postfix)]

    # 3. Remove all occurrences of a specific substring
    if remove_str:
        new_name_part = new_name_part.replace(remove_str, "")

    # 4. Perform a general cleanup of common unwanted characters
    if perform_clean:
        # Replace characters like _, ., - with a space
        new_name_part = re.sub(r'[_.\-]+', ' ', new_name_part)

        # Remove common unwanted strings (case-insensitive)
        chars_to_remove = [
            'web-dl', 'blueray', 'dd5.1', 'cmrg',
            '[tgx]', 'hevc', 'webrip', 'hdr', 'av1', 'opus',
            '5.1', 'h265', 'x265', 'x264', 'h264'
        ]
        pattern_to_remove = r'|'.join([re.escape(s) for s in sorted(chars_to_remove, key=len, reverse=True)])
        new_name_part = re.sub(pattern_to_remove, '', new_name_part, flags=re.IGNORECASE)

        # Remove curly braces
        new_name_part = new_name_part.replace('{', '').replace('}', '')

        # Consolidate multiple spaces and trim
        new_name_part = " ".join(new_name_part.split()).strip()

    # Return the new filename only if a change was made
    if new_name_part != name_part:
        return new_name_part.strip() + extension
    else:
        return filename

def rename_files_in_directory(directory, prefix=None, postfix=None, remove_str=None, perform_clean=False, dry_run=False):
    """
    Recursively renames files based on the provided operations.
    """
    if not os.path.isdir(directory):
        print(f"Error: Directory not found at '{os.path.abspath(directory)}'")
        return

    print(f"Starting scan in directory: {os.path.abspath(directory)}")
    if prefix:
        print(f" - Will strip prefix: '{prefix}'")
    if postfix:
        print(f" - Will strip postfix: '{postfix}'")
    if remove_str:
        print(f" - Will remove all instances of: '{remove_str}'")
    if perform_clean:
        print(f" - Will perform general filename cleaning.")
    print("-" * 20)

    renamed_files_count = 0
    for root, dirs, files in os.walk(directory):
        for filename in files:
            new_filename = process_filename(filename, prefix, postfix, remove_str, perform_clean)
            if new_filename != filename:
                old_filepath = os.path.join(root, filename)
                new_filepath = os.path.join(root, new_filename)

                # Prevent overwriting an existing file
                if os.path.exists(new_filepath):
                    print(f"  - Skipped (conflict): Renaming '{filename}' to '{new_filename}' would overwrite an existing file.")
                    continue
                if dry_run:
                    print(f"  - [DRY RUN] Would rename: '{filename}' -> '{new_filename}'")
                else:
                    try:
                        os.rename(old_filepath, new_filepath)
                        print(f"  - Renamed: '{filename}' -> '{new_filename}'")
                        renamed_files_count += 1
                    except OSError as e:
                        print(f"  - Error renaming '{filename}': {e}")

    print("-" * 20)
    print(f"\nScan complete. Renamed {renamed_files_count} file(s).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recursively strip prefixes, postfixes, or any substring from filenames.",
        epilog="Example: python media-managed.py ./my_files --prefix \"DRAFT-\" --clean"
    )

    parser.add_argument("directory", help="The target directory to scan.")
    parser.add_argument("-p", "--prefix", help="The prefix to strip from the start of filenames.")
    parser.add_argument("-s", "--postfix", help="The postfix to strip from the end of filenames (before extension).")
    parser.add_argument("-r", "--remove", dest="remove_str", help="A string to remove from anywhere within filenames.")
    parser.add_argument("-m", "--mkfolders", action="store_true", help="For each file, create a folder (named after the file, minus extension) and move the file into it after renaming/cleaning.")
    parser.add_argument("-c", "--clean", action="store_true", help="Perform a general cleanup (replaces '_', '.', '-' with spaces and removes common unwanted strings).")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Show what would happen, but don't actually rename or move any files.")

    args = parser.parse_args()

    # Make sure at least one action is selected
    if not any([args.prefix, args.postfix, args.remove_str, args.clean, args.mkfolders]):
        print("Error: You must specify at least one operation: --prefix, --postfix, --remove, --clean, or --mkfolders.")
        parser.print_help()
        sys.exit(1)

    # First, rename/clean files as requested
    rename_files_in_directory(
        args.directory,
        args.prefix,
        args.postfix,
        args.remove_str,
        args.clean,
        dry_run=args.dry_run
    )

    # Then, move files into individual folders if requested
    if args.mkfolders:
        move_files_to_individual_folders(args.directory, dry_run=args.dry_run)
