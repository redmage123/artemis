#!/usr/bin/env python3
"""
Application-level encryption for RAG database content.

WHY: Provides end-to-end encryption of RAG content before storage.
     Most secure but requires decryption on every query.

RESPONSIBILITY:
- Encrypt content before storing in RAG
- Decrypt content when retrieving from RAG
- Transparent to application code using wrapper

PATTERNS:
- Decorator Pattern: Wraps RAGAgent with encryption/decryption
- Proxy Pattern: Intercepts store/query operations
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
import json
import base64

from artemis_logger import get_logger
logger = get_logger(__name__)


class EncryptedRAGWrapper:
    """
    Wrapper for RAGAgent that encrypts all content before storage.

    Usage:
        # Generate and save key (do this once)
        key = EncryptedRAGWrapper.generate_key()
        EncryptedRAGWrapper.save_key(key, '/secure/path/rag.key')

        # Use encrypted RAG
        from rag_agent import RAGAgent
        rag = RAGAgent(db_path='db')
        encrypted_rag = EncryptedRAGWrapper(rag, key_path='/secure/path/rag.key')

        # Store and query work normally, but content is encrypted
        encrypted_rag.store_artifact('code_example', 'card-123', 'Task', 'sensitive content')
        results = encrypted_rag.query_similar('search query')
    """

    def __init__(self, rag_agent, key_path: str):
        """
        Initialize encrypted RAG wrapper.

        Args:
            rag_agent: RAGAgent instance to wrap
            key_path: Path to encryption key file
        """
        self.rag_agent = rag_agent
        self.key = self._load_key(key_path)
        self.cipher = Fernet(self.key)
        logger.log(f"🔒 Encrypted RAG wrapper initialized with key from: {key_path}", "INFO")

    @staticmethod
    def generate_key() -> bytes:
        """
        Generate new encryption key.

        Returns:
            Encryption key bytes
        """
        return Fernet.generate_key()

    @staticmethod
    def save_key(key: bytes, key_path: str):
        """
        Save encryption key to file.

        Args:
            key: Encryption key to save
            key_path: Path to save key (should be secure location)
        """
        Path(key_path).parent.mkdir(parents=True, exist_ok=True)
        with open(key_path, 'wb') as f:
            f.write(key)
        # Set restrictive permissions (owner read/write only)
        os.chmod(key_path, 0o600)
        logger.log(f"🔑 Encryption key saved to: {key_path}", "INFO")
        logger.log(f"   Permissions set to 600 (owner read/write only)", "INFO")

    def _load_key(self, key_path: str) -> bytes:
        """
        Load encryption key from file.

        Args:
            key_path: Path to key file

        Returns:
            Encryption key bytes
        """
        with open(key_path, 'rb') as f:
            return f.read()

    def _encrypt(self, text: str) -> str:
        """
        Encrypt text content.

        Args:
            text: Plaintext to encrypt

        Returns:
            Encrypted text (base64 encoded)
        """
        encrypted_bytes = self.cipher.encrypt(text.encode('utf-8'))
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    def _decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt encrypted text.

        Args:
            encrypted_text: Encrypted text (base64 encoded)

        Returns:
            Decrypted plaintext
        """
        encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
        decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')

    def store_artifact(
        self,
        artifact_type: str,
        card_id: str,
        task_title: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store artifact with encrypted content.

        Args:
            artifact_type: Type of artifact
            card_id: Card ID
            task_title: Task title (NOT encrypted for searchability)
            content: Content to encrypt and store
            metadata: Additional metadata

        Returns:
            Artifact ID
        """
        # Encrypt the content
        encrypted_content = self._encrypt(content)

        # Add encryption marker to metadata
        if metadata is None:
            metadata = {}
        metadata['encrypted'] = True
        metadata['encryption_version'] = '1.0'

        # Store encrypted content
        artifact_id = self.rag_agent.store_artifact(
            artifact_type=artifact_type,
            card_id=card_id,
            task_title=task_title,
            content=encrypted_content,
            metadata=metadata
        )

        logger.log(f"🔒 Stored encrypted artifact: {artifact_id}", "INFO")
        return artifact_id

    def query_similar(
        self,
        query_text: str,
        artifact_types: Optional[List[str]] = None,
        top_k: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query for similar artifacts and decrypt results.

        NOTE: Semantic search on encrypted content has limitations.
              Consider storing searchable summaries separately.

        Args:
            query_text: Query text
            artifact_types: Types to search
            top_k: Number of results
            filters: Metadata filters

        Returns:
            List of decrypted artifacts
        """
        # Query encrypted content
        results = self.rag_agent.query_similar(
            query_text=query_text,
            artifact_types=artifact_types,
            top_k=top_k,
            filters=filters
        )

        # Decrypt content in results
        decrypted_results = []
        for result in results:
            if result.get('metadata', {}).get('encrypted'):
                try:
                    result['content'] = self._decrypt(result['content'])
                    decrypted_results.append(result)
                except Exception as e:
                    logger.log(f"⚠️  Failed to decrypt artifact: {e}", "WARNING")
            else:
                # Not encrypted, return as-is
                decrypted_results.append(result)

        return decrypted_results

    def get_recommendations(
        self,
        task_description: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Get recommendations with decrypted content.

        Args:
            task_description: Task description
            context: Additional context

        Returns:
            Recommendations with decrypted content
        """
        recommendations = self.rag_agent.get_recommendations(
            task_description=task_description,
            context=context
        )

        # Decrypt any encrypted content in recommendations
        if 'similar_tasks' in recommendations:
            for task in recommendations['similar_tasks']:
                if task.get('metadata', {}).get('encrypted'):
                    try:
                        task['content'] = self._decrypt(task['content'])
                    except Exception as e:
                        logger.log(f"⚠️  Failed to decrypt task content: {e}", "WARNING")

        return recommendations

    def search_code_examples(
        self,
        query: str,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search code examples and decrypt results.

        Args:
            query: Code query
            language: Programming language filter
            framework: Framework filter
            top_k: Number of results

        Returns:
            List of decrypted code examples
        """
        results = self.rag_agent.search_code_examples(
            query=query,
            language=language,
            framework=framework,
            top_k=top_k
        )

        # Decrypt code examples
        decrypted_results = []
        for result in results:
            if result.get('metadata', {}).get('encrypted'):
                try:
                    result['content'] = self._decrypt(result['content'])
                    decrypted_results.append(result)
                except Exception as e:
                    logger.log(f"⚠️  Failed to decrypt code example: {e}", "WARNING")
            else:
                decrypted_results.append(result)

        return decrypted_results


def setup_encrypted_rag():
    """
    Interactive setup for encrypted RAG.

    Usage:
        python encrypted_rag_wrapper.py
    """
    print("=" * 70)
    print("  RAG Database Application-Level Encryption Setup")
    print("=" * 70)
    print()
    print("This will generate an encryption key for your RAG database.")
    print()

    key_path = input("Enter path to save encryption key [~/.artemis/rag.key]: ").strip()
    if not key_path:
        key_path = os.path.expanduser("~/.artemis/rag.key")

    key_path = os.path.expanduser(key_path)

    if os.path.exists(key_path):
        print(f"\n⚠️  Key already exists at: {key_path}")
        response = input("Overwrite? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Aborted.")
            return

    # Generate and save key
    print(f"\n🔑 Generating encryption key...")
    key = EncryptedRAGWrapper.generate_key()
    EncryptedRAGWrapper.save_key(key, key_path)

    print()
    print("=" * 70)
    print("  ✅ Encryption Setup Complete!")
    print("=" * 70)
    print()
    print(f"🔑 Key saved to: {key_path}")
    print()
    print("Usage in your code:")
    print()
    print("    from rag_agent import RAGAgent")
    print("    from encrypted_rag_wrapper import EncryptedRAGWrapper")
    print()
    print("    rag = RAGAgent(db_path='db')")
    print(f"    encrypted_rag = EncryptedRAGWrapper(rag, key_path='{key_path}')")
    print()
    print("    # Use encrypted_rag instead of rag")
    print("    encrypted_rag.store_artifact('code_example', 'card-1', 'Task', 'content')")
    print("    results = encrypted_rag.query_similar('query')")
    print()
    print("⚠️  IMPORTANT:")
    print("   - Keep the encryption key secure!")
    print("   - Back up the key - you cannot decrypt data without it")
    print("   - Do NOT commit the key to version control")
    print()


if __name__ == '__main__':
    setup_encrypted_rag()
