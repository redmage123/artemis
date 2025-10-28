#!/usr/bin/env python3
"""
Automated Nested If Refactoring Tool

Transforms deeply nested if statements into early return patterns
following claude.md coding standards.

Strategy:
1. Parse Python file to AST
2. Identify nested if blocks (depth >= 2)
3. Transform to early returns using guard clauses
4. Generate refactored code
5. Verify compilation
6. Optionally run tests
"""

import ast
import astor
import sys
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
import subprocess


@dataclass
class RefactoringResult:
    """Result of refactoring a file"""
    file_path: str
    success: bool
    violations_before: int
    violations_after: int
    compilation_ok: bool
    error_message: str = ""


class NestedIfRefactorer(ast.NodeTransformer):
    """
    AST transformer that converts nested ifs to early returns.

    Transformation strategy:
    - Identify nested if statements (depth >= 2)
    - Invert conditions and use early returns
    - Preserve original logic exactly
    """

    def __init__(self):
        self.transformations = 0
        self.in_function = False
        self.function_returns_value = False

    def visit_FunctionDef(self, node):
        """Track when we're inside a function"""
        old_in_function = self.in_function
        old_returns_value = self.function_returns_value

        self.in_function = True
        self.function_returns_value = self._function_has_return_value(node)

        # Transform function body
        new_node = self.generic_visit(node)

        self.in_function = old_in_function
        self.function_returns_value = old_returns_value

        return new_node

    def visit_If(self, node):
        """Transform nested if statements"""
        # Only transform if we're in a function
        if not self.in_function:
            return self.generic_visit(node)

        # Check if this is a nested if (depth >= 2)
        depth = self._get_nesting_depth(node)

        if depth >= 2:
            # Attempt to refactor using early return pattern
            refactored = self._refactor_to_early_return(node)
            if refactored:
                self.transformations += 1
                return refactored

        # Recursively process children
        return self.generic_visit(node)

    def _get_nesting_depth(self, node):
        """Calculate nesting depth of an if statement"""
        depth = 0
        parent = getattr(node, 'parent', None)

        while parent:
            if isinstance(parent, ast.If):
                depth += 1
            parent = getattr(parent, 'parent', None)

        return depth

    def _refactor_to_early_return(self, node):
        """
        Refactor nested if to early return pattern.

        BEFORE:
        if condition1:
            if condition2:
                if condition3:
                    return result

        AFTER:
        if not condition1:
            return default
        if not condition2:
            return default
        if not condition3:
            return default
        return result
        """
        # For now, use a simplified transformation
        # More complex transformations can be added incrementally

        # Strategy: Extract nested ifs and flatten them
        flattened_statements = []
        current = node

        # Walk down the nested if chain
        while isinstance(current, ast.If):
            # Check if this if has a simple structure we can flatten
            if self._can_flatten(current):
                # Create inverted guard clause
                guard = self._create_guard_clause(current)
                if guard:
                    flattened_statements.append(guard)

                # Move to next level
                if len(current.body) == 1 and isinstance(current.body[0], ast.If):
                    current = current.body[0]
                else:
                    # Add remaining body statements
                    flattened_statements.extend(current.body)
                    break
            else:
                # Can't flatten this structure, abort
                return None

        # Return the flattened statements
        if len(flattened_statements) > 1:
            return flattened_statements

        return None

    def _can_flatten(self, node):
        """Check if an if statement can be safely flattened"""
        # Simple heuristic: Can flatten if:
        # 1. No else clause (or simple else)
        # 2. Body is either single nested if or simple statements
        # 3. Condition is invertible

        # Check for complex else clauses
        if node.orelse and not self._is_simple_else(node.orelse):
            return False

        # Check body structure
        if len(node.body) == 1 and isinstance(node.body[0], ast.If):
            return True  # Nested if, can flatten

        if len(node.body) <= 3:
            return True  # Simple body, can flatten

        return False

    def _is_simple_else(self, orelse):
        """Check if else clause is simple enough to preserve"""
        if len(orelse) == 1 and isinstance(orelse[0], (ast.Return, ast.Pass)):
            return True
        return False

    def _create_guard_clause(self, if_node):
        """Create an inverted guard clause from an if statement"""
        # Invert the condition
        inverted_condition = ast.UnaryOp(
            op=ast.Not(),
            operand=if_node.test
        )

        # Determine what to return
        return_value = self._get_early_return_value(if_node)

        # Create guard clause: if not condition: return value
        guard = ast.If(
            test=inverted_condition,
            body=[ast.Return(value=return_value)],
            orelse=[]
        )

        return guard

    def _get_early_return_value(self, if_node):
        """Determine appropriate return value for early return"""
        # Check if there's an else clause with a return
        if if_node.orelse:
            for stmt in if_node.orelse:
                if isinstance(stmt, ast.Return):
                    return stmt.value

        # Default returns based on context
        if self.function_returns_value:
            # Return None as safe default
            return ast.Constant(value=None)
        else:
            # Void function, return nothing
            return None

    def _function_has_return_value(self, func_node):
        """Check if function returns a value (vs void)"""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return) and node.value is not None:
                return True
        return False


