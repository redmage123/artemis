#!/bin/bash
#
# Start Artemis Code Examples Downloader
#
# Usage:
#   ./start_code_downloader.sh [OPTIONS]
#
# Options:
#   --foreground    Run in foreground (default: background)
#   --interval N    Update interval in seconds (default: 3600)
#   --max-examples N  Max examples per language (default: 100)
#   --install-service  Install as systemd service
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default options
FOREGROUND=false
INTERVAL=3600
MAX_EXAMPLES=100

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --foreground)
            FOREGROUND=true
            shift
            ;;
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        --max-examples)
            MAX_EXAMPLES="$2"
            shift 2
            ;;
        --install-service)
            echo "📦 Installing systemd service..."
            sudo cp ../artemis-code-downloader.service /etc/systemd/system/
            sudo systemctl daemon-reload
            sudo systemctl enable artemis-code-downloader
            sudo systemctl start artemis-code-downloader
            echo "✅ Service installed and started"
            echo "📝 Check status: sudo systemctl status artemis-code-downloader"
            echo "📄 View logs: sudo journalctl -u artemis-code-downloader -f"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Build command
CMD="python3 code_examples_downloader.py --interval $INTERVAL --max-examples $MAX_EXAMPLES"

if [ "$FOREGROUND" = true ]; then
    CMD="$CMD --foreground"
    echo "🚀 Starting Artemis Code Examples Downloader in foreground..."
    echo "   Interval: ${INTERVAL}s"
    echo "   Max examples: ${MAX_EXAMPLES}"
    echo "   Press Ctrl+C to stop"
    echo ""
    exec $CMD
else
    echo "🚀 Starting Artemis Code Examples Downloader in background..."
    echo "   Interval: ${INTERVAL}s"
    echo "   Max examples: ${MAX_EXAMPLES}"

    # Run in background with nohup
    nohup $CMD > /tmp/artemis_downloader.log 2>&1 &
    PID=$!

    echo "✅ Started with PID: $PID"
    echo "📝 Log file: /tmp/artemis_downloader.log"
    echo "📊 Artemis logs: /tmp/artemis_logs/CodeExamplesDownloader.log"
    echo ""
    echo "To stop: kill $PID"
    echo "To monitor: tail -f /tmp/artemis_downloader.log"
fi
