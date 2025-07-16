# media-managed

A flexible and scriptable tool for batch renaming and organizing media files.

---

## Features

- **Batch rename** files in a directory (recursively), with options to strip prefixes, postfixes, or any substring.
- **Cleanup** filenames by removing common media tags and replacing underscores, dashes, and dots with spaces.
- **Optionally organize**: After renaming, create a folder for each file (named after the file, minus extension) and move the file into its own folder.
- **Organize by season**: Move files into folders like 'Season 1' if their names contain the S01E01 pattern.
- **Dry run mode**: Preview changes before making them.
- **Advanced cleaning**: 
  - Removes curly braces from filenames.
  - Automatically adds parentheses around years (e.g., 1938 → (1938)).
  - Ensures resolutions (e.g., 720p, 1080p, 2160p) are shown in brackets `[720p]`.
  - Standardizes season/episode formats like `1x02`, `s1e2` to `S01E02`.
  - Removes a wide range of common “junk” media tags and codec/quality indicators.
- **Process directories**: Optionally apply renaming/cleaning rules to directory names as well as files (using `--process-dirs`).

---

## Why use `media-managed`?

Messy filenames and cluttered downloads are a pain - especially for media collectors, archivists, and data wranglers. `media-managed` helps you quickly clean up and organize your files, with a single command, and full control over how things are processed.

---

## Installation

No installation required! Just download `media-managed.py` and run it with Python 3:

```bash
python media-managed.py --help
```
Optional color output with colorama, install with:

```bash
PIP install colorama
```

---

## Usage

```bash
python media-managed.py DIRECTORY [options]
```

**Examples:**

- Strip `DRAFT-` prefix from all files and clean up common tags:
    ```bash
    python media-managed.py ./downloads -refix "DRAFT-" --clean
    ```

- Remove all `_scene` substrings and move each file into its own folder:
    ```bash
    python media-managed.py ./movies --remove "_scene" --mkfolders
    ```

- Organize TV episodes into season folders:
    ```bash
    python media-managed.py ./shows --by-season
    ```

- Preview what would happen (dry run):
    ```bash
    python media-managed.py ./shows --clean --mkfolders --by-season --dry-run
    ```

- Also process directory names:
    ```bash
    python media-managed.py ./media --clean -rocess-dirs
    ```

---

## Options

| Option               | Description                                                                                           |
|----------------------|------------------------------------------------------------------------------------------------------|
| `-p`, `--prefix`     | Prefix to strip from the start of filenames.                                                         |
| `-s`, `--postfix`    | Postfix to strip from the end of filenames (before extension).                                       |
| `-r`, `--remove`     | Substring to remove from anywhere in filenames.                                                      |
| `-c`, `--clean`      | Cleanup: replace `_`, `.`, and `-` with spaces; remove common media tags (e.g. "web-dl", etc).       |
| `-m`, `--mkfolders`  | After renaming/cleaning, move each file into its own folder (named after the file, minus ext).        |
| `-b`, `--by-season`  | Organize files into season folders if filename matches SxxExx pattern.                               |
| `-d`, `--dry-run`    | Show what would happen, but don’t actually rename or move any files.                                 |
| `-P', '--process-dirs`     | Apply renaming/cleaning logic to directory names as well as files.                             |

---

## How does it work?

- **Order of Operations:**
    1. Renames/cleans files (and optionally directories) as specified, recursively.
    2. If `--mkfolders` is set, moves each file into a new folder named after the file (without extension).
    3. If `--by-season` is set, moves files with SxxExx in name into their season folder.

- **Cleaning details (`--clean`):**  
  - Replaces `_`, `.`, and `-` with spaces.
  - Standardizes season/episode notations to `SxxEyy`.
  - Removes common tags: `web-dl`, `blueray`, `webrip`, `hdr`, `hevc`, `av1`, `opus`, `h265`, `x265`, `x264`, `h264`, `yify`, `dvdrip`, `xvid`, `sfm`, `ac1`, `ac2`, `ac3`, `fov`, `vfua`, and more.
  - Removes curly braces.
  - Adds parentheses around year patterns (e.g., 1938 → (1938)), only if not already in parentheses.
  - Formats resolutions as `[720p]`, `[1080p]`, `[2160p]`.
  - Trims and consolidates spaces.

---

## Safety & Best Practices

- **Dry run first!** Always use `--dry-run` to preview what will change.
- The script avoids overwriting files. If a rename/move would overwrite an existing file, it skips that file and prints a warning.
- Works on Linux, MacOS, and Windows (Python 3).

---

## License

MIT License.  
Feel free to improve and share!

---

## Contributing

Pull requests and issues are welcome! Have ideas for more cleaning patterns or features? Open an issue or PR.

---

## Author

github.com/imthalaw
