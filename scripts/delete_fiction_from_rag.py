#!/usr/bin/env python3
"""
WHY: Remove fiction books from RAG database to keep only technical content
RESPONSIBILITY: Identify and delete fiction entries from ChromaDB
PATTERNS: Direct ChromaDB access, metadata filtering, safe deletion with logging

This script:
1. Connects to ChromaDB directly
2. Searches for fiction books by keywords and metadata
3. Deletes fiction entries
4. Logs all deletions for audit trail
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Set

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import chromadb
from chromadb.config import Settings
from artemis_logger import get_logger

logger = get_logger('fiction_cleanup')

# Fiction detection keywords
FICTION_KEYWORDS = [
    'novel', 'fiction', 'story', 'fantasy', 'sci-fi', 'science fiction',
    'thriller', 'mystery', 'romance', 'horror', 'adventure', 'epic',
    'saga', 'tale', 'legend', 'chronicles', 'realm', 'hero', 'heroes',
    'dragon', 'magic', 'wizard', 'witch', 'vampire', 'werewolf',
    'dystopian', 'apocalypse', 'series book', 'warhammer', 'trilogy'
]

# Known fiction publishers/series
FICTION_PUBLISHERS = [
    'z-library fiction', 'black library', 'tor books', 'penguin random house',
    'harpercollins', 'simon & schuster', 'macmillan', 'hachette'
]

# Known fiction authors (add as we find them)
FICTION_AUTHORS = [
    'david guymer', 'j.k. rowling', 'george r.r. martin', 'stephen king',
    'brandon sanderson', 'patrick rothfuss', 'neil gaiman'
]


def get_chromadb_client(db_path: str) -> chromadb.PersistentClient:
    """Initialize ChromaDB client."""
    path = Path(db_path)
    if not path.is_absolute():
        script_dir = Path(__file__).parent.parent / 'src'
        path = script_dir / path

    logger.log(f"📂 Connecting to ChromaDB at: {path}", "INFO")
    return chromadb.PersistentClient(
        path=str(path),
        settings=Settings(anonymized_telemetry=False)
    )


def is_fiction_by_metadata(metadata: Dict) -> bool:
    """
    Determine if content is fiction based on metadata.

    WHY: Filter out fiction books from technical content
    PATTERNS: Multi-criteria heuristic analysis
    """
    if not metadata:
        return False

    # Check title and author
    title = metadata.get('book_title', '').lower()
    author = metadata.get('author', '').lower()

    # Check for fiction keywords in title
    if any(keyword in title for keyword in FICTION_KEYWORDS):
        return True

    # Check for known fiction authors
    if any(author_name in author for author_name in FICTION_AUTHORS):
        return True

    # Check for fiction-specific patterns in title
    fiction_patterns = [
        r'\b(book|vol|volume)\s+\d+\b',  # "Book 1", "Volume 2"
        r'\b(part|chapter)\s+\d+\b',      # "Part 1", "Chapter 2"
        r':\s*(a|an|the)\s+',             # Subtitle patterns common in fiction
        r'(chronicles|saga|legend|tale)\s+of',
    ]

    if any(re.search(pattern, title) for pattern in fiction_patterns):
        # Double-check it's not a technical book
        technical_keywords = ['programming', 'development', 'guide', 'manual',
                             'tutorial', 'learning', 'practice', 'design pattern',
                             'architecture', 'engineering', 'reference']
        if not any(keyword in title for keyword in technical_keywords):
            return True

    return False


def find_fiction_entries(client: chromadb.PersistentClient) -> Dict[str, List[str]]:
    """
    Find all fiction entries across collections.

    Returns:
        Dict mapping collection names to lists of IDs to delete
    """
    logger.log("\n🔍 Scanning for fiction entries...", "INFO")

    collections = client.list_collections()
    fiction_ids = {}
    total_fiction = 0

    for collection_info in collections:
        collection_name = collection_info.name
        collection = client.get_collection(collection_name)

        logger.log(f"\n   Checking collection: {collection_name}", "INFO")

        # Get all items in collection
        try:
            results = collection.get(include=['metadatas', 'documents'])

            if not results or not results.get('ids'):
                logger.log(f"      Empty collection", "INFO")
                continue

            ids = results['ids']
            metadatas = results.get('metadatas', [])
            documents = results.get('documents', [])

            logger.log(f"      Found {len(ids)} total entries", "INFO")

            # Check each entry
            fiction_in_collection = []
            for i, item_id in enumerate(ids):
                metadata = metadatas[i] if i < len(metadatas) else {}
                document = documents[i] if i < len(documents) else ""

                if is_fiction_by_metadata(metadata):
                    fiction_in_collection.append(item_id)
                    book_title = metadata.get('book_title', 'Unknown')
                    author = metadata.get('author', 'Unknown')
                    logger.log(f"      ❌ Fiction found: {book_title} by {author}", "WARNING")

            if fiction_in_collection:
                fiction_ids[collection_name] = fiction_in_collection
                total_fiction += len(fiction_in_collection)
                logger.log(f"      Found {len(fiction_in_collection)} fiction entries", "WARNING")

        except Exception as e:
            logger.log(f"      Error scanning collection: {e}", "ERROR")
            continue

    logger.log(f"\n📊 Total fiction entries found: {total_fiction}", "INFO" if total_fiction == 0 else "WARNING")
    return fiction_ids


def delete_fiction_entries(client: chromadb.PersistentClient, fiction_ids: Dict[str, List[str]]) -> int:
    """
    Delete fiction entries from ChromaDB.

    Returns:
        Number of entries deleted
    """
    if not fiction_ids:
        logger.log("\n✅ No fiction entries to delete", "SUCCESS")
        return 0

    logger.log("\n🗑️  Deleting fiction entries...", "INFO")

    total_deleted = 0

    for collection_name, ids_to_delete in fiction_ids.items():
        logger.log(f"\n   Collection: {collection_name}", "INFO")
        logger.log(f"   Deleting {len(ids_to_delete)} entries...", "INFO")

        try:
            collection = client.get_collection(collection_name)

            # Delete in batches of 100 to avoid overwhelming ChromaDB
            batch_size = 100
            for i in range(0, len(ids_to_delete), batch_size):
                batch = ids_to_delete[i:i + batch_size]
                collection.delete(ids=batch)
                total_deleted += len(batch)
                logger.log(f"      ✓ Deleted batch {i//batch_size + 1} ({len(batch)} items)", "INFO")

            logger.log(f"   ✅ Deleted {len(ids_to_delete)} entries from {collection_name}", "SUCCESS")

        except Exception as e:
            logger.log(f"   ❌ Error deleting from {collection_name}: {e}", "ERROR")
            continue

    logger.log(f"\n✅ Total deleted: {total_deleted} fiction entries", "SUCCESS")
    return total_deleted


def main():
    """Main execution."""
    logger.log("=" * 70, "INFO")
    logger.log("FICTION CLEANUP - Remove Fiction from RAG Database", "INFO")
    logger.log("=" * 70, "INFO")

    # Connect to ChromaDB
    try:
        client = get_chromadb_client('db')
    except Exception as e:
        logger.log(f"❌ Failed to connect to ChromaDB: {e}", "ERROR")
        logger.log("   Make sure ChromaDB is installed: pip install chromadb", "ERROR")
        return 1

    # Find fiction entries
    fiction_ids = find_fiction_entries(client)

    # Confirm deletion
    if fiction_ids:
        total_to_delete = sum(len(ids) for ids in fiction_ids.values())
        logger.log(f"\n⚠️  About to delete {total_to_delete} fiction entries", "WARNING")
        logger.log("   Fiction books found:", "INFO")

        for collection, ids in fiction_ids.items():
            logger.log(f"      {collection}: {len(ids)} entries", "INFO")

        # Delete
        deleted = delete_fiction_entries(client, fiction_ids)

        logger.log("\n" + "=" * 70, "INFO")
        logger.log(f"CLEANUP COMPLETE - Deleted {deleted} fiction entries", "SUCCESS")
        logger.log("=" * 70, "INFO")
    else:
        logger.log("\n" + "=" * 70, "INFO")
        logger.log("NO FICTION FOUND - RAG database is clean", "SUCCESS")
        logger.log("=" * 70, "INFO")

    return 0


if __name__ == "__main__":
    sys.exit(main())
