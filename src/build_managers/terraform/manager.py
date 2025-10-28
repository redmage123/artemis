#!/usr/bin/env python3
"""
WHY: Infrastructure as Code build management for Terraform
RESPONSIBILITY: Manage Terraform validation, formatting, planning
PATTERNS: Template Method (BuildManagerBase), Strategy (IaC operations)

Terraform manager adapts IaC workflow to Artemis build interface.
"""

from pathlib import Path
from typing import Dict, List
from build_manager_base import BuildManagerBase, wrap_exception


class TerraformManager(BuildManagerBase):
    """
    Manages Terraform infrastructure-as-code operations.

    WHY: Terraform uses declarative config (not compilation).
    RESPONSIBILITY: Validate, format, plan infrastructure changes.
    PATTERNS: Template Method, Strategy.
    """

    @wrap_exception
    def __init__(self, project_dir: Path):
        """Initialize Terraform manager with .tf file discovery."""
        super().__init__(project_dir)
        self.terraform_files = list(self.project_dir.glob("*.tf"))

    @property
    def name(self) -> str:
        """Get build manager name."""
        return "terraform"

    @wrap_exception
    def detect(self) -> bool:
        """Detect if this is a Terraform project (.tf files exist)."""
        return len(self.terraform_files) > 0 or (
            self.project_dir / "main.tf"
        ).exists()

    @wrap_exception
    def install_dependencies(self) -> bool:
        """Initialize Terraform backend and download providers."""
        return self._run_command(["terraform", "init"])

    @wrap_exception
    def build(self) -> bool:
        """Validate and format-check Terraform configuration."""
        return (
            self._run_command(["terraform", "fmt", "-check"]) and
            self._run_command(["terraform", "validate"])
        )

    @wrap_exception
    def run_tests(self) -> bool:
        """Generate Terraform execution plan (preview changes)."""
        return self._run_command(["terraform", "plan", "-detailed-exitcode"])

    @wrap_exception
    def clean(self) -> bool:
        """Clean Terraform state cache (.terraform directory)."""
        import shutil
        terraform_dir = self.project_dir / ".terraform"
        # Guard clause - only remove if exists
        if terraform_dir.exists():
            shutil.rmtree(terraform_dir)
        return True

    @wrap_exception
    def get_metadata(self) -> Dict:
        """Extract Terraform project metadata."""
        return {
            "manager": "terraform",
            "terraform_files": [
                str(f.relative_to(self.project_dir))
                for f in self.terraform_files
            ],
            "has_backend": (self.project_dir / "backend.tf").exists(),
            "has_variables": (self.project_dir / "variables.tf").exists()
        }
