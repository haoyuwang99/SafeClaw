#!/usr/bin/env python3
# hash_directory.py - generates SHA256 checksums for all files in a directory

import hashlib
import os
import sys
from pathlib import Path

def hash_file(path):
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def hash_directory(root):
    root = Path(root)
    results = []
    for filepath in sorted(root.rglob('*')):
        if filepath.is_file():
            try:
                digest = hash_file(filepath)
                rel = filepath.relative_to(root)
                results.append((digest, str(rel)))
            except (PermissionError, OSError):
                pass
    return results

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    hashes = hash_directory(target)
    for digest, path in hashes:
        print(f"{digest}  {path}")
    print(f"\n{len(hashes)} files hashed.")
