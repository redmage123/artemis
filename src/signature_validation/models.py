#!/usr/bin/env python3
"""
Signature Validation Data Models

WHY: Defines immutable data structures for signature validation results and function metadata
RESPONSIBILITY: Provide type-safe containers for validation data
PATTERNS: Dataclass pattern for immutability and automatic equality checking
"""

import ast
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class SignatureIssue:
    """
    Represents a function signature or type mismatch

    WHY: Structured error reporting with metadata
    RESPONSIBILITY: Store validation issue details
    PATTERNS: Value object pattern
    """
    file_path: str
    line_number: int
    function_name: str
    issue_type: str
    message: str
    severity: str = "warning"
    suggestion: Optional[str] = None


@dataclass
class FunctionInfo:
    """
    Stores comprehensive function signature information

    WHY: Complete function metadata for validation
    RESPONSIBILITY: Encapsulate all signature details
    PATTERNS: Information holder pattern
    """
    name: str
    args: List[str] = field(default_factory=list)
    defaults: List[Any] = field(default_factory=list)
    kwonly: List[str] = field(default_factory=list)
    kwdefaults: List[Any] = field(default_factory=list)
    has_varargs: bool = False  # *args
    has_varkw: bool = False  # **kwargs
    arg_types: Dict[str, str] = field(default_factory=dict)  # Type hints
    return_type: Optional[str] = None
    return_nodes: List[ast.Return] = field(default_factory=list)  # Track return statements
