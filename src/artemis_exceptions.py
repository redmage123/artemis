#!/usr/bin/env python3
"""
Module: artemis_exceptions.py (DEPRECATED - Use core.exceptions instead)

BACKWARD COMPATIBILITY WRAPPER

Purpose: Maintains backward compatibility for existing imports.
Why: Allows gradual migration to new modular structure without breaking existing code.

DEPRECATION NOTICE:
This module is deprecated and will be removed in a future version.
Please update your imports to use:
    from core.exceptions import *

Migration Status: Phase 1 - Core exceptions moved to src/core/exceptions.py
Next Steps: Update all imports across codebase to use new location.

Patterns:
- Facade Pattern: Re-exports exceptions from new location
- Adapter Pattern: Provides compatibility shim during migration
"""

# Import all exceptions from new location and re-export
from core.exceptions import *

# Note: The wildcard import above brings in all exception classes and utility functions
# from core.exceptions, maintaining full backward compatibility
