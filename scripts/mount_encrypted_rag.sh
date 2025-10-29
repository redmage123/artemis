#!/bin/bash
# Mount encrypted RAG database
# Run this before starting Artemis

set -e

ENCRYPTED_FILE="/home/bbrelin/encrypted_rag.img"
MOUNT_POINT="/home/bbrelin/src/repos/artemis/src/db_encrypted"

# Check if already mounted
if mountpoint -q "$MOUNT_POINT"; then
    echo "✅ Encrypted RAG database is already mounted at: $MOUNT_POINT"
    exit 0
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script must be run with sudo"
    echo "Usage: sudo bash mount_encrypted_rag.sh"
    exit 1
fi

echo "🔓 Mounting encrypted RAG database..."
echo ""

# Open LUKS container
cryptsetup luksOpen "$ENCRYPTED_FILE" rag_encrypted

# Mount filesystem
mkdir -p "$MOUNT_POINT"
mount /dev/mapper/rag_encrypted "$MOUNT_POINT"

# Set ownership
ORIGINAL_USER=$(logname)
chown -R $ORIGINAL_USER:$ORIGINAL_USER "$MOUNT_POINT"

echo ""
echo "✅ Encrypted RAG database mounted at: $MOUNT_POINT"
echo "You can now start Artemis."
