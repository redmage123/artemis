#!/usr/bin/env python3
"""
WHY: Handle document processing, ID generation, and metadata transformations.
     Ensures consistent artifact identification and ChromaDB compatibility.

RESPONSIBILITY:
- Generate unique artifact identifiers
- Serialize/deserialize metadata for ChromaDB
- Convert complex types to storage-compatible formats

PATTERNS:
- Strategy Pattern: Different serialization strategies for different data types
- Pure Functions: Stateless transformation functions
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional


def generate_artifact_id(artifact_type: str, card_id: str) -> str:
    """
    Generate unique artifact ID.

    Uses timestamp and hash to ensure uniqueness across distributed systems.

    Args:
        artifact_type: Type of artifact
        card_id: Card identifier

    Returns:
        Unique artifact ID in format: {type}-{card_id}-{hash}
    """
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    unique = hashlib.md5(f"{artifact_type}{card_id}{timestamp}".encode()).hexdigest()[:8]
    return f"{artifact_type}-{card_id}-{unique}"


def serialize_metadata_for_chromadb(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert metadata to ChromaDB-compatible format.

    ChromaDB requires metadata values to be strings, numbers, or booleans.
    Lists and dicts are serialized to JSON strings.

    Args:
        metadata: Original metadata dictionary

    Returns:
        ChromaDB-compatible metadata dictionary
    """
    chromadb_metadata = {}

    for key, value in metadata.items():
        # Guard: Skip None values
        if value is None:
            chromadb_metadata[key] = ""
            continue

        # Guard: Serialize complex types
        if isinstance(value, (list, dict)):
            chromadb_metadata[key] = json.dumps(value)
            continue

        # Simple types pass through
        chromadb_metadata[key] = value

    return chromadb_metadata


def deserialize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert JSON strings back to Python objects in metadata.

    Reverses the serialization applied for ChromaDB storage.

    Args:
        metadata: ChromaDB metadata with JSON strings

    Returns:
        Deserialized metadata with Python objects
    """
    deserialized = {}

    for key, value in metadata.items():
        # Guard: Only attempt to parse strings that look like JSON
        if not isinstance(value, str):
            deserialized[key] = value
            continue

        if not value.startswith(('[', '{')):
            deserialized[key] = value
            continue

        # Attempt JSON parsing
        try:
            deserialized[key] = json.loads(value)
        except (json.JSONDecodeError, ValueError):
            deserialized[key] = value

    return deserialized


def prepare_artifact_metadata(
    card_id: str,
    task_title: str,
    timestamp: str,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Prepare complete metadata dictionary for ChromaDB storage.

    Combines standard fields with custom metadata and serializes for storage.

    Args:
        card_id: Card identifier
        task_title: Task title
        timestamp: ISO format timestamp
        additional_metadata: Optional custom metadata

    Returns:
        Complete ChromaDB-compatible metadata
    """
    # Base metadata
    metadata = {
        "card_id": card_id,
        "task_title": task_title,
        "timestamp": timestamp
    }

    # Guard: Add additional metadata if provided
    if not additional_metadata:
        return metadata

    # Merge and serialize
    serialized_additional = serialize_metadata_for_chromadb(additional_metadata)
    metadata.update(serialized_additional)

    return metadata
