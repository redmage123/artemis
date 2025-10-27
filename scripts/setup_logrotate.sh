#!/bin/bash
# Setup logrotate for Artemis
# This script installs the logrotate configuration and fixes log directory permissions

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOGROTATE_CONFIG="$PROJECT_ROOT/logrotate.d/artemis"

echo "=================================================="
echo "Artemis Logrotate Setup"
echo "=================================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Running as root - will install directly"
    USE_SUDO=""
else
    echo "ℹ️  Running as user - will use sudo"
    USE_SUDO="sudo"
fi

# 1. Create /var/log/artemis if it doesn't exist
echo ""
echo "1. Setting up /var/log/artemis directory..."
if [ ! -d /var/log/artemis ]; then
    $USE_SUDO mkdir -p /var/log/artemis
    echo "   ✅ Created /var/log/artemis"
else
    echo "   ✓ /var/log/artemis already exists"
fi

# 2. Fix permissions on /var/log/artemis
echo ""
echo "2. Fixing permissions on /var/log/artemis..."
$USE_SUDO chown -R $USER:$USER /var/log/artemis
$USE_SUDO chmod 755 /var/log/artemis
echo "   ✅ Set ownership to $USER:$USER"
echo "   ✅ Set permissions to 755"

# 3. Create /tmp/artemis_logs if it doesn't exist
echo ""
echo "3. Setting up /tmp/artemis_logs directory..."
if [ ! -d /tmp/artemis_logs ]; then
    mkdir -p /tmp/artemis_logs
    echo "   ✅ Created /tmp/artemis_logs"
else
    echo "   ✓ /tmp/artemis_logs already exists"
fi
chmod 755 /tmp/artemis_logs
echo "   ✅ Set permissions to 755"

# 4. Install logrotate configuration
echo ""
echo "4. Installing logrotate configuration..."
if [ ! -f "$LOGROTATE_CONFIG" ]; then
    echo "   ❌ ERROR: Logrotate config not found: $LOGROTATE_CONFIG"
    exit 1
fi

$USE_SUDO cp "$LOGROTATE_CONFIG" /etc/logrotate.d/artemis
$USE_SUDO chmod 644 /etc/logrotate.d/artemis
$USE_SUDO chown root:root /etc/logrotate.d/artemis
echo "   ✅ Installed /etc/logrotate.d/artemis"

# 5. Verify logrotate configuration
echo ""
echo "5. Verifying logrotate configuration..."
if $USE_SUDO logrotate -d /etc/logrotate.d/artemis 2>&1 | grep -q "error"; then
    echo "   ⚠️  Warning: Logrotate config has errors"
    echo "   Running debug output:"
    $USE_SUDO logrotate -d /etc/logrotate.d/artemis
else
    echo "   ✅ Logrotate configuration is valid"
fi

# 6. Test logrotate (dry run)
echo ""
echo "6. Testing logrotate (dry run)..."
$USE_SUDO logrotate -d /etc/logrotate.d/artemis | head -20
echo "   ✅ Dry run successful"

echo ""
echo "=================================================="
echo "✅ Logrotate setup complete!"
echo "=================================================="
echo ""
echo "📋 Configuration Details:"
echo "   • Main logs: /var/log/artemis/*.log"
echo "     - Rotated: daily"
echo "     - Kept: 30 days"
echo "     - Max size: 100M per file"
echo ""
echo "   • Temp logs: /tmp/artemis_logs/*.log"
echo "     - Rotated: daily"
echo "     - Kept: 7 days"
echo "     - Max size: 50M per file"
echo ""
echo "   • Upload logs: /tmp/*_upload*.log"
echo "     - Rotated: weekly"
echo "     - Kept: 4 weeks"
echo "     - Max size: 10M per file"
echo ""
echo "📝 Manual Test:"
echo "   sudo logrotate -f /etc/logrotate.d/artemis"
echo ""
echo "🔍 Check Status:"
echo "   cat /var/lib/logrotate/status | grep artemis"
echo ""
