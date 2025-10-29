# RAG Database Encryption Guide

## Overview

This guide covers three approaches to encrypting your Artemis RAG database:

1. **Filesystem-Level Encryption (LUKS)** - ✅ RECOMMENDED
2. **Application-Level Encryption** - Most secure, but query limitations
3. **SQLite Encryption (SQLCipher)** - Advanced, requires ChromaDB modifications

## Current RAG Setup

Your RAG database uses:
- **Storage**: ChromaDB with PersistentClient
- **Backend**: SQLite database files
- **Location**: `/home/bbrelin/src/repos/artemis/src/db`
- **Collections**: Separate collections per artifact type

## Option 1: Filesystem-Level Encryption (LUKS) ⭐ RECOMMENDED

### Overview
Encrypts the entire database directory using Linux LUKS (Linux Unified Key Setup). Data is encrypted at rest but accessible when mounted.

### Pros
- ✅ Transparent to application - no code changes needed
- ✅ Strong AES-256 encryption
- ✅ Fast performance (hardware-accelerated)
- ✅ Protects against disk theft, unauthorized access
- ✅ Standard Linux encryption, well-tested

### Cons
- ❌ Requires sudo/root access to mount/unmount
- ❌ Data accessible when mounted (not end-to-end)
- ❌ Manual mount required before starting Artemis

### Setup

**Step 1: Run setup script**
```bash
cd /home/bbrelin/src/repos/artemis/scripts
sudo bash setup_encrypted_rag.sh
```

This will:
1. Create a 10GB encrypted container file
2. Prompt you to create a passphrase
3. Mount the encrypted filesystem to `src/db_encrypted`
4. Copy existing RAG data

**Step 2: Update your RAG configuration**

Option A: Environment variable (easiest)
```bash
export ARTEMIS_RAG_DB_PATH="/home/bbrelin/src/repos/artemis/src/db_encrypted"
```

Option B: Update code directly in `src/rag/vector_store.py`:
```python
# Change default db_path
def __init__(self, db_path: Path = None, log_fn: Optional[Callable[[str], None]] = None):
    if db_path is None:
        db_path = Path("/home/bbrelin/src/repos/artemis/src/db_encrypted")
    # ... rest of init
```

**Step 3: Daily operations**

Mount before using Artemis:
```bash
sudo bash /home/bbrelin/src/repos/artemis/scripts/mount_encrypted_rag.sh
```

Unmount when done for maximum security:
```bash
sudo bash /home/bbrelin/src/repos/artemis/scripts/unmount_encrypted_rag.sh
```

### Automatic Mounting (Optional)

Add to systemd for auto-mount on boot:

```bash
# Create systemd mount unit
sudo tee /etc/systemd/system/artemis-rag.mount << 'EOF'
[Unit]
Description=Artemis RAG Encrypted Database
After=local-fs.target

[Mount]
What=/dev/mapper/rag_encrypted
Where=/home/bbrelin/src/repos/artemis/src/db_encrypted
Type=ext4
Options=defaults

[Install]
WantedBy=multi-user.target
EOF

# Enable auto-mount
sudo systemctl enable artemis-rag.mount
sudo systemctl start artemis-rag.mount
```

You'll still need to unlock on boot using a key file or manual passphrase entry.

---

## Option 2: Application-Level Encryption

### Overview
Encrypts content before storing in RAG, decrypts when retrieving. Most secure but has query limitations.

### Pros
- ✅ End-to-end encryption - data never stored unencrypted
- ✅ No special privileges required
- ✅ Fine-grained control over what's encrypted
- ✅ Works with any ChromaDB deployment

### Cons
- ❌ **Semantic search doesn't work on encrypted text** (embeddings are meaningless)
- ❌ Requires code changes throughout application
- ❌ Performance overhead on every query
- ❌ Lose key = lose all data permanently

### Setup

**Step 1: Install cryptography library**
```bash
pip install cryptography
```

**Step 2: Generate encryption key**
```bash
cd /home/bbrelin/src/repos/artemis/scripts
python encrypted_rag_wrapper.py
```

Follow prompts to save key to `~/.artemis/rag.key`

**Step 3: Use encrypted wrapper in your code**

```python
from rag_agent import RAGAgent
from scripts.encrypted_rag_wrapper import EncryptedRAGWrapper

# Create RAG agent
rag = RAGAgent(db_path='db')

# Wrap with encryption
encrypted_rag = EncryptedRAGWrapper(
    rag,
    key_path=os.path.expanduser('~/.artemis/rag.key')
)

# Use encrypted_rag everywhere instead of rag
encrypted_rag.store_artifact(
    artifact_type='code_example',
    card_id='card-123',
    task_title='Example task',
    content='Sensitive content here'
)

# Queries work but semantic search is limited
results = encrypted_rag.query_similar('search term')
```

### Important: Semantic Search Limitation

When content is encrypted, ChromaDB creates embeddings of the encrypted gibberish, NOT the actual content. This means semantic search becomes essentially random.

**Workaround**: Store searchable summaries separately
```python
# Store encrypted full content
encrypted_rag.store_artifact(
    artifact_type='code_example',
    card_id='card-123',
    task_title='OAuth Implementation',  # Not encrypted - used for search
    content=full_sensitive_code,  # Encrypted
    metadata={
        'summary': 'Implements OAuth using authlib',  # Not encrypted - searchable
        'keywords': ['oauth', 'authlib', 'authentication']  # Searchable
    }
)

# Query by metadata instead of content
results = encrypted_rag.query_similar(
    'oauth authentication',
    filters={'keywords': {'$contains': 'oauth'}}
)
```

