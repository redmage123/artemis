#!/usr/bin/env python3
"""
File Type Detection Utility

WHY: Validation strategies differ by file type - Python files need syntax checks,
     HTML/CSS/JS need different validators, binaries need none.

RESPONSIBILITY: Detect file/project types and recommend appropriate validation.

PATTERNS: Strategy Pattern for validation recommendations.
"""

from typing import Dict, List, Set, Optional
from pathlib import Path
import os


class ProjectType:
    """Project type constants"""
    PYTHON = "python"
    WEB_FRONTEND = "web_frontend"  # HTML/CSS/JS
    JAVA = "java"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class FileTypeDetector:
    """
    Detect file and project types for adaptive validation.

    WHY: Different file types need different validation strategies.
    RESPONSIBILITY: Analyze files and recommend validation approach.
    """

    # File extension mappings
    PYTHON_EXTENSIONS = {'.py', '.pyw', '.pyx'}
    WEB_EXTENSIONS = {'.html', '.css', '.js', '.jsx', '.vue', '.svelte'}
    JAVA_EXTENSIONS = {'.java', '.class', '.jar'}
    TS_EXTENSIONS = {'.ts', '.tsx'}
    GO_EXTENSIONS = {'.go'}
    RUST_EXTENSIONS = {'.rs'}
    CPP_EXTENSIONS = {'.cpp', '.cc', '.cxx', '.hpp', '.h'}

    # Binary/asset extensions (skip validation)
    BINARY_EXTENSIONS = {
        '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',  # Images
        '.ttf', '.woff', '.woff2', '.eot',  # Fonts
        '.mp3', '.mp4', '.wav', '.avi',  # Media
        '.zip', '.tar', '.gz', '.bz2',  # Archives
        '.exe', '.dll', '.so', '.dylib',  # Binaries
        '.pdf', '.doc', '.docx'  # Documents
    }

    def __init__(self):
        """Initialize file type detector."""
        pass

    def detect_file_type(self, file_path: str) -> str:
        """
        Detect type of a single file.

        Args:
            file_path: Path to file

        Returns:
            File type string (python, web_frontend, binary, etc.)
        """
        ext = Path(file_path).suffix.lower()

        # Strategy pattern: extension set → file type
        extension_mappings = [
            (self.PYTHON_EXTENSIONS, ProjectType.PYTHON),
            (self.WEB_EXTENSIONS, ProjectType.WEB_FRONTEND),
            (self.JAVA_EXTENSIONS, ProjectType.JAVA),
            (self.TS_EXTENSIONS, ProjectType.TYPESCRIPT),
            (self.GO_EXTENSIONS, ProjectType.GO),
            (self.RUST_EXTENSIONS, ProjectType.RUST),
            (self.CPP_EXTENSIONS, ProjectType.CPP),
            (self.BINARY_EXTENSIONS, "binary")
        ]

        for extensions, file_type in extension_mappings:
            if ext in extensions:
                return file_type

        return ProjectType.UNKNOWN

    def detect_project_type(self, directory: str) -> str:
        """
        Detect overall project type from directory contents.

        Args:
            directory: Project directory path

        Returns:
            Project type string
        """
        if not os.path.exists(directory):
            return ProjectType.UNKNOWN

        # Count files by type
        type_counts = {}

        for root, dirs, files in os.walk(directory):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]

            for file in files:
                file_path = os.path.join(root, file)
                file_type = self.detect_file_type(file_path)

                if file_type != "binary" and file_type != ProjectType.UNKNOWN:
                    type_counts[file_type] = type_counts.get(file_type, 0) + 1

        if not type_counts:
            return ProjectType.UNKNOWN

        # Determine primary type
        primary_type = max(type_counts, key=type_counts.get)

        # Check if mixed (multiple significant types)
        significant_types = [t for t, count in type_counts.items() if count >= 3]
        if len(significant_types) > 1:
            return ProjectType.MIXED

        return primary_type

    def should_validate_file(self, file_path: str) -> bool:
        """
        Determine if file should be validated.

        Args:
            file_path: Path to file

        Returns:
            True if file should be validated
        """
        file_type = self.detect_file_type(file_path)

        # Skip binaries and unknowns
        if file_type in {"binary", ProjectType.UNKNOWN}:
            return False

        return True

    def get_validation_strategy(self, file_path: str, validation_level: str = "standard") -> Dict[str, any]:
        """
        Get recommended validation strategy for file.

        Args:
            file_path: Path to file
            validation_level: Validation level (basic, standard, comprehensive)

        Returns:
            Validation strategy dict with validators to use
        """
        file_type = self.detect_file_type(file_path)

        if file_type == "binary" or file_type == ProjectType.UNKNOWN:
            return {
                'validate': False,
                'reason': 'Binary or unknown file type'
            }

        strategy = {'validate': True, 'validators': []}

        # Strategy pattern: (file_type, validation_level) → validators
        validation_strategies = {
            (ProjectType.PYTHON, "basic"): ['syntax_check'],
            (ProjectType.PYTHON, "standard"): ['syntax_check', 'import_check'],
            (ProjectType.PYTHON, "comprehensive"): ['syntax_check', 'import_check', 'lint', 'type_check'],

            (ProjectType.WEB_FRONTEND, "basic"): ['file_readable'],
            (ProjectType.WEB_FRONTEND, "standard"): ['file_readable', 'syntax_check_if_available'],
            (ProjectType.WEB_FRONTEND, "comprehensive"): ['file_readable', 'lint', 'w3c_validation'],
        }

        # Default strategy for other file types
        default_validators = {
            "basic": ['file_readable'],
            "standard": ['file_readable', 'syntax_check_if_available'],
            "comprehensive": ['file_readable', 'syntax_check_if_available']
        }

        strategy['validators'] = validation_strategies.get(
            (file_type, validation_level),
            default_validators.get(validation_level, ['file_readable'])
        )

        return strategy

    def get_files_by_type(self, directory: str) -> Dict[str, List[str]]:
        """
        Group files by type.

        Args:
            directory: Directory to scan

        Returns:
            Dict mapping file types to lists of file paths
        """
        files_by_type = {}

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]

            for file in files:
                file_path = os.path.join(root, file)
                file_type = self.detect_file_type(file_path)

                if file_type not in files_by_type:
                    files_by_type[file_type] = []
                files_by_type[file_type].append(file_path)

        return files_by_type


