"""
Go Modules Build Manager - Modularized Components

WHY: Backward compatibility wrapper for refactored Go modules manager
RESPONSIBILITY: Re-export all components for seamless migration
PATTERNS: Facade pattern - single import point for all functionality
"""

from .models import BuildMode, GoArch, GoOS, GoModuleInfo
from .parser import GoModParser
from .dependency_manager import GoDependencyManager
from .build_operations import GoBuildOperations
from .version_detector import GoVersionDetector
from .manager import GoModManager

__all__ = [
    'BuildMode',
    'GoArch',
    'GoOS',
    'GoModuleInfo',
    'GoModParser',
    'GoDependencyManager',
    'GoBuildOperations',
    'GoVersionDetector',
    'GoModManager'
]
