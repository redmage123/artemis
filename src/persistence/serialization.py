#!/usr/bin/env python3
"""
Serialization Utilities

WHY: Provides JSON serialization/deserialization for persistence models.
     Centralizes conversion logic between Python objects and storable formats.

RESPONSIBILITY: Converts between PipelineState/StageCheckpoint objects and JSON.
                Handles type conversion and validation during serialization.

PATTERNS:
- Single Responsibility: Focused solely on serialization concerns
- Guard Clauses: Early returns for validation
- Type Safety: Explicit type hints for all functions
"""

import json
from typing import Dict, Any, List, Optional

from .models import PipelineState, StageCheckpoint


def serialize_pipeline_state(state: PipelineState) -> Dict[str, Any]:
    """
    Serialize pipeline state to dictionary.

    WHY: Converts PipelineState to JSON-serializable format for storage.
    PERFORMANCE: O(n) where n is size of state object.

    Args:
        state: PipelineState instance to serialize

    Returns:
        Dictionary representation suitable for JSON serialization
    """
    return state.to_dict()


def deserialize_pipeline_state(data: Dict[str, Any]) -> PipelineState:
    """
    Deserialize pipeline state from dictionary.

    WHY: Reconstructs PipelineState object from stored data.
    PERFORMANCE: O(n) where n is size of data dictionary.

    Args:
        data: Dictionary containing pipeline state data

    Returns:
        Reconstructed PipelineState instance
    """
    return PipelineState(**data)


def serialize_stage_checkpoint(checkpoint: StageCheckpoint) -> Dict[str, Any]:
    """
    Serialize stage checkpoint to dictionary.

    WHY: Converts StageCheckpoint to JSON-serializable format for storage.
    PERFORMANCE: O(n) where n is size of checkpoint object.

    Args:
        checkpoint: StageCheckpoint instance to serialize

    Returns:
        Dictionary representation suitable for JSON serialization
    """
    return checkpoint.to_dict()


def deserialize_stage_checkpoint(data: Dict[str, Any]) -> StageCheckpoint:
    """
    Deserialize stage checkpoint from dictionary.

    WHY: Reconstructs StageCheckpoint object from stored data.
    PERFORMANCE: O(n) where n is size of data dictionary.

    Args:
        data: Dictionary containing checkpoint data

    Returns:
        Reconstructed StageCheckpoint instance
    """
    return StageCheckpoint(**data)


def serialize_json(obj: Any) -> str:
    """
    Serialize object to JSON string.

    WHY: Provides consistent JSON formatting across persistence layer.
    PERFORMANCE: O(n) where n is size of object.

    Args:
        obj: Python object to serialize (must be JSON-serializable)

    Returns:
        JSON string representation
    """
    return json.dumps(obj)


def deserialize_json(json_str: str) -> Any:
    """
    Deserialize JSON string to Python object.

    WHY: Provides consistent JSON parsing across persistence layer.
    PERFORMANCE: O(n) where n is length of JSON string.

    Args:
        json_str: JSON string to deserialize

    Returns:
        Parsed Python object
    """
    return json.loads(json_str)


def serialize_list(items: List[Any]) -> str:
    """
    Serialize list to JSON string.

    WHY: Converts lists to storable format (e.g., for database TEXT columns).
    PERFORMANCE: O(n) where n is total size of all items.

    Args:
        items: List to serialize

    Returns:
        JSON string representation of list
    """
    return json.dumps(items)


def deserialize_list(json_str: str) -> List[Any]:
    """
    Deserialize JSON string to list.

    WHY: Reconstructs list from stored format.
    PERFORMANCE: O(n) where n is length of JSON string.

    Args:
        json_str: JSON string containing list

    Returns:
        Deserialized list
    """
    return json.loads(json_str)


def serialize_dict(data: Dict[str, Any]) -> str:
    """
    Serialize dictionary to JSON string.

    WHY: Converts dicts to storable format (e.g., for database TEXT columns).
    PERFORMANCE: O(n) where n is total size of all values.

    Args:
        data: Dictionary to serialize

    Returns:
        JSON string representation of dictionary
    """
    return json.dumps(data)


def deserialize_dict(json_str: str) -> Dict[str, Any]:
    """
    Deserialize JSON string to dictionary.

    WHY: Reconstructs dictionary from stored format.
    PERFORMANCE: O(n) where n is length of JSON string.

    Args:
        json_str: JSON string containing dictionary

    Returns:
        Deserialized dictionary
    """
    return json.loads(json_str)
