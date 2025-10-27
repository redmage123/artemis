#!/usr/bin/env python3
"""
Module: Terraform Manager

Purpose: Infrastructure as Code (IaC) build management for Terraform projects
Why: Terraform requires specialized handling because it's not a traditional build system but an
     infrastructure provisioning tool. It needs validation, formatting, and planning steps that
     differ from code compilation and testing workflows.
Patterns: Strategy Pattern (via BuildManagerBase), Decorator Pattern (wrap_exception)
Integration: Registered with BuildManagerFactory as BuildSystem.TERRAFORM, providing unified
             interface for Artemis to manage infrastructure-as-code alongside application code.

Key Differences from Traditional Build Systems:
- No compilation step (validation replaces it)
- 'Build' means validate + format check (not create artifacts)
- 'Test' means generate execution plan (preview changes)
- 'Install' initializes backend and downloads providers
- 'Clean' removes state cache (not build artifacts)
"""

from pathlib import Path
from typing import Dict, List, Optional
from build_manager_base import BuildManagerBase, wrap_exception
from build_system_exceptions import BuildException
from build_manager_factory import register_build_manager, BuildSystem


@register_build_manager(BuildSystem.TERRAFORM)
class TerraformManager(BuildManagerBase):
    """
    Manages Terraform infrastructure-as-code operations.

    Why it exists: Terraform uses declarative configuration files to provision cloud
                   infrastructure. Unlike traditional build systems, it doesn't compile code
                   but validates and applies infrastructure changes. This manager adapts
                   Terraform's workflow to Artemis's unified build interface.

    Design pattern: Template Method (inherits from BuildManagerBase)

    Responsibilities:
    - Detect Terraform projects (*.tf files)
    - Initialize Terraform backend and providers
    - Validate Terraform syntax and configuration
    - Format Terraform code
    - Generate execution plans (terraform plan)
    - Clean Terraform state cache

    Integration: Provides build system abstraction so Artemis can treat infrastructure
                 projects the same as code projects (detect, build, test, clean).
    """

    @wrap_exception
    def __init__(self, project_dir: Path):
        """
        Initialize Terraform manager.

        Why needed: Scans project directory for .tf files to identify Terraform projects.
                   This allows auto-detection without requiring explicit configuration.

        Args:
            project_dir: Root directory containing Terraform configuration files

        Raises:
            BuildException: If initialization fails (wrapped by decorator)
        """
        super().__init__(project_dir)
        # Cache list of .tf files for quick project detection and metadata
        # Why cache: Avoids repeated filesystem scans during detect() and get_metadata()
        self.terraform_files = list(self.project_dir.glob("*.tf"))

    @property
    def name(self) -> str:
        """
        Get build manager name.

        Why needed: Identifies this manager in logs and error messages.

        Returns:
            str: Always returns "terraform"
        """
        return "terraform"

    @wrap_exception
    def detect(self) -> bool:
        """
        Detect if this is a Terraform project.

        Why needed: Auto-detection allows Artemis to automatically identify Terraform
                   projects without manual configuration. Checks for .tf files which are
                   Terraform's configuration format.

        Returns:
            bool: True if any .tf files exist (especially main.tf), False otherwise

        Edge cases:
            - Empty directories return False
            - Projects with only .tfvars files return False (not configuration files)
            - Subdirectories with .tf files are included in self.terraform_files
        """
        return len(self.terraform_files) > 0 or (self.project_dir / "main.tf").exists()

    @wrap_exception
    def install_dependencies(self) -> bool:
        """
        Initialize Terraform backend and download provider plugins.

        Why needed: Terraform requires initialization before any other operations.
                   This downloads provider plugins (AWS, Azure, GCP, etc.), sets up
                   backend for state storage, and validates configuration structure.

        What it does:
            - Downloads and installs provider plugins from Terraform Registry
            - Initializes backend (local, S3, Azure Storage, etc.)
            - Creates .terraform directory with cached providers
            - Validates configuration can be loaded

        Returns:
            bool: True if initialization succeeds, False otherwise

        Raises:
            BuildException: If terraform not found or init fails (wrapped by decorator)
        """
        return self._run_command(["terraform", "init"])

    @wrap_exception
    def build(self) -> bool:
        """
        Validate and format-check Terraform configuration.

        Why needed: Since Terraform doesn't compile, 'build' means validation.
                   This catches syntax errors, invalid resource configurations, and
                   formatting issues before attempting to apply changes.

        What it does:
            1. terraform fmt -check: Verifies code follows canonical formatting
               (Why: Consistent formatting aids code review and prevents formatting conflicts)
            2. terraform validate: Validates configuration syntax and internal consistency
               (Why: Catches errors like missing required arguments, invalid types)

        Returns:
            bool: True if both formatting check and validation pass, False if either fails

        Edge cases:
            - Returns False if code is valid but poorly formatted
            - Validation may pass even if plan will fail (can't check provider API)
        """
        return (
            self._run_command(["terraform", "fmt", "-check"]) and
            self._run_command(["terraform", "validate"])
        )

    @wrap_exception
    def run_tests(self) -> bool:
        """
        Generate Terraform execution plan (preview infrastructure changes).

        Why needed: For IaC, 'testing' means previewing what changes will be made
                   to infrastructure. This is critical because applying changes affects
                   real cloud resources and can cause downtime or data loss.

        What it does:
            - Compares current state with desired configuration
            - Shows what resources will be created, modified, or destroyed
            - Uses -detailed-exitcode flag:
              Exit 0: No changes needed
              Exit 1: Error occurred
              Exit 2: Changes planned (success with diff)

        Why -detailed-exitcode: Allows distinguishing between "no changes" (success)
                                and "changes planned" (also success, but different).

        Returns:
            bool: True if plan succeeds (exit 0 or 2), False if plan fails (exit 1)

        Edge cases:
            - Requires valid cloud credentials (may fail if creds expired)
            - May show changes even if configuration unchanged (provider API updates)
            - Does NOT make any actual infrastructure changes
        """
        return self._run_command(["terraform", "plan", "-detailed-exitcode"])

    @wrap_exception
    def clean(self) -> bool:
        """
        Clean Terraform state cache and downloaded providers.

        Why needed: .terraform directory can become large with cached providers and
                   modules. Cleaning forces re-download on next init, useful for:
                   - Updating to newer provider versions
                   - Fixing corrupted provider cache
                   - Reclaiming disk space

        What it does:
            - Removes .terraform directory (provider cache, modules, plugins)
            - Does NOT remove terraform.tfstate (actual infrastructure state)
               Why: State file tracks real infrastructure; deleting it loses track
                    of managed resources and can cause infrastructure drift

        Returns:
            bool: Always True (cleanup is best-effort)

        Edge cases:
            - If .terraform doesn't exist, silently succeeds
            - Requires re-running terraform init after clean
        """
        import shutil
        terraform_dir = self.project_dir / ".terraform"
        # Short-circuit evaluation: only rmtree if directory exists
        # Why: Avoids FileNotFoundError on already-clean projects
        terraform_dir.exists() and shutil.rmtree(terraform_dir)
        return True

    @wrap_exception
    def get_metadata(self) -> Dict:
        """
        Extract Terraform project metadata.

        Why needed: Provides context about project structure without parsing all .tf files.
                   Useful for Artemis to understand project complexity and configuration.

        What it returns:
            - manager: Identifies this as terraform project
            - terraform_files: List of all .tf configuration files
              Why: Indicates project size and complexity
            - has_backend: Whether backend.tf exists
              Why: Backend config determines where state is stored (critical for teams)
            - has_variables: Whether variables.tf exists
              Why: Variables make configuration reusable across environments

        Returns:
            Dict: Project metadata including file inventory and configuration presence

        Edge cases:
            - Returns empty terraform_files list if no .tf files (shouldn't happen if detect() passed)
            - Missing backend.tf is valid (defaults to local backend)
        """
        return {
            "manager": "terraform",
            "terraform_files": [str(f.relative_to(self.project_dir)) for f in self.terraform_files],
            "has_backend": (self.project_dir / "backend.tf").exists(),
            "has_variables": (self.project_dir / "variables.tf").exists()
        }


if __name__ == "__main__":
    import sys
    manager = TerraformManager(Path.cwd())
    sys.exit(0 if manager.detect() else 1)