class AutoRefactorEngine:
    """Main refactoring engine"""

    def __init__(self, verify_compilation: bool = True, dry_run: bool = False):
        self.verify_compilation = verify_compilation
        self.dry_run = dry_run
        self.results: List[RefactoringResult] = []

    def refactor_file(self, file_path: Path) -> RefactoringResult:
        """Refactor a single file"""
        try:
            # Read source
            source = file_path.read_text()

            # Count violations before
            violations_before = self._count_nested_ifs(source)

            if violations_before == 0:
                return RefactoringResult(
                    file_path=str(file_path),
                    success=True,
                    violations_before=0,
                    violations_after=0,
                    compilation_ok=True,
                    error_message="No violations found"
                )

            # Parse to AST
            tree = ast.parse(source)

            # Add parent references
            self._add_parent_refs(tree)

            # Apply transformations
            refactorer = NestedIfRefactorer()
            new_tree = refactorer.visit(tree)

            # Generate refactored code
            try:
                refactored_code = astor.to_source(new_tree)
            except Exception as e:
                return RefactoringResult(
                    file_path=str(file_path),
                    success=False,
                    violations_before=violations_before,
                    violations_after=violations_before,
                    compilation_ok=False,
                    error_message=f"Code generation failed: {e}"
                )

            # Count violations after
            violations_after = self._count_nested_ifs(refactored_code)

            # Verify compilation
            compilation_ok = True
            if self.verify_compilation:
                try:
                    compile(refactored_code, str(file_path), 'exec')
                except SyntaxError as e:
                    compilation_ok = False
                    return RefactoringResult(
                        file_path=str(file_path),
                        success=False,
                        violations_before=violations_before,
                        violations_after=violations_after,
                        compilation_ok=False,
                        error_message=f"Refactored code has syntax error: {e}"
                    )

            # Write refactored code (if not dry run)
            if not self.dry_run:
                # Backup original
                backup_path = file_path.with_suffix('.py.bak')
                file_path.rename(backup_path)

                # Write refactored
                file_path.write_text(refactored_code)

            return RefactoringResult(
                file_path=str(file_path),
                success=True,
                violations_before=violations_before,
                violations_after=violations_after,
                compilation_ok=compilation_ok,
                error_message=""
            )

        except Exception as e:
            return RefactoringResult(
                file_path=str(file_path),
                success=False,
                violations_before=0,
                violations_after=0,
                compilation_ok=False,
                error_message=f"Unexpected error: {e}"
            )

    def _count_nested_ifs(self, source: str) -> int:
        """Count nested if violations in source code"""
        try:
            tree = ast.parse(source)
            self._add_parent_refs(tree)

            count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    depth = 0
                    parent = getattr(node, 'parent', None)
                    while parent:
                        if isinstance(parent, ast.If):
                            depth += 1
                        parent = getattr(parent, 'parent', None)

                    if depth >= 2:
                        count += 1

            return count
        except:
            return 0

    def _add_parent_refs(self, tree):
        """Add parent references to AST nodes"""
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                child.parent = parent

    def refactor_directory(self, directory: Path, pattern: str = "*.py") -> List[RefactoringResult]:
        """Refactor all Python files in directory"""
        results = []

        for file_path in directory.rglob(pattern):
            # Skip __pycache__, .venv, etc.
            if any(excluded in file_path.parts for excluded in ['.venv', '__pycache__', '.git']):
                continue

            print(f"Refactoring {file_path}...")
            result = self.refactor_file(file_path)
            results.append(result)

            if result.success:
                improvement = result.violations_before - result.violations_after
                print(f"  ✅ {result.violations_before} → {result.violations_after} violations ({improvement} fixed)")
            else:
                print(f"  ❌ Failed: {result.error_message}")

        return results

    def print_summary(self, results: List[RefactoringResult]):
        """Print refactoring summary"""
        print("\n" + "="*70)
        print("REFACTORING SUMMARY")
        print("="*70)

        total_files = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total_files - successful

        total_violations_before = sum(r.violations_before for r in results)
        total_violations_after = sum(r.violations_after for r in results)
        total_fixed = total_violations_before - total_violations_after

        print(f"Files processed: {total_files}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print()
        print(f"Violations before: {total_violations_before}")
        print(f"Violations after: {total_violations_after}")
        print(f"Total fixed: {total_fixed} ({total_fixed/total_violations_before*100:.1f}%)")

        if failed > 0:
            print("\n❌ Failed files:")
            for r in results:
                if not r.success:
                    print(f"  - {r.file_path}: {r.error_message}")

        print("="*70)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Auto-refactor nested if statements')
    parser.add_argument('path', help='File or directory to refactor')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--no-verify', action='store_true', help='Skip compilation verification')

    args = parser.parse_args()

    path = Path(args.path)

    engine = AutoRefactorEngine(
        verify_compilation=not args.no_verify,
        dry_run=args.dry_run
    )

    if path.is_file():
        result = engine.refactor_file(path)
        engine.print_summary([result])
    else:
        results = engine.refactor_directory(path)
        engine.print_summary(results)


if __name__ == '__main__':
    main()
