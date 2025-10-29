from artemis_logger import get_logger
logger = get_logger('scanner')
'\nWHY: Orchestrate code standards scanning\nRESPONSIBILITY: Coordinate file finding, AST parsing, violation collection\nPATTERNS: Facade (simplified scanning interface), Composition\n\nScanner provides unified interface for code quality checking.\n'
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
from coding_standards.scanner.models import Violation
from coding_standards.scanner.ast_visitor import CodeStandardsVisitor
from coding_standards.scanner.todo_scanner import TodoCommentScanner
from coding_standards.scanner.file_finder import PythonFileFinder

class CodeStandardsScanner:
    """
    Main scanner orchestrator.

    WHY: Centralizes scanning workflow (find, parse, check, report).
    RESPONSIBILITY: Orchestrate file finding, parsing, checking, reporting.
    PATTERNS: Facade, Composition (visitor, scanners, finder).
    """

    def __init__(self, root_path: str, exclude_dirs: Set[str]=None):
        """
        Initialize scanner.

        Args:
            root_path: Root directory to scan
            exclude_dirs: Directories to exclude
        """
        self.root_path = Path(root_path)
        self.exclude_dirs = exclude_dirs or {'.venv', '__pycache__', '.git', 'node_modules'}
        self.violations_by_type: Dict[str, List[Violation]] = defaultdict(list)
        self.files_scanned = 0

    def scan_codebase(self) -> Dict[str, List[Violation]]:
        """
        Scan entire codebase for violations.

        WHY: Single method provides complete scanning workflow.

        Returns:
            Violations grouped by type

        Example:
            >>> scanner = CodeStandardsScanner('src')
            >>> violations = scanner.scan_codebase()
            >>> violations['nested_if']
            [Violation(...), ...]
        """
        
        logger.log(f'🔍 Scanning codebase: {self.root_path}', 'INFO')
        
        logger.log(f"   Excluding: {', '.join(self.exclude_dirs)}", 'INFO')
        
        pass
        finder = PythonFileFinder(self.root_path, self.exclude_dirs)
        for py_file in finder.find_files():
            self._scan_file(py_file)
        return self.violations_by_type

    def get_files_with_critical_violations(self) -> List[str]:
        """
        Get list of files with critical violations.

        WHY: Critical violations require immediate attention.

        Returns:
            Sorted list of file paths
        """
        critical_files = set()
        for violations in self.violations_by_type.values():
            for v in violations:
                if v.severity == 'critical':
                    critical_files.add(v.file_path)
        return sorted(critical_files)

    def _scan_file(self, file_path: Path):
        """
        Scan a single Python file.

        WHY: Isolates per-file scanning logic with error handling.

        Args:
            file_path: Path to Python file
        """
        try:
            source = file_path.read_text()
            source_lines = source.splitlines()
            tree = ast.parse(source, filename=str(file_path))
            self._add_parent_refs(tree)
            visitor = CodeStandardsVisitor(str(file_path), source_lines)
            visitor.visit(tree)
            todo_violations = TodoCommentScanner.scan_file(str(file_path), source_lines)
            all_violations = visitor.violations + todo_violations
            for violation in all_violations:
                self.violations_by_type[violation.violation_type].append(violation)
            self.files_scanned += 1
        except SyntaxError as e:
            
            logger.log(f'⚠️  Syntax error in {file_path}: {e}', 'INFO')
        except Exception as e:
            
            logger.log(f'⚠️  Error scanning {file_path}: {e}', 'INFO')

    def _add_parent_refs(self, tree):
        """
        Add parent references to AST nodes.

        WHY: Enables depth calculation for nested if detection.

        Args:
            tree: AST tree
        """
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                child.parent = parent

def main():
    """
    Main entry point for CLI usage.

    WHY: Provides command-line interface for scanning.
    """
    import argparse
    parser = argparse.ArgumentParser(description='Scan Artemis codebase for coding standards violations')
    parser.add_argument('--root', default='src', help='Root directory to scan (default: src)')
    parser.add_argument('--exclude', nargs='*', help='Additional directories to exclude')
    parser.add_argument('--critical-only', action='store_true', help='Show only critical violations')
    parser.add_argument('--exit-code', action='store_true', help='Exit with code 1 if violations found (default: always enabled)')
    args = parser.parse_args()
    exclude_dirs = {'.venv', '__pycache__', '.git', 'node_modules', '.artemis_data'}
    if args.exclude:
        exclude_dirs.update(args.exclude)
    scanner = CodeStandardsScanner(args.root, exclude_dirs)
    violations = scanner.scan_codebase()
    if args.critical_only:
        violations = {k: [v for v in vals if v.severity == 'critical'] for k, vals in violations.items()}
        scanner.violations_by_type = violations
    from coding_standards.scanner.reporter import print_report
    print_report(scanner)
    critical_files = scanner.get_files_with_critical_violations()
    if critical_files:
        
        logger.log('\n🚨 FILES WITH CRITICAL VIOLATIONS:', 'INFO')
        for file_path in critical_files:
            
            logger.log(f'   - {file_path}', 'INFO')
    total_violations = sum((len(v) for v in violations.values()))
    sys.exit(1 if total_violations > 0 else 0)
if __name__ == '__main__':
    main()