#!/usr/bin/env python3
"""
Utility script to create __init__.py files for new package structure.

WHY: Efficiently create __init__.py files for all new subdirectories.
"""

from pathlib import Path

# Define all subdirectories that need __init__.py files
SUBDIRS = [
    # Services subdirectories
    "services/llm",
    "services/storage",
    "services/messaging",
    "services/knowledge_graph",
    # Managers subdirectories
    "managers/build",
    "managers/git",
    "managers/bash",
    "managers/kanban",
    # Agents subdirectories
    "agents/supervisor",
    "agents/developer",
    "agents/analysis",
    "agents/specialized",
    # Pipelines subdirectories
    "pipelines/two_pass",
    "pipelines/dynamic",
    "pipelines/thermodynamic",
    "pipelines/strategies",
    # Stages subdirectories
    "stages/requirements",
    "stages/architecture",
    "stages/development",
    "stages/testing",
    "stages/validation",
    "stages/integration",
    "stages/deployment",
    # Validators subdirectories
    "validators/code_standards",
    "validators/signature",
    # Workflows subdirectories
    "workflows/handlers",
    # Utilities subdirectories
    "utilities/helpers",
    # Tests subdirectories
    "tests/unit",
    "tests/integration",
    "tests/advanced",
    "tests/fixtures",
]

def create_init_files():
    """Create __init__.py files for all subdirectories."""
    src_dir = Path(__file__).parent

    for subdir in SUBDIRS:
        init_file = src_dir / subdir / "__init__.py"

        # Skip if already exists
        if init_file.exists():
            print(f"✓ Already exists: {init_file}")
            continue

        # Create __init__.py with appropriate content
        package_name = subdir.split("/")[-1]
        parent_package = "/".join(subdir.split("/")[:-1])

        content = f'''"""
{package_name.capitalize()} subpackage.

Part of: {parent_package}
"""

__all__ = []
'''

        init_file.write_text(content)
        print(f"✓ Created: {init_file}")

if __name__ == "__main__":
    create_init_files()
    print("\n✅ All __init__.py files created successfully!")
