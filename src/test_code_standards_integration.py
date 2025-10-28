#!/usr/bin/env python3
"""
Test Code Standards Integration

WHY: Verify code standards validator integrates correctly with code review stage
RESPONSIBILITY: Test code standards reviewer component
PATTERNS: Unit testing, Test fixtures
"""

import tempfile
import os
from pathlib import Path

# Test imports
from artemis_logger import get_logger
from stages.code_review_stage.code_standards_reviewer import CodeStandardsReviewer


def test_code_standards_reviewer_clean_code():
    """Test code standards reviewer with clean code"""
    print("\n=== Test 1: Clean Code (No Violations) ===")

    # Create temp directory with clean code
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write clean Python file
        test_file = Path(temp_dir) / "clean_code.py"
        test_file.write_text("""
def calculate_sum(numbers):
    '''Calculate sum of numbers'''
    total = 0
    for num in numbers:
        total += num
    return total

def process_data(data):
    '''Process data using dispatch table'''
    # Guard: No data
    if not data:
        return None

    # Dispatch table instead of if/elif chain
    handlers = {
        'type_a': handle_type_a,
        'type_b': handle_type_b,
    }

    handler = handlers.get(data['type'])
    if not handler:
        return None

    return handler(data)

def handle_type_a(data):
    return f"Type A: {data}"

def handle_type_b(data):
    return f"Type B: {data}"
""")

        # Create reviewer
        logger = get_logger("test")
        reviewer = CodeStandardsReviewer(
            logger=logger,
            severity_threshold="warning",
            enabled=True
        )

        # Run review
        result = reviewer.review_developer_code(
            developer_name="test-dev",
            code_directory=temp_dir
        )

        # Verify results
        print(f"✓ Enabled: {result['enabled']}")
        print(f"✓ Passed: {result['passed']}")
        print(f"✓ Violation count: {result['violation_count']}")
        print(f"✓ Files scanned: {result['files_scanned']}")

        assert result['enabled'] is True
        assert result['passed'] is True
        assert result['violation_count'] == 0

        print("✅ Test 1 PASSED: Clean code correctly identified")


def test_code_standards_reviewer_with_violations():
    """Test code standards reviewer with code violations"""
    print("\n=== Test 2: Code with Violations ===")

    # Create temp directory with problematic code
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write code with nested ifs
        test_file = Path(temp_dir) / "bad_code.py"
        test_file.write_text("""
def process_request(request):
    '''Process request with nested ifs'''
    if request is not None:
        if request.valid:
            if request.user:
                return "processed"
    return "failed"

def handle_status(status):
    '''Handle status with elif chain'''
    if status == "pending":
        return "wait"
    elif status == "approved":
        return "proceed"
    elif status == "rejected":
        return "stop"
    elif status == "canceled":
        return "abort"
    else:
        return "unknown"
""")

        # Create reviewer
        logger = get_logger("test")
        reviewer = CodeStandardsReviewer(
            logger=logger,
            severity_threshold="warning",
            enabled=True
        )

        # Run review
        result = reviewer.review_developer_code(
            developer_name="test-dev",
            code_directory=temp_dir
        )

        # Verify results
        print(f"✓ Enabled: {result['enabled']}")
        print(f"✓ Passed: {result['passed']}")
        print(f"✓ Violation count: {result['violation_count']}")
        print(f"✓ Files scanned: {result['files_scanned']}")

        assert result['enabled'] is True
        assert result['passed'] is False  # Should fail due to violations
        assert result['violation_count'] > 0  # Should have violations

        # Show sample violations
        print("\nViolations found:")
        for v in result['violations'][:3]:
            print(f"  - {v['file']}:{v['line']} [{v['severity']}] {v['message']}")

        print("✅ Test 2 PASSED: Violations correctly detected")


def test_code_standards_reviewer_disabled():
    """Test code standards reviewer when disabled"""
    print("\n=== Test 3: Reviewer Disabled ===")

    # Create temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write bad code
        test_file = Path(temp_dir) / "bad_code.py"
        test_file.write_text("""
def bad_code():
    if True:
        if True:
            if True:
                pass
""")

        # Create reviewer with disabled flag
        logger = get_logger("test")
        reviewer = CodeStandardsReviewer(
            logger=logger,
            severity_threshold="warning",
            enabled=False  # Disabled
        )

        # Run review
        result = reviewer.review_developer_code(
            developer_name="test-dev",
            code_directory=temp_dir
        )

        # Verify results
        print(f"✓ Enabled: {result['enabled']}")
        print(f"✓ Passed: {result['passed']}")
        print(f"✓ Violation count: {result['violation_count']}")

        assert result['enabled'] is False
        assert result['passed'] is True  # Should pass when disabled
        assert result['violation_count'] == 0  # No violations when disabled

        print("✅ Test 3 PASSED: Disabled reviewer works correctly")


def test_format_violations_for_report():
    """Test violation formatting for reports"""
    print("\n=== Test 4: Format Violations for Report ===")

    logger = get_logger("test")
    reviewer = CodeStandardsReviewer(
        logger=logger,
        severity_threshold="warning",
        enabled=True
    )

    # Sample violations
    violations = [
        {
            'file': 'src/example.py',
            'line': 42,
            'severity': 'critical',
            'message': 'Deeply nested if statement',
            'context': '        if condition:'
        },
        {
            'file': 'src/another.py',
            'line': 15,
            'severity': 'warning',
            'message': 'TODO comment found',
            'context': '    # TODO: fix this'
        }
    ]

    # Format violations
    markdown = reviewer.format_violations_for_report(violations)

    print("Generated Markdown Report:")
    print(markdown)

    # Verify markdown contains expected content
    assert "## Code Standards Violations" in markdown
    assert "src/example.py:42" in markdown
    assert "src/another.py:15" in markdown
    assert "critical" in markdown.lower()
    assert "warning" in markdown.lower()

    print("✅ Test 4 PASSED: Report formatting works correctly")


def test_directory_not_found():
    """Test handling of non-existent directory"""
    print("\n=== Test 5: Directory Not Found ===")

    logger = get_logger("test")
    reviewer = CodeStandardsReviewer(
        logger=logger,
        severity_threshold="warning",
        enabled=True
    )

    # Try to review non-existent directory
    result = reviewer.review_developer_code(
        developer_name="test-dev",
        code_directory="/non/existent/path"
    )

    # Verify error handling
    print(f"✓ Enabled: {result['enabled']}")
    print(f"✓ Passed: {result['passed']}")
    print(f"✓ Has error: {'error' in result}")

    assert result['enabled'] is True
    assert result['passed'] is False
    assert 'error' in result

    print("✅ Test 5 PASSED: Error handling works correctly")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Code Standards Integration Tests")
    print("="*60)

    try:
        test_code_standards_reviewer_clean_code()
        test_code_standards_reviewer_with_violations()
        test_code_standards_reviewer_disabled()
        test_format_violations_for_report()
        test_directory_not_found()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)

    except AssertionError as e:
        print("\n" + "="*60)
        print(f"❌ TEST FAILED: {e}")
        print("="*60)
        raise

    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ TEST ERROR: {e}")
        print("="*60)
        raise
