#!/usr/bin/env python3
"""
WHY: Format and print violation reports
RESPONSIBILITY: Generate human-readable violation reports
PATTERNS: Reporter (presentation logic)

Reporter separates presentation from scanning logic.
"""

from collections import defaultdict


def print_report(scanner):
    """
    Print comprehensive violation report.

    WHY: Separates reporting from scanning logic (SRP).

    Args:
        scanner: CodeStandardsScanner instance with violations
    """
    print("="*70)
    print("CODE STANDARDS VIOLATION REPORT")
    print("="*70)
    print(f"Files scanned: {scanner.files_scanned}")
    print()

    # Summary by type
    total_violations = sum(len(v) for v in scanner.violations_by_type.values())
    print(f"Total violations: {total_violations}")
    print()

    # Guard clause - no violations
    if not total_violations:
        print("✅ No violations found!")
        return

    print("Violations by type:")
    for v_type, violations in sorted(scanner.violations_by_type.items()):
        severity_counts = defaultdict(int)
        for v in violations:
            severity_counts[v.severity] += 1

        severity_str = ", ".join(f"{count} {sev}" for sev, count in severity_counts.items())
        print(f"  {v_type}: {len(violations)} ({severity_str})")
    print()

    # Detailed violations
    print("="*70)
    print("DETAILED VIOLATIONS")
    print("="*70)

    for v_type, violations in sorted(scanner.violations_by_type.items()):
        print(f"\n{v_type.upper().replace('_', ' ')}:")
        print("-"*70)

        # Group by file
        violations_by_file = defaultdict(list)
        for v in violations:
            violations_by_file[v.file_path].append(v)

        for file_path, file_violations in sorted(violations_by_file.items()):
            print(f"\n📄 {file_path}")
            for v in sorted(file_violations, key=lambda x: x.line_number):
                print(f"   Line {v.line_number} [{v.severity.upper()}]: {v.message}")

    print("\n" + "="*70)
