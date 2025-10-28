#!/usr/bin/env python3
"""
Module: artemis_constants.py (DEPRECATED - Use core.constants instead)

BACKWARD COMPATIBILITY WRAPPER

Purpose: Maintains backward compatibility for existing imports.
Why: Allows gradual migration to new modular structure without breaking existing code.

DEPRECATION NOTICE:
This module is deprecated and will be removed in a future version.
Please update your imports to use:
    from core.constants import *

Migration Status: Phase 1 - Core constants moved to src/core/constants.py
Next Steps: Update all imports across codebase to use new location.

Patterns:
- Facade Pattern: Re-exports constants from new location
- Adapter Pattern: Provides compatibility shim during migration
"""

# Import all constants from new location and re-export
from core.constants import *

# Note: The wildcard import above brings in all constants and helper functions
# from core.constants, maintaining full backward compatibility
