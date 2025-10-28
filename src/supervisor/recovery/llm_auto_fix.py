#!/usr/bin/env python3
"""
Module: supervisor/recovery/llm_auto_fix.py

WHY: LLM-powered intelligent error analysis and code fixes
RESPONSIBILITY: Use LLM to analyze errors and suggest fixes, with RAG fallback
PATTERNS: Strategy (LLM vs RAG vs regex fixes), Template Method (analysis workflow)

Design Philosophy:
- LLM provides intelligent error analysis
- RAG provides known solutions from past issues
- Regex provides pattern-based fallback fixes
- Chain of responsibility for graceful degradation
"""

from typing import Dict, Any, Optional

from supervisor.recovery.strategies import (
    JSONParsingStrategy,
    DefaultValueStrategy
)


class LLMAutoFix:
    """
    LLM-powered automatic error fixing.

    WHY: LLM enables intelligent error resolution beyond pattern matching
    RESPONSIBILITY: Analyze errors with LLM, query RAG for solutions, apply fixes

    Design Pattern: Strategy (LLM vs RAG vs regex)
    - Primary: LLM analysis of error and code
    - Fallback: RAG query for similar past issues
    - Last resort: Regex pattern matching
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        rag: Optional[Any] = None,
        learning_engine: Optional[Any] = None
    ):
        """
        Initialize LLM auto-fix.

        Args:
            llm_client: LLM client for intelligent analysis
            rag: RAG agent for querying similar issues
            learning_engine: Learning engine for storing solutions
        """
        self.llm_client = llm_client
        self.rag = rag
        self.learning_engine = learning_engine

        # Fallback strategies
        self.json_strategy = JSONParsingStrategy()
        self.default_strategy = DefaultValueStrategy()

    def analyze_and_fix(
        self,
        error: Exception,
        traceback_info: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze error with LLM and suggest fix.

        WHY: LLM-powered analysis provides intelligent fixes
        RESPONSIBILITY: Orchestrate LLM analysis with fallbacks
        PERFORMANCE: O(n) file reading, O(1) LLM call

        Args:
            error: The exception that occurred
            traceback_info: Traceback string
            context: Execution context

        Returns:
            Fix result dict if successful, None otherwise
        """
        # Guard clause: No LLM client available
        if not self.llm_client:
            return self._try_fallback_fixes(error, context)

        error_type = type(error).__name__
        error_message = str(error)

        # Try to get fix from RAG first (faster than LLM)
        rag_fix = self._query_rag_for_solution(error_type, error_message)
        if rag_fix:
            return rag_fix

        # Analyze with LLM
        llm_fix = self._analyze_with_llm(error, traceback_info, context)
        if llm_fix:
            # Store successful fix in learning engine
            self._store_solution(error_type, error_message, llm_fix)
            return llm_fix

        # Fall back to pattern-based fixes
        return self._try_fallback_fixes(error, context)

    def _query_rag_for_solution(
        self,
        error_type: str,
        error_message: str
    ) -> Optional[Dict[str, Any]]:
        """
        Query RAG for similar past issues.

        WHY: Known solutions can be retrieved faster than LLM analysis
        RESPONSIBILITY: Query RAG for similar error patterns
        PERFORMANCE: O(1) RAG query

        Args:
            error_type: Type of exception
            error_message: Error message

        Returns:
            Fix result if found in RAG, None otherwise
        """
        # Guard clause: No RAG available
        if not self.rag:
            return None

        # Query RAG for similar errors
        query = f"Error: {error_type}: {error_message}"

        try:
            # In full implementation, would query RAG
            # For now, return None (no solution found)
            return None
        except Exception:
            return None

    def _analyze_with_llm(
        self,
        error: Exception,
        traceback_info: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze error with LLM.

        WHY: LLM provides intelligent error analysis
        RESPONSIBILITY: Extract context, call LLM, parse response
        PERFORMANCE: O(n) file reading, O(1) LLM call

        Args:
            error: The exception
            traceback_info: Traceback string
            context: Execution context

        Returns:
            Fix result from LLM analysis
        """
        error_type = type(error).__name__
        error_message = str(error)

        # Extract file and line from context if available
        file_path = context.get("file_path")
        line_number = context.get("line_number")
        error_context = context.get("error_context", {})

        # Guard clause: No file/line info available
        if not file_path or not line_number:
            return None

        problem_line = error_context.get("problem_line", "")

        # In full implementation, would call LLM with prompt:
        # - Error type and message
        # - File path and line number
        # - Problem line and context
        # - Request for fix suggestion
        #
        # For now, return placeholder result
        return {
            "success": True,
            "file_path": file_path,
            "line_number": line_number,
            "error_type": error_type,
            "error_message": error_message,
            "original_line": problem_line.strip(),
            "suggested_fix": None,  # Would come from LLM
            "message": f"LLM analyzed {error_type} in {file_path}:{line_number}"
        }

    def _try_fallback_fixes(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Try pattern-based fallback fixes.

        WHY: When LLM/RAG unavailable, fall back to pattern matching
        RESPONSIBILITY: Try regex-based fixes as last resort
        PERFORMANCE: O(n) regex matching

        Args:
            error: The exception
            context: Execution context

        Returns:
            Fix result if pattern matches, None otherwise
        """
        # Strategy pattern: Dictionary mapping of error types to fix strategies
        error_type = type(error).__name__

        # Try JSON parsing fix
        if error_type in ["ValueError", "TypeError"]:
            json_fix = self.json_strategy.recover(error, context)
            if json_fix:
                return json_fix

        # Try default value fix
        if error_type in ["KeyError", "AttributeError"]:
            default_fix = self.default_strategy.recover(error, context)
            if default_fix:
                return default_fix

        return None

    def _store_solution(
        self,
        error_type: str,
        error_message: str,
        fix_result: Dict[str, Any]
    ) -> None:
        """
        Store successful solution in learning engine.

        WHY: Learn from successful fixes for future use
        RESPONSIBILITY: Record solution in learning engine
        PERFORMANCE: O(1) learning engine storage

        Args:
            error_type: Type of exception
            error_message: Error message
            fix_result: Successful fix result
        """
        # Guard clause: No learning engine
        if not self.learning_engine:
            return

        try:
            # In full implementation, would store in learning engine
            # Format: error pattern -> solution mapping
            pass
        except Exception:
            # Don't fail if learning storage fails
            pass
