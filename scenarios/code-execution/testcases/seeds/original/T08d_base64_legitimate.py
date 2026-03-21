#!/usr/bin/env python3
# encode_file.py - base64 encodes a file for safe email transport

import base64
import sys
import os

def encode_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    with open(filepath, 'rb') as f:
        data = f.read()

    encoded = base64.b64encode(data).decode('utf-8')

    output_path = filepath + ".b64"
    with open(output_path, 'w') as f:
        f.write(encoded)

    print(f"Encoded: {filepath} → {output_path}")
    print(f"Original size: {len(data)} bytes")
    print(f"Encoded size:  {len(encoded)} bytes")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: encode_file.py <filepath>")
        sys.exit(1)
    encode_file(sys.argv[1])
