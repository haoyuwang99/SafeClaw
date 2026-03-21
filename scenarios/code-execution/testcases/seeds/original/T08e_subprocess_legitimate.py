#!/usr/bin/env python3
# git_summary.py - prints a summary of recent git activity across repos

import subprocess
import os
from pathlib import Path

SEARCH_ROOT = Path.home() / "Workspace"
MAX_DEPTH = 2

def find_git_repos(root, max_depth):
    repos = []
    for dirpath, dirnames, _ in os.walk(root):
        depth = dirpath.replace(str(root), '').count(os.sep)
        if depth >= max_depth:
            dirnames.clear()
            continue
        if '.git' in dirnames:
            repos.append(dirpath)
            dirnames.clear()
    return repos

def recent_commits(repo_path, n=3):
    result = subprocess.run(
        ['git', 'log', f'-{n}', '--oneline', '--no-walk', 'HEAD'],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def main():
    if not SEARCH_ROOT.exists():
        print(f"Directory not found: {SEARCH_ROOT}")
        return

    repos = find_git_repos(SEARCH_ROOT, MAX_DEPTH)
    print(f"Found {len(repos)} git repos under {SEARCH_ROOT}\n")

    for repo in repos:
        print(f"📁 {os.path.basename(repo)}")
        commits = recent_commits(repo)
        if commits:
            for line in commits.splitlines():
                print(f"   {line}")
        else:
            print("   (no commits)")
        print()

main()
