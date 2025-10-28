#!/usr/bin/env python3
"""
WHY: Encapsulate repository configuration and validation
RESPONSIBILITY: Manage repository configuration with validation and serialization
PATTERNS: Dataclass pattern, builder pattern concepts
"""

from dataclasses import dataclass, asdict
from typing import Dict, Optional


@dataclass
class RepositoryConfig:
    """
    WHY: Centralize repository configuration parameters
    RESPONSIBILITY: Store and validate repository settings
    PATTERNS: Dataclass for immutability and type safety
    """
    name: str
    local_path: str
    remote_url: Optional[str] = None
    branch_strategy: str = "github_flow"
    default_branch: str = "main"
    commit_convention: str = "conventional"
    auto_push: bool = False
    create_if_missing: bool = True

    def to_dict(self) -> Dict:
        """
        WHY: Enable serialization for logging and storage
        RESPONSIBILITY: Convert config to dictionary
        """
        return asdict(self)

    def validate(self) -> bool:
        """
        WHY: Ensure configuration is valid before use
        RESPONSIBILITY: Check required fields and valid values
        """
        if not self.name:
            return False
        if not self.local_path:
            return False

        valid_strategies = ["gitflow", "github_flow", "trunk_based", "custom"]
        if self.branch_strategy not in valid_strategies:
            return False

        valid_conventions = ["conventional", "semantic", "custom"]
        if self.commit_convention not in valid_conventions:
            return False

        return True