---

## Option 3: SQLite Encryption (SQLCipher) - Advanced

### Overview
Uses SQLCipher to encrypt the SQLite database files that ChromaDB uses. Requires modifying ChromaDB or using custom SQLite.

### Pros
- ✅ Transparent encryption at database level
- ✅ Semantic search works normally
- ✅ Good performance with hardware acceleration

### Cons
- ❌ Requires compiling ChromaDB with SQLCipher support
- ❌ Complex setup and maintenance
- ❌ May break ChromaDB updates
- ❌ Not officially supported by ChromaDB

### Setup (Advanced Users Only)

**Step 1: Install SQLCipher**
```bash
sudo apt-get install sqlcipher libsqlcipher-dev
```

**Step 2: Compile pysqlcipher3**
```bash
pip install pysqlcipher3
```

**Step 3: Modify ChromaDB to use SQLCipher**

This requires forking ChromaDB and modifying its SQLite connection code. **Not recommended** unless you have specific compliance requirements.

### Alternative: Use ChromaDB Cloud with encryption

ChromaDB Cloud (commercial) offers:
- Encryption at rest
- Encryption in transit
- Managed key rotation
- Compliance certifications

See: https://www.trychroma.com/pricing

---

## Comparison Matrix

| Feature | LUKS (Recommended) | Application-Level | SQLCipher |
|---------|-------------------|-------------------|-----------|
| Ease of Setup | ⭐⭐⭐ Easy | ⭐⭐ Moderate | ⭐ Complex |
| Code Changes | None | Extensive | Moderate |
| Performance | ⭐⭐⭐ Native speed | ⭐⭐ Overhead | ⭐⭐⭐ Native speed |
| Semantic Search | ✅ Works | ❌ Limited | ✅ Works |
| Security Level | 🛡️ Strong | 🛡️🛡️ Strongest | 🛡️ Strong |
| Maintenance | ⭐⭐⭐ Low | ⭐⭐ Moderate | ⭐ High |
| Root Required | Yes (mount) | No | No |

---

## Security Best Practices

Regardless of which encryption method you choose:

1. **Key Management**
   - Store keys in secure location (NOT in repo)
   - Use password managers for passphrases
   - Consider hardware security modules (HSM) for production

2. **Access Control**
   - Restrict file permissions on database directory (700)
   - Limit user access to encryption keys
   - Use separate encryption keys per environment

3. **Backup Strategy**
   - Backup encryption keys separately from data
   - Test restore procedures regularly
   - Document recovery process

4. **Monitoring**
   - Log all database access
   - Monitor for unauthorized mount attempts
   - Alert on encryption key access

5. **Compliance**
   - Ensure encryption meets your compliance requirements (GDPR, HIPAA, etc.)
   - Document encryption implementation
   - Regular security audits

---

## Recommendation

For most users, **LUKS filesystem encryption (Option 1)** is the best choice:

- ✅ Strong AES-256 encryption
- ✅ No application changes needed
- ✅ Standard Linux technology
- ✅ Good performance
- ✅ Easy to implement

If you need end-to-end encryption with zero trust architecture, use **Application-Level Encryption (Option 2)**, but be aware of semantic search limitations.

**SQLCipher (Option 3)** is only recommended if you have specific requirements that necessitate database-level encryption with full semantic search, and you have the expertise to maintain a custom ChromaDB build.

---

## Quick Start: LUKS Encryption

```bash
# 1. Setup encrypted database
cd /home/bbrelin/src/repos/artemis/scripts
sudo bash setup_encrypted_rag.sh

# 2. Mount before using Artemis
sudo bash mount_encrypted_rag.sh

# 3. Update db_path to use encrypted location
export ARTEMIS_RAG_DB_PATH="/home/bbrelin/src/repos/artemis/src/db_encrypted"

# 4. Use Artemis normally
python src/artemis_orchestrator.py --card-id card-123

# 5. Unmount when done
sudo bash unmount_encrypted_rag.sh
```

Done! Your RAG database is now encrypted at rest with military-grade AES-256 encryption.

---

## Troubleshooting

### LUKS won't mount
```bash
# Check if already open
sudo dmsetup ls

# Close and retry
sudo cryptsetup luksClose rag_encrypted
sudo bash mount_encrypted_rag.sh
```

### Forgot passphrase
Unfortunately, LUKS encryption is designed to be unbreakable. If you forget your passphrase, the data is unrecoverable. This is why backup strategies are critical.

### Performance issues
```bash
# Check if encryption is using hardware acceleration
sudo cryptsetup luksDump /home/bbrelin/encrypted_rag.img | grep cipher

# Should show: aes-xts-plain64 (hardware accelerated)
```

### Application-level encryption search not working
This is expected - encrypted content cannot be semantically searched. Use metadata and summaries for search, full content for display.

---

## Additional Resources

- LUKS Documentation: https://gitlab.com/cryptsetup/cryptsetup
- Fernet Encryption (Python): https://cryptography.io/en/latest/fernet/
- SQLCipher: https://www.zetetic.net/sqlcipher/
- ChromaDB Security: https://docs.trychroma.com/deployment
