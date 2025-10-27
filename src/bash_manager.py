#!/usr/bin/env python3
"""
Module: Bash Manager

Purpose: Shell script quality management and testing for bash/sh projects
Why: Shell scripts need static analysis, formatting checks, and testing just like
     compiled code, but traditional build systems don't support them. This manager
     provides quality gates for shell script projects.
Patterns: Strategy Pattern (via BuildManagerBase), Decorator Pattern (wrap_exception)
Integration: Registered with BuildManagerFactory as BuildSystem.BASH, allowing Artemis
             to treat shell scripts as first-class projects with CI/CD pipelines.

Key Tools Used:
- shellcheck: Static analysis tool that catches common shell script bugs
  Why: Shell scripts are error-prone; shellcheck finds issues like unquoted variables,
       missing error handling, and portability problems before runtime
- shfmt: Shell script formatter (like prettier for JavaScript)
  Why: Consistent formatting improves readability and prevents formatting-related diffs
- bats: Bash Automated Testing System
  Why: Shell scripts need unit tests too; bats provides test framework for bash
"""

from pathlib import Path
from typing import Dict, List, Optional
from build_manager_base import BuildManagerBase, wrap_exception
from build_system_exceptions import BuildException
from build_manager_factory import register_build_manager, BuildSystem


@register_build_manager(BuildSystem.BASH)
class BashManager(BuildManagerBase):
    """
    Manages bash shell script projects.

    Why it exists: Shell scripts are often neglected in CI/CD pipelines despite being
                   critical for automation, deployment, and system administration.
                   This manager brings shell scripts into modern development workflows
                   with linting, formatting, and testing.

    Design pattern: Template Method (inherits from BuildManagerBase)

    Responsibilities:
    - Detect bash/sh script projects (recursively finds *.sh files)
    - Run shellcheck static analysis on all scripts
    - Verify formatting with shfmt
    - Execute bats test suites if present
    - Provide metadata about script inventory

    Integration: Allows Artemis to manage shell script repos the same as application
                 code, with automated quality checks and testing in CI pipelines.
    """

    @wrap_exception
    def __init__(self, project_dir: Path):
        """
        Initialize Bash manager.

        Why needed: Recursively scans for .sh files to identify shell script projects.
                   Caching file list improves performance for subsequent operations.

        Args:
            project_dir: Root directory containing shell scripts

        Raises:
            BuildException: If initialization fails (wrapped by decorator)
        """
        super().__init__(project_dir)
        # Recursively find all .sh files in project
        # Why recursive: Shell scripts may be organized in subdirectories (bin/, scripts/, etc.)
        # Why cache: Avoids repeated filesystem traversals in detect(), build(), and metadata
        self.shell_scripts = list(self.project_dir.glob("**/*.sh"))

    @property
    def name(self) -> str:
        """
        Get build manager name.

        Why needed: Identifies this manager in logs and error messages.

        Returns:
            str: Always returns "bash"
        """
        return "bash"

    @wrap_exception
    def detect(self) -> bool:
        """
        Detect if this is a bash/shell script project.

        Why needed: Auto-detection allows Artemis to recognize shell script repositories
                   without explicit configuration. Any directory with .sh files is
                   considered a bash project.

        Returns:
            bool: True if any .sh files exist in project tree, False otherwise

        Edge cases:
            - Empty directories return False
            - Directories with only executable scripts (no .sh extension) return False
              (Could be enhanced to detect shebang lines)
            - Projects mixing shell scripts with other code types return True
        """
        return len(self.shell_scripts) > 0

    @wrap_exception
    def install_dependencies(self) -> bool:
        """
        Install dependencies (no-op for bash).

        Why needed: Template Method pattern requires this method, but shell scripts
                   typically don't have dependency management like npm or pip.

        What it does: Immediately returns True (success)

        Why always succeed: Shell scripts may source other scripts, but there's no
                           standard dependency installer. If scripts need dependencies,
                           they're usually documented in README or installed via package
                           manager (apt, brew, yum) outside this tool.

        Returns:
            bool: Always True

        Note: Could be enhanced to:
            - Check for required commands (jq, curl, etc.)
            - Install via package manager if missing
            - Parse and validate sourced scripts
        """
        return True

    @wrap_exception
    def build(self) -> bool:
        """
        Lint and format-check all shell scripts.

        Why needed: Shell scripts have no compilation step, so 'build' means quality
                   checks. This catches bugs and style issues before execution.

        What it does:
            1. Run shellcheck on each script (static analysis)
               Why: Catches common errors like:
                   - Unquoted variables that break on spaces
                   - Missing error handling (set -e)
                   - Portability issues between bash/sh
                   - Security issues like command injection
                   - Logic errors like useless use of cat

            2. Run shfmt on each script (format verification)
               Why: Ensures consistent formatting:
                   - Indentation (tabs vs spaces)
                   - Line continuation style
                   - Case statement formatting
                   - Function definition style

        Returns:
            bool: True if ALL scripts pass both shellcheck and shfmt, False if any fail

        Why fail-fast: Using &= means if any script fails, all_passed becomes False
                       but we continue checking other scripts to show all errors at once.

        Edge cases:
            - If shellcheck/shfmt not installed, command fails (could check first)
            - Some shellcheck warnings may be false positives (can be disabled with directives)
        """
        all_passed = True

        # shellcheck for static analysis
        # Why iterate: shellcheck analyzes one file at a time for detailed feedback
        for script in self.shell_scripts:
            all_passed &= self._run_command(["shellcheck", str(script)])

        # shfmt for formatting check
        # Why -d flag: Shows diff instead of reformatting (read-only check)
        for script in self.shell_scripts:
            all_passed &= self._run_command(["shfmt", "-d", str(script)])

        return all_passed

    @wrap_exception
    def run_tests(self) -> bool:
        """
        Run bats (Bash Automated Testing System) test suite.

        Why needed: Shell scripts need unit tests to verify logic, especially for
                   complex parsing, error handling, and edge cases. Bats provides
                   test framework similar to pytest for Python or jest for JavaScript.

        What it does:
            - Checks if test/ directory exists
            - Runs all .bats test files using bats command
            - If no tests exist, returns True (no tests = passing)

        Why test/ directory: Convention borrowed from other ecosystems (Python's tests/,
                            Go's _test.go). Keeps test files separate from source.

        Why succeed when no tests: Not all script projects have tests (yet), and we
                                  don't want to fail CI for legacy projects. However,
                                  Artemis should warn about missing tests.

        Returns:
            bool: True if tests pass or don't exist, False if tests fail

        Example test file (test/example.bats):
            ```bash
            #!/usr/bin/env bats

            @test "script exits 0 on success" {
              run ./myscript.sh --valid-input
              [ "$status" -eq 0 ]
            }
            ```

        Edge cases:
            - Returns True if test dir exists but is empty
            - Fails if bats not installed (could check first)
        """
        test_dir = self.project_dir / "test"
        return (
            self._run_command(["bats", str(test_dir)])
            if test_dir.exists()
            else True  # No tests = passing (but should warn)
        )

    @wrap_exception
    def clean(self) -> bool:
        """
        Clean build artifacts (no-op for bash).

        Why needed: Template Method pattern requires this method, but shell scripts
                   don't produce build artifacts like compiled binaries or .class files.

        What it does: Immediately returns True (success)

        Why always succeed: There's nothing to clean. Shell scripts run directly
                           without intermediate artifacts.

        Returns:
            bool: Always True

        Note: Could be enhanced to:
            - Remove temporary files created during test runs
            - Clean up log files if tests generate them
            - Remove coverage reports if using kcov for coverage
        """
        return True

    @wrap_exception
    def get_metadata(self) -> Dict:
        """
        Extract bash project metadata.

        Why needed: Provides inventory and structural information about shell script
                   projects. Useful for dashboards, project analysis, and understanding
                   codebase complexity.

        What it returns:
            - manager: Identifies this as bash project
            - shell_scripts: List of all .sh files (relative paths)
              Why relative: Portable across machines, doesn't expose absolute paths
            - has_tests: Boolean indicating if test directory exists
              Why useful: Quick check for test coverage without running tests
            - script_count: Total number of shell scripts
              Why useful: Indicates project size/complexity

        Returns:
            Dict: Project metadata including script inventory and test presence

        Example output:
            {
              "manager": "bash",
              "shell_scripts": ["deploy.sh", "scripts/backup.sh", "bin/setup.sh"],
              "has_tests": true,
              "script_count": 3
            }

        Edge cases:
            - Empty list if no scripts (shouldn't happen if detect() passed)
            - has_tests=false doesn't mean tests don't exist elsewhere (non-standard location)
        """
        return {
            "manager": "bash",
            "shell_scripts": [str(s.relative_to(self.project_dir)) for s in self.shell_scripts],
            "has_tests": (self.project_dir / "test").exists(),
            "script_count": len(self.shell_scripts)
        }


if __name__ == "__main__":
    import sys
    manager = BashManager(Path.cwd())
    sys.exit(0 if manager.detect() else 1)
