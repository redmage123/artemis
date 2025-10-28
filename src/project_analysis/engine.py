#!/usr/bin/env python3
"""
WHY: Orchestrate analysis across all dimensions
RESPONSIBILITY: Coordinate analyzers and generate comprehensive analysis reports
PATTERNS: SOLID principles, Dependency Injection, Strategy Pattern, Guard clauses

This module coordinates dimension-specific analyzers to produce comprehensive
task analysis, following SOLID principles for extensibility and maintainability.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional

from debug_mixin import DebugMixin

from project_analysis.interfaces import DimensionAnalyzer
from project_analysis.models import Issue, Severity

# Import AIQueryService for centralized KG→RAG→LLM pipeline
try:
    from ai_query_service import create_ai_query_service
    AI_QUERY_SERVICE_AVAILABLE = True
except ImportError:
    AI_QUERY_SERVICE_AVAILABLE = False


class ProjectAnalysisEngine(DebugMixin):
    """
    WHY: SOLID principles - orchestrate analysis without knowing analyzer details
    RESPONSIBILITY: Coordinate analyzers, aggregate results, generate recommendations
    PATTERNS: Dependency Inversion (depends on DimensionAnalyzer interface),
              Open/Closed (extensible without modification),
              Single Responsibility (orchestration only)

    Coordinates analysis across all dimensions using pluggable analyzers.
    Can add new analyzers without modifying this class (Open/Closed Principle).
    Depends on DimensionAnalyzer abstraction (Dependency Inversion Principle).
    """

    def __init__(
        self,
        analyzers: Optional[List[DimensionAnalyzer]] = None,
        llm_client: Optional[Any] = None,
        config: Optional[Any] = None,
        enable_llm_analysis: bool = True,
        ai_service: Optional[Any] = None,
        rag: Optional[Any] = None
    ):
        """
        Initialize with dependency injection.

        Args:
            analyzers: List of dimension analyzers (injected)
            llm_client: LLM client for AI-powered analysis
            config: Configuration agent
            enable_llm_analysis: Enable LLM-powered analysis (default: True)
            ai_service: AI Query Service for KG-First queries (optional)
            rag: RAG agent for pattern retrieval (optional)
        """
        DebugMixin.__init__(self, component_name="project_analysis")

        # Initialize AI Query Service if not provided
        ai_service = self._initialize_ai_service(ai_service, llm_client, rag)
        self.ai_service = ai_service

        # Create analyzers list
        self.analyzers = self._create_analyzers(
            analyzers, enable_llm_analysis, llm_client, config, ai_service
        )

        self.llm_client = llm_client
        self.config = config
        self.debug_log(
            "ProjectAnalysisEngine initialized",
            analyzer_count=len(self.analyzers),
            llm_enabled=enable_llm_analysis
        )

    def _initialize_ai_service(
        self,
        ai_service: Optional[Any],
        llm_client: Optional[Any],
        rag: Optional[Any]
    ) -> Optional[Any]:
        """
        Initialize AI Query Service if not provided.

        Guard clauses prevent unnecessary initialization.

        Args:
            ai_service: Existing AI Query Service (if any)
            llm_client: LLM client for creating new service
            rag: RAG agent for creating new service

        Returns:
            AI Query Service instance or None
        """
        # Guard clause: Service already provided
        if ai_service:
            return ai_service

        # Guard clause: Dependencies unavailable
        if not llm_client or not AI_QUERY_SERVICE_AVAILABLE:
            return None

        try:
            return create_ai_query_service(
                llm_client=llm_client,
                rag=rag,
                logger=None,
                verbose=False
            )
        except Exception:
            return None

    def _create_analyzers(
        self,
        analyzers: Optional[List[DimensionAnalyzer]],
        enable_llm_analysis: bool,
        llm_client: Optional[Any],
        config: Optional[Any],
        ai_service: Optional[Any]
    ) -> List[DimensionAnalyzer]:
        """
        Create list of analyzers with optional LLM-powered analyzer.

        Guard clause: Use provided analyzers if available.

        Args:
            analyzers: Pre-configured analyzers (if provided)
            enable_llm_analysis: Whether to enable LLM analysis
            llm_client: LLM client for LLM-powered analyzer
            config: Configuration agent
            ai_service: AI Query Service

        Returns:
            List of dimension analyzers
        """
        # Guard clause: Analyzers already provided
        if analyzers is not None:
            return analyzers

        # Import here to avoid circular dependencies
        from project_analysis.analyzers.rule_based import (
            ErrorHandlingAnalyzer,
            PerformanceAnalyzer,
            ScopeAnalyzer,
            SecurityAnalyzer,
            TestingAnalyzer,
        )

        # Default analyzers (rule-based)
        default_analyzers = [
            ScopeAnalyzer(),
            SecurityAnalyzer(),
            PerformanceAnalyzer(),
            TestingAnalyzer(),
            ErrorHandlingAnalyzer()
        ]

        # Guard clause: LLM analysis disabled or unavailable
        if not enable_llm_analysis or not llm_client:
            return default_analyzers

        # Add LLM-powered analyzer
        from project_analysis.analyzers.llm_powered import LLMPoweredAnalyzer
        default_analyzers.append(LLMPoweredAnalyzer(llm_client, config, ai_service))
        return default_analyzers

    def analyze_task(self, card: Dict, context: Dict) -> Dict:
        """
        Analyze task across all dimensions.

        Open/Closed Principle: Can add analyzers without changing this method.

        Args:
            card: Kanban card with task details
            context: Pipeline context (RAG recommendations, etc.)

        Returns:
            Dict with complete analysis results including:
            - total_issues: Total number of issues found
            - critical_count: Number of critical issues
            - high_count: Number of high-priority issues
            - medium_count: Number of medium-priority issues
            - dimensions_analyzed: Number of dimensions analyzed
            - results: List of AnalysisResult objects
            - critical_issues: List of critical Issue objects
            - high_issues: List of high-priority Issue objects
            - medium_issues: List of medium-priority Issue objects
            - recommendation: Overall recommendation (REJECT/APPROVE_CRITICAL/APPROVE_ALL)
            - recommendation_reason: Explanation for recommendation
        """
        self.debug_trace("analyze_task", task_title=card.get('title', 'Unknown'))

        results = []
        all_issues = []

        # Run each analyzer (Open/Closed: can add analyzers without changing this)
        for analyzer in self.analyzers:
            result = analyzer.analyze(card, context)
            results.append(result)
            all_issues.extend(result.issues)

        # Categorize issues by severity (Performance: Single-pass O(n) vs O(3n))
        issues_by_severity = defaultdict(list)
        for issue in all_issues:
            issues_by_severity[issue.severity].append(issue)

        critical_issues = issues_by_severity[Severity.CRITICAL]
        high_issues = issues_by_severity[Severity.HIGH]
        medium_issues = issues_by_severity[Severity.MEDIUM]

        # Generate recommendation based on severity
        recommendation, recommendation_reason = self._generate_recommendation(
            critical_issues, high_issues, medium_issues
        )

        # Generate summary
        summary = {
            "total_issues": len(all_issues),
            "critical_count": len(critical_issues),
            "high_count": len(high_issues),
            "medium_count": len(medium_issues),
            "dimensions_analyzed": len(self.analyzers),
            "results": results,
            "critical_issues": critical_issues,
            "high_issues": high_issues,
            "medium_issues": medium_issues,
            "recommendation": recommendation,  # Agent's recommendation
            "recommendation_reason": recommendation_reason
        }

        self.debug_dump_if_enabled("analysis_summary", "Analysis Summary", {
            "total_issues": len(all_issues),
            "critical": len(critical_issues),
            "high": len(high_issues),
            "recommendation": recommendation
        })

        return summary

    def _generate_recommendation(
        self,
        critical_issues: List[Issue],
        high_issues: List[Issue],
        medium_issues: List[Issue]
    ) -> tuple:
        """
        Generate recommendation based on issue severity.

        Dispatch table pattern using guard clauses for clarity.

        Args:
            critical_issues: List of critical severity issues
            high_issues: List of high severity issues
            medium_issues: List of medium severity issues

        Returns:
            Tuple of (recommendation, recommendation_reason)
        """
        # Guard clause: Critical issues found
        if critical_issues:
            return "REJECT", f"Found {len(critical_issues)} CRITICAL issues that must be fixed"

        # Guard clause: Too many high-priority issues
        if len(high_issues) > 5:
            return "APPROVE_CRITICAL", f"Found {len(high_issues)} HIGH-priority issues - consider fixing"

        # Default: Approve with suggestions
        return "APPROVE_ALL", f"No critical issues found - {len(high_issues)} high, {len(medium_issues)} medium priority improvements suggested"


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def analyze_project(card: Dict, context: Optional[Dict] = None) -> Dict:
    """
    Convenience function to analyze a project.

    Provides simple API for one-off analysis without creating engine instance.

    Args:
        card: Kanban card with task details
        context: Optional pipeline context

    Returns:
        Complete analysis results (see analyze_task for structure)
    """
    context = context or {}
    engine = ProjectAnalysisEngine()
    return engine.analyze_task(card, context)
