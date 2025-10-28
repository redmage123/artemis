#!/usr/bin/env python3
"""
Test backward compatibility of refactored exceptions module.

WHY: Verify that all existing imports continue working after refactoring.
     100% backward compatibility is CRITICAL - no existing code should break.

RESPONSIBILITY: Test all exception types and utilities can be imported from
                both old style (core.exceptions) and new style (core.exceptions.X).
"""

import sys


def test_base_exception_import():
    """Test base exception can be imported (old style)."""
    from core.exceptions import ArtemisException

    # Test instantiation
    exc = ArtemisException(
        "Test error",
        context={"test": "value"},
        original_exception=ValueError("original")
    )

    assert exc.message == "Test error"
    assert exc.context == {"test": "value"}
    assert isinstance(exc.original_exception, ValueError)
    print("✓ Base exception import works")


def test_database_exceptions_import():
    """Test database exceptions can be imported (old style)."""
    from core.exceptions import (
        RAGException, RAGError, RAGQueryError, RAGStorageError, RAGConnectionError,
        RedisException, RedisConnectionError, RedisCacheError,
        KnowledgeGraphError, KGQueryError, KGConnectionError
    )

    # Test instantiation
    exc = RAGQueryError("Query failed", context={"query": "test"})
    assert exc.message == "Query failed"
    assert RAGError is RAGException  # Test alias
    print("✓ Database exceptions import works")


def test_llm_exceptions_import():
    """Test LLM exceptions can be imported (old style)."""
    from core.exceptions import (
        LLMException, LLMError, LLMClientError, LLMAPIError,
        LLMResponseParsingError, LLMRateLimitError, LLMAuthenticationError
    )

    # Test instantiation
    exc = LLMRateLimitError("Rate limit hit", context={"limit": 100})
    assert exc.message == "Rate limit hit"
    assert LLMError is LLMException  # Test alias
    print("✓ LLM exceptions import works")


def test_agent_exceptions_import():
    """Test agent exceptions can be imported (old style)."""
    from core.exceptions import (
        DeveloperException, DeveloperExecutionError, DeveloperPromptError,
        DeveloperOutputError, CodeReviewException, CodeReviewExecutionError,
        CodeReviewScoringError, CodeReviewFeedbackError
    )

    # Test instantiation
    exc = DeveloperExecutionError("Execution failed", context={"agent": "dev-a"})
    assert exc.message == "Execution failed"
    print("✓ Agent exceptions import works")


def test_parsing_exceptions_import():
    """Test parsing exceptions can be imported (old style)."""
    from core.exceptions import (
        RequirementsException, RequirementsFileError, RequirementsParsingError,
        RequirementsValidationError, RequirementsExportError,
        UnsupportedDocumentFormatError, DocumentReadError
    )

    # Test instantiation
    exc = RequirementsParsingError("Parse failed", context={"file": "test.pdf"})
    assert exc.message == "Parse failed"
    print("✓ Parsing exceptions import works")


def test_pipeline_exceptions_import():
    """Test pipeline exceptions can be imported (old style)."""
    from core.exceptions import (
        PipelineException, PipelineStageError, PipelineValidationError,
        PipelineConfigurationError, ConfigurationError
    )

    # Test instantiation
    exc = PipelineStageError("Stage failed", context={"stage": "architecture"})
    assert exc.message == "Stage failed"
    print("✓ Pipeline exceptions import works")


def test_workflow_exceptions_import():
    """Test workflow exceptions can be imported (old style)."""
    from core.exceptions import (
        KanbanException, KanbanCardNotFoundError, KanbanBoardError,
        KanbanWIPLimitError, SprintException, SprintPlanningError,
        FeatureExtractionError, PlanningPokerError, SprintAllocationError,
        ProjectReviewError, RetrospectiveError, UIUXEvaluationError,
        WCAGEvaluationError, GDPREvaluationError
    )

    # Test instantiation
    exc = KanbanWIPLimitError("WIP exceeded", context={"limit": 5})
    assert exc.message == "WIP exceeded"
    print("✓ Workflow exceptions import works")


