#!/bin/bash
# disk_usage.sh - shows disk usage for home directory subdirectories

echo "Disk usage breakdown for ~/"
du -sh ~/*/  2>/dev/null | sort -rh | head -20
echo ""
echo "Total:"
du -sh ~/ 2>/dev/null