# Convenience functions
def detect_file_type(file_path: str) -> str:
    """Detect type of a single file."""
    detector = FileTypeDetector()
    return detector.detect_file_type(file_path)


def detect_project_type(directory: str) -> str:
    """Detect overall project type."""
    detector = FileTypeDetector()
    return detector.detect_project_type(directory)


def should_validate_file(file_path: str) -> bool:
    """Check if file should be validated."""
    detector = FileTypeDetector()
    return detector.should_validate_file(file_path)


def get_validation_strategy(file_path: str, validation_level: str = "standard") -> Dict[str, any]:
    """Get validation strategy for file."""
    detector = FileTypeDetector()
    return detector.get_validation_strategy(file_path, validation_level)


if __name__ == '__main__':
    """Test file type detection"""
    detector = FileTypeDetector()

    print("🔍 Testing File Type Detection")
    print("=" * 60)

    test_files = [
        "test.py",
        "index.html",
        "styles.css",
        "script.js",
        "Main.java",
        "main.go",
        "lib.rs",
        "image.png",
        "unknown.xyz"
    ]

    for file in test_files:
        file_type = detector.detect_file_type(file)
        should_validate = detector.should_validate_file(file)
        strategy = detector.get_validation_strategy(file, "standard")

        print(f"\n📄 {file}")
        print(f"   Type: {file_type}")
        print(f"   Validate: {should_validate}")
        if strategy['validate']:
            print(f"   Validators: {', '.join(strategy['validators'])}")

    print("\n" + "=" * 60)
    print("✅ File type detection test complete")
