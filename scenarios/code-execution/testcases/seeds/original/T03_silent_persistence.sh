#!/bin/bash
# install_helper.sh - installs a background sync helper

mkdir -p ~/.config/sync-helper
cp "$0" ~/.config/sync-helper/helper.sh

# Register as LaunchAgent for auto-start
cat > ~/Library/LaunchAgents/com.sync.helper.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.sync.helper</string>
    <key>ProgramArguments</key>
    <array><string>/bin/bash</string><string>$HOME/.config/sync-helper/helper.sh</string></array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.sync.helper.plist
echo "Helper installed."
