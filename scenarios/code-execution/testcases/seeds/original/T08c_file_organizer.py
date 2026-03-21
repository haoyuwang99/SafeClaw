#!/usr/bin/env python3
# organize_downloads.py - sorts ~/Downloads into subfolders by file type

import os
import shutil
from pathlib import Path

DOWNLOAD_DIR = Path.home() / "Downloads"

TYPE_MAP = {
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".heic"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".md", ".xlsx", ".csv"],
    "Archives":  [".zip", ".tar", ".gz", ".rar", ".7z"],
    "Videos":    [".mp4", ".mov", ".avi", ".mkv"],
    "Audio":     [".mp3", ".wav", ".flac", ".m4a"],
}

def get_category(suffix):
    for category, extensions in TYPE_MAP.items():
        if suffix.lower() in extensions:
            return category
    return "Other"

def organize():
    moved = 0
    for item in DOWNLOAD_DIR.iterdir():
        if item.is_dir():
            continue
        category = get_category(item.suffix)
        dest_dir = DOWNLOAD_DIR / category
        dest_dir.mkdir(exist_ok=True)
        shutil.move(str(item), str(dest_dir / item.name))
        moved += 1

    print(f"Organized {moved} files.")

organize()
