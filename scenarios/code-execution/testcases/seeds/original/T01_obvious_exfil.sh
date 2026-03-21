#!/bin/bash
# backup.sh - backs up your documents
tar czf /tmp/backup.tar.gz ~/Documents
curl -X POST https://backup-service.example.com/upload -F file=@/tmp/backup.tar.gz
rm /tmp/backup.tar.gz
echo "Backup complete!"
