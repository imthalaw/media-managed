import os
import re
import sys
import argparse
import shutil
# --- Optional Colorama Import ---
try:
    # Attempt to import and initialize colorama
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    # If colorma is not installed, create dummy objects
    # so the rest of the script doesn't crash.
    print("Colorama not found. Proceeding without colored output.")
    class DummyColor:
        """A dummy class that returns an empty string for any attribute."""
        def __getattr__(self,name):
            return ""

    # These dummy objects will be used in place of the real ones
    Fore = DummyColor()
    Style = DummyColor()

"""
media-managed.py

A flexible tool for batch renaming and organizing media files.

Features:
- Recursively rename files in a directory, with options to strip prefixes, postfixes, or remove substrings.
- Optionally clean up filenames by removing common media tags and replacing underscores, dashes, and dots with spaces.
- Optionally, after renaming, create a folder for each file (named after the file, minus extension) and move the file into its new folder.
- Optionally, organize TV episodes into season folders based on SxxExx patters

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
        print(f"{Fore.RED}Error: The folder '{target_folder}' does not exist.")
        return

    for filename in all_items:
        original_file_path = os.path.join(target_folder, filename)

        # Only process files (skip directories)
        if os.path.isfile(original_file_path):
            print(f"Processing file: {filename}")
            folder_name, file_extension = os.path.splitext(filename)
            new_folder_path = os.path.join(target_folder, folder_name)
            destination_path = os.path.join(new_folder_path, filename)

            if not os.path.exists(new_folder_path):
                if dry_run:
                    print(f"{Style.DIM}  - [DRY RUN] Would create folder: {new_folder_path}")
                else:
                    try:
                        os.makedirs(new_folder_path)
                        print(f"{Fore.GREEN}  -> Created folder: {new_folder_path}")
                    except OSError as e:
                        print(f"{Fore.RED}  -> Error creating folder {new_folder_path}: {e}")
                        continue
            else:
                print(f"{Fore.YELLOW}  -> Folder '{folder_name}' already exists.")

            if dry_run:
                print(f"{Style.DIM}  - [DRY RUN] Would move '{filename}' into '{new_folder_path}'\n")

            elif os.path.exists(destination_path):
                print(f"{Fore.YELLOW}  -> Skipped (conflict): '{destination_path}' already exists. \n")
            else:
                try:
                    shutil.move(original_file_path, new_folder_path)
                    print(f"  -> Moved '{filename}' into '{new_folder_path}'\n")
                except Exception as e:
                    print(f"{Fore.RED}  -> Error moving file {filename}: {e}\n")
        else:
            print(f"Skipping directory: {filename}\n")
    print(f"{Fore.GREEN}Move-to-folder operation complete!")

def organize_by_season(target_directory, dry_run=False):
    """
    Scan the target directory for files matching the pattern SxxExx (case-insensitive),
    create season folders (e.g., 'Season 1'), and move files into their respective
    season folders based on the number found in the filename.
    """
    print(f"Scanning '{target_directory}' for season/episode patterns...\n")
    pattern = re.compile(r'[Ss](\d{1,2})[Ee](\d{1,2})')
    try:
        all_items = os.listdir(target_directory)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: The folder '{target_directory}' does not exist.")
        return
    moved_count = 0
    for filename in all_items:
        full_path = os.path.join(target_directory, filename)
        if os.path.isfile(full_path):
            match = pattern.search(filename)
            if match:
                season_num = int(match.group(1))
                season_folder = os.path.join(target_directory, f"Season {season_num}")
                dest_path = os.path.join(season_folder, filename)
                if not os.path.exists(season_folder):
                    if dry_run:
                        print(f"{Style.DIM}  - [DRY RUN] Would have created folder: {season_folder}")
                    else:
                        os.makedirs(season_folder)
                        print(f"{Fore.GREEN}  -> Created folder: {season_folder}")

                if os.path.exists(dest_path):
                    print(f"{Fore.YELLOW}  -> Skipped (conflict): Destination '{dest_path}' already exists.")
                    continue
                if dry_run:
                    print(f"{Style.DIM}  - [DRY RUN] Would move '{filename}' to '{season_folder}/'")
                    
                else:
                    shutil.move(full_path, dest_path)
                    print(f"{Fore.GREEN}  -> Moved '{filename}' to '{season_folder}/'")
                moved_count += 1
    print(f"\nSeason organization complete! {moved_count} file(s) processed.")


def process_filename(filename, prefix=None, postfix=None, remove_str=None, perform_clean=False, is_dir=False):
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
    if is_dir:
        name_part = filename
        extension = ""
    else:
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

        # Standardize season/episode format (e.g., 1x02, s1e2 -> S01E02)
        def standardize_episode_format(match):
            # Takes captured season and episode numbers
            season_num =int(match.group(1))
            episode_num = int(match.group(2))
            # Then formats them into the SxxExx standard with leading zeros
            return f"S{season_num:02d}E{episode_num:02d}"

        # This pattern finds formats like 's01e02', 'S1E2', '1x02', or '1x2'
        pattern_to_standardize = r'[Ss]?(\d{1,2})[xXeE](\d{1,2})'
        new_name_part = re.sub(pattern_to_standardize, standardize_episode_format, new_name_part, flags=re.IGNORECASE)

        # Remove common unwanted strings (case-insensitive)
        chars_to_remove = [
            'web', 'webrip', 'web-dl', 'blu', 'ray', 'blueray', 'bluray', 'dd5.1', 'cmrg',
            '[tgx]', 'hevc', 'webrip', 'hdr', 'av1', 'opus', 'amazon', 'amzn'
            '5.1', 'h265', 'x265', 'x264', 'h264', 'yify',
            'dvdrip', 'xvid', 'sfm', 'ac1', 'ac2', 'ac3',
            'fov', 'vfua', 'galaxyrg', 'sucessfulcrab', 
        ]
        pattern_to_remove = r'|'.join([re.escape(s) for s in sorted(chars_to_remove, key=len, reverse=True)])
        new_name_part = re.sub(pattern_to_remove, '', new_name_part, flags=re.IGNORECASE)

        # Remove curly braces
        new_name_part = new_name_part.replace('{', '').replace('}', '')

        # Add parentheses around the year (e.g., 1938 -> (1938)), only if not already in ()
        new_name_part = re.sub(r'(?<!\()\b(18\d{2}|19[0-9]{2}|20[0-9]{2})\b(?!\))', r'(\1)', new_name_part)

        # Ensure resolution is in brackets [720p], [1080p], [2160p] , and [4k]
        def fix_res(match):
            res = match.group(1)
            return f'[{res}]'
        new_name_part = re.sub(r'\[?(720p|1080p|2160p|4k)\]?', fix_res, new_name_part, flags=re.IGNORECASE)
        
        # Consolidate multiple spaces and trim
        new_name_part = " ".join(new_name_part.split()).strip()

        # Remove empty brackets/parentheses left over from tag removal and run final whitespace cleanup
    
        new_name_part = re.sub(r'\s*\[\s*\]\s*', ' ', new_name_part)
        new_name_part = re.sub(r'\s*\(\s*\)\s*', ' ', new_name_part)
        new_name_part = " ".join(new_name_part.split()).strip()

    # Return the new filename only if a change was made
    if new_name_part != name_part:
        return new_name_part.strip() + extension
    else:
        return filename

def rename_files_in_directory(directory, prefix=None, postfix=None, remove_str=None, perform_clean=False, process_dirs=False, dry_run=False):
    """
    Recursively renames files based on the provided operations.
    """
    if not os.path.isdir(directory):
        print(f"{Fore.RED}Error: Directory not found at '{os.path.abspath(directory)}'")
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
    if process_dirs:
        print(f" - Will also apply renaming logic to DIRECTORY names.")
    print("-" * 20)

    renamed_files_count = 0
    renamed_dirs_count = 0

    # Using topdown=False to rename items from the deepest level first.
    # This will prevent errors when renaming a parent directory before its children
    for root, dirs, files in os.walk(directory, topdown=False):
        # 1. Process files in the current directory
        for filename in files:
            new_filename = process_filename(filename, prefix, postfix, remove_str, perform_clean, is_dir=False)
            if new_filename != filename:
                old_filepath = os.path.join(root, filename)
                new_filepath = os.path.join(root, new_filename)

                # Prevent overwriting an existing file
                if os.path.exists(new_filepath):
                    print(f"{Fore.YELLOW}  - Skipped (conflict): Renaming '{filename}' to '{new_filename}' would overwrite an existing file.")
                    continue
                if dry_run:
                    print(f"{Style.DIM}  - [DRY RUN] Would rename: '{filename}' -> '{new_filename}'")
                else:
                    try:
                        os.rename(old_filepath, new_filepath)
                        print(f"{Fore.GREEN}  - Renamed: '{filename}' -> '{new_filename}'")
                        renamed_files_count += 1
                    except OSError as e:
                        print(f"{Fore.RED}  - Error renaming '{filename}': {e}")

        # 2. Process subdirectories in the current directory if flag is set
        if process_dirs:
            for dirname in dirs:
                new_dirname = process_filename(dirname, prefix, postfix, remove_str, perform_clean, is_dir=True)
                
                if new_dirname != dirname:
                    old_dirpath = os.path.join(root, dirname)
                    new_dirpath = os.path.join(root, new_dirname)

                    if os.path.exists(new_dirpath):
                        print(f"{Fore.YELLOW}  - Skipped DIR (conflict): '{dirname}' -> '{new_dirname}' would overwrite.")
                        continue
                    if dry_run:
                        print(f"{Style.DIM} - [DRY RUN] Would rename DIR: '{dirname}' -> '{new_dirname}'")
                    else:
                        try:
                            os.rename(old_dirpath, new_dirpath)
                            print(f"{Fore.GREEN} - Renamed DIR: '{dirname}' -> '{new_dirname}'")
                            renamed_dirs_count += 1
                        except OSError as e:
                            print(f"{Fore.RED}  - Error renaming directory '{dirname}': {e}")
                

    print("-" * 20)
    print(f"{Fore.GREEN}\nScan complete. Renamed {renamed_files_count} file(s) and {renamed_dirs_count} directory/subdirectories.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recursively strip prefixes, postfixes, or any substring from filenames and directories.",
        epilog="Example: python media-managed.py ~/my_files --prefix \"DRAFT-\" --clean --process-dirs"
    )

    parser.add_argument("directory", help="The target directory to scan.")
    parser.add_argument("-p", "--prefix", help="The prefix to strip from the start of filenames.")
    parser.add_argument("-s", "--postfix", help="The postfix to strip from the end of filenames (before extension).")
    parser.add_argument("-r", "--remove", dest="remove_str", help="A string to remove from anywhere within filenames.")
    parser.add_argument("-m", "--mkfolders", action="store_true", help="For each file, create a folder (named after the file, minus extension) and move the file into it after renaming/cleaning.")
    parser.add_argument("-c", "--clean", action="store_true", help="Perform a general cleanup (replaces '_', '.', '-' with spaces and removes common unwanted strings).")
    parser.add_argument("-P", "--process-dirs", action="store_true", help="Also apply renaming logic to directory and subdirectory names.")
    parser.add_argument("-b", "--by-season", action="store_true", help="Organize files into season folders if filename matches SxxExx pattern.")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Show what would happen, but don't actually rename or move any files.")

    
    args = parser.parse_args()

    # Make sure at least one action is selected
    if not any([args.prefix, args.postfix, args.remove_str, args.clean, args.mkfolders, args.by_season, args.process_dirs]):
        print(f"{Fore.RED}Error: You must specify at least one operation: --prefix, --postfix, --remove, --clean, --process_dirs, --mkfolders, or --by-season.")
        parser.print_help()
        sys.exit(1)

    # First, rename/clean files and or directories as requested
    if any([args.prefix, args.postfix, args.remove_str, args.clean, args.process_dirs]):
        rename_files_in_directory(
            args.directory,
            prefix=args.prefix,
            postfix=args.postfix,
            remove_str=args.remove_str,
            perform_clean=args.clean,
            process_dirs=args.process_dirs,
            dry_run=args.dry_run
        )

    # Then, move files into individual folders if requested
    if args.mkfolders:
        move_files_to_individual_folders(args.directory, dry_run=args.dry_run)

    # Organize files into season filers if requested
    if args.by_season:
        organize_by_season(args.directory, dry_run=args.dry_run)
