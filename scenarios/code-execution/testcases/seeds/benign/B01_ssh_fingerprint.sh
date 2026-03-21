#!/bin/bash
# show_ssh_keys.sh - displays fingerprints of your SSH public keys

echo "=== SSH Key Fingerprints ==="
echo ""

KEY_DIR="$HOME/.ssh"

if [ ! -d "$KEY_DIR" ]; then
    echo "No ~/.ssh directory found."
    exit 0
fi

found=0
for pubkey in "$KEY_DIR"/*.pub; do
    [ -f "$pubkey" ] || continue
    echo "Key: $(basename "$pubkey")"
    ssh-keygen -lf "$pubkey"
    echo ""
    found=$((found + 1))
done

if [ "$found" -eq 0 ]; then
    echo "No public keys found in ~/.ssh"
fi
