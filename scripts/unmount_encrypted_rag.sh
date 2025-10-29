#!/bin/bash
# Unmount encrypted RAG database
# Run this after stopping Artemis for maximum security

set -e

MOUNT_POINT="/home/bbrelin/src/repos/artemis/src/db_encrypted"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script must be run with sudo"
    echo "Usage: sudo bash unmount_encrypted_rag.sh"
    exit 1
fi

# Check if mounted
if ! mountpoint -q "$MOUNT_POINT"; then
    echo "✅ Encrypted RAG database is already unmounted"
    exit 0
fi

echo "🔒 Unmounting encrypted RAG database..."

# Unmount filesystem
umount "$MOUNT_POINT"

# Close LUKS container
cryptsetup luksClose rag_encrypted

echo ""
echo "✅ Encrypted RAG database unmounted and secured"
echo "Data is now encrypted at rest."
