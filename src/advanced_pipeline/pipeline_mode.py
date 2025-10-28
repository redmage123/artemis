#!/usr/bin/env python3
"""
Module: pipeline_mode.py

WHY this module exists:
    Defines execution modes for advanced pipeline integration. Different tasks need different
    execution strategies, and modes provide explicit control over feature activation.

RESPONSIBILITY:
    - Define pipeline execution mode enumeration
    - Document mode selection criteria
    - Provide mode descriptions and use cases

PATTERNS:
    - Enum Pattern: Type-safe mode definitions
"""

from enum import Enum


class PipelineMode(Enum):
    """
    Execution modes for advanced pipeline integration.

    WHY modes: Different tasks need different execution strategies. Simple tasks
    waste resources on advanced features. Complex tasks benefit from all features.
    Modes provide explicit control over feature activation.

    Mode selection criteria:
        STANDARD: Tasks with clear requirements, low risk, known solution
        DYNAMIC: Tasks with varying complexity, benefit from adaptive selection
        TWO_PASS: Tasks needing fast feedback, iterative refinement
        ADAPTIVE: Tasks with high uncertainty, benefit from confidence tracking
        FULL: Complex, high-risk tasks requiring all advanced features
    """
    STANDARD = "standard"      # Traditional pipeline (no advanced features)
    DYNAMIC = "dynamic"        # Dynamic stage selection only
    TWO_PASS = "two_pass"      # Two-pass execution only
    ADAPTIVE = "adaptive"      # Thermodynamic uncertainty only
    FULL = "full"              # All features enabled
