#!/usr/bin/env python3
"""Copy file names from a folder to the clipboard."""

from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path


# Edit this default when you want to run the script without command-line args.
DEFAULT_FOLDER_PATH = '/Volumes/ME/MEO/Blogging/miawanders/articles_miawanders/00-top things to do in Gent, Belgium/compress/final/name updated'


def get_names(folder: Path, recursive: bool, include_folders: bool, include_hidden: bool) -> list[str]:
    if recursive:
        items = folder.rglob("*")
    else:
        items = folder.iterdir()

    names: list[str] = []
    for item in items:
        if not include_hidden and any(part.startswith(".") for part in item.relative_to(folder).parts):
            continue
        if item.is_file() or (include_folders and item.is_dir()):
            names.append(str(item.relative_to(folder)) if recursive else item.name)

    return sorted(names, key=str.lower)


def copy_to_clipboard(text: str) -> bool:
    system = platform.system()

    commands: list[list[str]]
    if system == "Darwin":
        commands = [["pbcopy"]]
    elif system == "Windows":
        commands = [["clip"]]
    else:
        commands = [["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]]

    for command in commands:
        try:
            subprocess.run(command, input=text, text=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue

    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy all file names from a folder.")
    parser.add_argument(
        "folder",
        nargs="?",
        default=DEFAULT_FOLDER_PATH,
        help="Folder to read. Defaults to DEFAULT_FOLDER_PATH in this script.",
    )
    parser.add_argument("-r", "--recursive", action="store_true", help="Include files inside subfolders.")
    parser.add_argument("--include-folders", action="store_true", help="Include folder names too.")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files and folders.")
    parser.add_argument("-o", "--output", help="Also save the names to a text file.")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Not a folder: {folder}", file=sys.stderr)
        return 1

    names = get_names(folder, args.recursive, args.include_folders, args.include_hidden)
    text = "\n".join(names)

    if args.output:
        Path(args.output).expanduser().write_text(text + ("\n" if text else ""), encoding="utf-8")

    copied = copy_to_clipboard(text)
    print(text)
    print()
    if copied:
        print(f"Copied {len(names)} name(s) to the clipboard.")
    else:
        print("Could not access a clipboard tool, but the names are printed above.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