def test_filesystem_exceptions_import():
    """Test filesystem exceptions can be imported (old style)."""
    from core.exceptions import (
        ArtemisFileError, FileNotFoundError, FileWriteError, FileReadError
    )

    # Test instantiation
    exc = FileReadError("Read failed", context={"file": "/path/test.py"})
    assert exc.message == "Read failed"
    print("✓ Filesystem exceptions import works")


def test_analysis_exceptions_import():
    """Test analysis exceptions can be imported (old style)."""
    from core.exceptions import (
        ProjectAnalysisException, ADRGenerationError, DependencyAnalysisError
    )

    # Test instantiation
    exc = ADRGenerationError("ADR failed", context={"adr_id": "ADR-001"})
    assert exc.message == "ADR failed"
    print("✓ Analysis exceptions import works")


def test_utilities_import():
    """Test utilities can be imported (old style)."""
    from core.exceptions import create_wrapped_exception, wrap_exception, LLMAPIError

    # Test create_wrapped_exception
    original = ValueError("original error")
    wrapped = create_wrapped_exception(
        original,
        LLMAPIError,
        "Wrapped error",
        {"context": "test"}
    )
    assert wrapped.message == "Wrapped error"
    assert wrapped.original_exception is original

    # Test wrap_exception decorator
    @wrap_exception(LLMAPIError, "Function failed")
    def test_function():
        raise ValueError("test error")

    try:
        test_function()
        assert False, "Should have raised exception"
    except LLMAPIError as e:
        assert "Function failed" in e.message
        assert isinstance(e.original_exception, ValueError)

    print("✓ Utilities import works")


def test_new_style_imports():
    """Test new style imports work (from specific modules)."""
    from core.exceptions.base import ArtemisException
    from core.exceptions.database import RAGException
    from core.exceptions.llm import LLMAPIError
    from core.exceptions.agents import DeveloperException
    from core.exceptions.parsing import RequirementsException
    from core.exceptions.pipeline import PipelineException
    from core.exceptions.workflow import KanbanException
    from core.exceptions.filesystem import ArtemisFileError
    from core.exceptions.analysis import ProjectAnalysisException
    from core.exceptions.utilities import wrap_exception

    print("✓ New style imports work")


def test_exception_hierarchy():
    """Test exception hierarchy is preserved."""
    from core.exceptions import (
        ArtemisException, RAGException, RAGQueryError,
        LLMException, LLMRateLimitError
    )

    # Test inheritance
    assert issubclass(RAGException, ArtemisException)
    assert issubclass(RAGQueryError, RAGException)
    assert issubclass(RAGQueryError, ArtemisException)

    assert issubclass(LLMException, ArtemisException)
    assert issubclass(LLMRateLimitError, LLMException)
    assert issubclass(LLMRateLimitError, ArtemisException)

    print("✓ Exception hierarchy preserved")


def test_exception_str_formatting():
    """Test exception string formatting with context."""
    from core.exceptions import LLMAPIError

    exc = LLMAPIError(
        "API call failed",
        context={"model": "gpt-4", "timeout": 30},
        original_exception=ValueError("connection error")
    )

    exc_str = str(exc)
    assert "API call failed" in exc_str
    assert "model=gpt-4" in exc_str
    assert "timeout=30" in exc_str
    assert "ValueError" in exc_str
    assert "connection error" in exc_str

    print("✓ Exception string formatting works")


def run_all_tests():
    """Run all backward compatibility tests."""
    print("\n" + "="*60)
    print("BACKWARD COMPATIBILITY TEST SUITE")
    print("="*60 + "\n")

    tests = [
        test_base_exception_import,
        test_database_exceptions_import,
        test_llm_exceptions_import,
        test_agent_exceptions_import,
        test_parsing_exceptions_import,
        test_pipeline_exceptions_import,
        test_workflow_exceptions_import,
        test_filesystem_exceptions_import,
        test_analysis_exceptions_import,
        test_utilities_import,
        test_new_style_imports,
        test_exception_hierarchy,
        test_exception_str_formatting,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} FAILED: {e}")

    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
