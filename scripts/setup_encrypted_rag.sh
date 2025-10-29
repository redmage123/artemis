#!/bin/bash
# Setup encrypted RAG database using LUKS
# This provides transparent filesystem-level encryption for ChromaDB

set -e  # Exit on error

# Configuration
ENCRYPTED_FILE="/home/bbrelin/encrypted_rag.img"
MOUNT_POINT="/home/bbrelin/src/repos/artemis/src/db_encrypted"
SIZE_MB=10240  # 10GB - adjust based on your needs

echo "======================================================================="
echo "  RAG Database Encryption Setup (LUKS)"
echo "======================================================================="
echo ""
echo "This script will:"
echo "  1. Create an encrypted container file"
echo "  2. Format it with LUKS encryption"
echo "  3. Mount it to: $MOUNT_POINT"
echo "  4. Copy existing RAG data (if any)"
echo ""
echo "IMPORTANT: You will be prompted to create a passphrase."
echo "           Store this passphrase securely - you'll need it to access your data!"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script must be run with sudo"
    echo "Usage: sudo bash setup_encrypted_rag.sh"
    exit 1
fi

# 1. Create encrypted container file
echo ""
echo "Step 1: Creating ${SIZE_MB}MB encrypted container..."
dd if=/dev/zero of="$ENCRYPTED_FILE" bs=1M count=$SIZE_MB status=progress

# 2. Setup LUKS encryption
echo ""
echo "Step 2: Setting up LUKS encryption..."
echo "You will now be prompted to create a passphrase for your encrypted RAG database."
cryptsetup luksFormat "$ENCRYPTED_FILE"

# 3. Open the encrypted container
echo ""
echo "Step 3: Opening encrypted container..."
echo "Enter the passphrase you just created:"
cryptsetup luksOpen "$ENCRYPTED_FILE" rag_encrypted

# 4. Create filesystem
echo ""
echo "Step 4: Creating ext4 filesystem..."
mkfs.ext4 /dev/mapper/rag_encrypted

# 5. Create mount point
echo ""
echo "Step 5: Creating mount point..."
mkdir -p "$MOUNT_POINT"

# 6. Mount the encrypted filesystem
echo ""
echo "Step 6: Mounting encrypted filesystem..."
mount /dev/mapper/rag_encrypted "$MOUNT_POINT"

# 7. Set ownership
ORIGINAL_USER=$(logname)
chown -R $ORIGINAL_USER:$ORIGINAL_USER "$MOUNT_POINT"

# 8. Copy existing data if present
ORIGINAL_DB="/home/bbrelin/src/repos/artemis/src/db"
if [ -d "$ORIGINAL_DB" ]; then
    echo ""
    echo "Step 7: Copying existing RAG database..."
    cp -r "$ORIGINAL_DB"/* "$MOUNT_POINT/" 2>/dev/null || true
    chown -R $ORIGINAL_USER:$ORIGINAL_USER "$MOUNT_POINT"
    echo "✅ Existing data copied"
fi

echo ""
echo "======================================================================="
echo "  ✅ Encrypted RAG Database Setup Complete!"
echo "======================================================================="
echo ""
echo "📁 Encrypted container: $ENCRYPTED_FILE"
echo "📂 Mount point: $MOUNT_POINT"
echo ""
echo "Next steps:"
echo "  1. Update db_path in your code to: '$MOUNT_POINT'"
echo "  2. Use the mount/unmount scripts below for daily operations"
echo ""
echo "⚠️  SECURITY REMINDERS:"
echo "  - Store your passphrase securely (password manager recommended)"
echo "  - The database is ONLY encrypted when unmounted"
echo "  - When mounted, data is accessible to applications"
echo "  - Unmount when not in use for maximum security"
echo ""
