#!/usr/bin/env python3
"""
Remove all print() statements from Artemis codebase

WHY: Artemis should never output to stdout/stderr. Output goes to logs or UI only.
WHAT: Replaces all print() statements with proper logging.
HOW: AST-based refactoring with import injection and statement replacement.

Usage:
    python scripts/refactor_remove_prints.py --dry-run    # Preview changes
    python scripts/refactor_remove_prints.py              # Apply changes
"""

import ast
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Set
import re


class PrintRemover(ast.NodeTransformer):
    """
    AST transformer that replaces print() with logger calls.

    Handles:
    - print() → logger.log()
    - print(f"text") → logger.log("text", "INFO")
    - print("error:", x) → logger.log(f"error: {x}", "INFO")
    """

    def __init__(self):
        self.has_prints = False
        self.needs_logger = False
        self.has_logger_import = False

    def visit_Call(self, node: ast.Call) -> ast.AST:
        # Check if this is a print() call
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.has_prints = True
            self.needs_logger = True

            # Build log message from print arguments
            if len(node.args) == 0:
                # print() → skip (empty line)
                return ast.Pass()
            elif len(node.args) == 1:
                # print(x) → logger.log(x, "INFO")
                arg = node.args[0]
                return ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='logger', ctx=ast.Load()),
                            attr='log',
                            ctx=ast.Load()
                        ),
                        args=[arg, ast.Constant(value="INFO")],
                        keywords=[]
                    )
                )
            else:
                # print(a, b, c) → logger.log(f"{a} {b} {c}", "INFO")
                # Join arguments with spaces
                format_parts = []
                for arg in node.args:
                    if isinstance(arg, ast.Constant):
                        format_parts.append(arg.value)
                    else:
                        # Convert to f-string interpolation
                        format_parts.append(f"{{{ast.unparse(arg)}}}")

                message = " ".join(str(p) for p in format_parts)
                return ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='logger', ctx=ast.Load()),
                            attr='log',
                            ctx=ast.Load()
                        ),
                        args=[ast.Constant(value=message), ast.Constant(value="INFO")],
                        keywords=[]
                    )
                )

        return self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> ast.AST:
        # Check for existing logger imports
        for alias in node.names:
            if 'logger' in alias.name.lower() or 'logging' in alias.name.lower():
                self.has_logger_import = True
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        # Check for existing logger imports
        if node.module and ('logger' in node.module.lower() or 'logging' in node.module.lower()):
            self.has_logger_import = True
        for alias in node.names:
            if 'logger' in alias.name.lower():
                self.has_logger_import = True
        return node


def refactor_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Refactor a single file to remove print statements.

    Returns:
        (changed, message) tuple
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Skip test files (they can use print for debugging)
        if 'test_' in file_path.name or file_path.name.startswith('test'):
            return False, "Skipped (test file)"

        # Skip if no print statements
        if 'print(' not in source:
            return False, "No print statements"

        # Parse AST
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return False, "Syntax error (skipped)"

        # Transform
        transformer = PrintRemover()
        new_tree = transformer.visit(tree)

        if not transformer.has_prints:
            return False, "No print statements found"

        # Add logger import if needed and not present
        if transformer.needs_logger and not transformer.has_logger_import:
            # Add import at top
            logger_import = ast.ImportFrom(
                module='artemis_logger',
                names=[ast.alias(name='get_logger', asname=None)],
                level=0
            )
            # Add logger initialization
            logger_init = ast.Assign(
                targets=[ast.Name(id='logger', ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id='get_logger', ctx=ast.Load()),
                    args=[ast.Constant(value=file_path.stem)],
                    keywords=[]
                )
            )
            new_tree.body.insert(0, logger_init)
            new_tree.body.insert(0, logger_import)

        # Fix missing location information for new nodes
        ast.fix_missing_locations(new_tree)

        # Generate new source
        new_source = ast.unparse(new_tree)

        if dry_run:
            return True, f"Would replace {transformer.has_prints} print statements"

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_source)

        return True, f"Replaced {transformer.has_prints} print statements"

    except Exception as e:
        return False, f"Error: {str(e)}"


def find_python_files(src_dir: Path) -> List[Path]:
    """Find all Python files in src directory."""
    return list(src_dir.rglob('*.py'))


def main():
    parser = argparse.ArgumentParser(description='Remove print statements from Artemis')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--src-dir', type=Path, default=Path('src'), help='Source directory')
    args = parser.parse_args()

    src_dir = Path(__file__).parent.parent / args.src_dir
    if not src_dir.exists():
        print(f"Error: {src_dir} does not exist")
        sys.exit(1)

    print(f"{'DRY RUN: ' if args.dry_run else ''}Removing print statements from {src_dir}")
    print("=" * 70)

    files = find_python_files(src_dir)
    print(f"Found {len(files)} Python files")
    print()

    changed_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in sorted(files):
        changed, message = refactor_file(file_path, dry_run=args.dry_run)

        if changed:
            changed_count += 1
            relative_path = file_path.relative_to(src_dir)
            print(f"✅ {relative_path}: {message}")
        elif "Error" in message:
            error_count += 1
            relative_path = file_path.relative_to(src_dir)
            print(f"❌ {relative_path}: {message}")
        else:
            skipped_count += 1

    print()
    print("=" * 70)
    print(f"Summary:")
    print(f"  Changed: {changed_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors: {error_count}")

    if args.dry_run:
        print()
        print("This was a dry run. Use without --dry-run to apply changes.")


if __name__ == '__main__':
    main()
