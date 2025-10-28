#!/usr/bin/env python3
"""
Platform Information Models

WHY: Provides data models for platform detection and resource allocation.
RESPONSIBILITY: Define immutable dataclasses for platform information and resource allocation.
PATTERNS: Dataclass pattern for structured data with type safety.

This module contains:
- PlatformInfo: Complete platform hardware and OS information
- ResourceAllocation: Resource allocation recommendations
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class PlatformInfo:
    """
    Complete platform and resource information.

    WHY: Encapsulates all detected platform characteristics in a type-safe structure.
    RESPONSIBILITY: Store platform detection results with validation.
    """

    # Operating System
    os_type: str  # linux, darwin, windows
    os_name: str  # Ubuntu, macOS, Windows 10
    os_version: str  # 22.04, 14.0, 10.0.19045
    os_release: str  # 6.8.0-79-generic

    # Hardware
    cpu_count_physical: int  # Physical cores
    cpu_count_logical: int  # Logical cores (with hyperthreading)
    cpu_frequency_mhz: float  # Current CPU frequency
    cpu_architecture: str  # x86_64, arm64, aarch64

    # Memory
    total_memory_gb: float  # Total RAM
    available_memory_gb: float  # Available RAM

    # Disk
    total_disk_gb: float  # Total disk space
    available_disk_gb: float  # Available disk space
    disk_type: str  # SSD, HDD, Unknown

    # Python Environment
    python_version: str  # 3.11.5
    python_implementation: str  # CPython, PyPy

    # Hostname
    hostname: str

    # Platform hash (for detecting changes)
    platform_hash: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        WHY: Enables serialization for storage and transmission.

        Returns:
            Dictionary representation of platform info
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlatformInfo':
        """
        Create from dictionary.

        WHY: Enables deserialization from stored/transmitted data.

        Args:
            data: Dictionary containing platform info

        Returns:
            PlatformInfo instance
        """
        return cls(**data)


@dataclass
class ResourceAllocation:
    """
    Resource allocation recommendations.

    WHY: Provides calculated resource limits based on detected platform capabilities.
    RESPONSIBILITY: Store resource allocation decisions with reasoning.
    """

    # Parallelization
    max_parallel_developers: int  # Maximum concurrent developer agents
    max_parallel_tests: int  # Maximum concurrent test runners
    max_parallel_stages: int  # Maximum stages to run in parallel

    # Resource limits
    max_memory_per_agent_gb: float  # Memory limit per agent
    recommended_batch_size: int  # For batch processing operations

    # Performance tuning
    use_async_io: bool  # Whether to use async I/O
    enable_caching: bool  # Whether to enable aggressive caching
    thread_pool_size: int  # Size of thread pool for I/O operations

    # Reasoning
    reasoning: str  # Explanation of allocation decisions

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        WHY: Enables serialization for storage and transmission.

        Returns:
            Dictionary representation of resource allocation
        """
        return asdict(self)
