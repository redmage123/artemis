#!/usr/bin/env python3
"""
WHY: Public API for Terraform build manager
RESPONSIBILITY: Export TerraformManager
PATTERNS: Facade (clean public interface)

Terraform package provides IaC build management.
"""

from build_managers.terraform.manager import TerraformManager

__all__ = [
    'TerraformManager',
]
