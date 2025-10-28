#!/usr/bin/env python3
"""
WHY: Centralize all git_agent data models, enums, and constants
RESPONSIBILITY: Define types, enums, and data structures for git operations
PATTERNS: Enum pattern, dataclass pattern, constants grouping
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional


# ============================================================================
# CONSTANTS
# ============================================================================

GIT_REMOTE_ORIGIN: str = 'origin'
GIT_STATUS_SUCCESS: str = 'success'
GIT_STATUS_FAILED: str = 'failed'
ARTEMIS_FOOTER: str = "\n\n🤖 Generated with Artemis Autonomous Pipeline"


# ============================================================================
# ENUMS
# ============================================================================

class BranchStrategy(Enum):
    """Git branching strategies"""
    GITFLOW = "gitflow"  # main, develop, feature/*, release/*, hotfix/*
    GITHUB_FLOW = "github_flow"  # main, feature/*
    TRUNK_BASED = "trunk_based"  # main only with short-lived branches
    CUSTOM = "custom"


class CommitConvention(Enum):
    """Commit message conventions"""
    CONVENTIONAL = "conventional"  # feat:, fix:, docs:, etc.
    SEMANTIC = "semantic"  # Similar to conventional
    CUSTOM = "custom"


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class GitOperation:
    """
    WHY: Track and audit git operations
    RESPONSIBILITY: Store operation metadata and results
    """
    operation_type: str
    timestamp: str
    status: str
    details: Dict
    error: Optional[str] = None
