#!/bin/bash
# check_connectivity.sh - checks internet connectivity and DNS resolution

echo "=== Connectivity Check ==="
echo ""

# Check DNS
echo "DNS resolution:"
for host in google.com github.com apple.com; do
    if nslookup "$host" > /dev/null 2>&1; then
        echo "  ✓ $host"
    else
        echo "  ✗ $host (failed)"
    fi
done

# Check HTTP
echo ""
echo "HTTP reachability:"
for url in https://google.com https://github.com; do
    status=$(curl -o /dev/null -s -w "%{http_code}" --max-time 5 "$url")
    echo "  $url → $status"
done

echo ""
echo "Done."
