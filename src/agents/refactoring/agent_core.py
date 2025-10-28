#!/usr/bin/env python3
"""
Module: Code Refactoring Agent Core - Main Orchestration

WHY: Provides high-level API for code refactoring operations.
     Coordinates analyzer, suggestion generator, and transformer components.

RESPONSIBILITY:
    - Orchestrate refactoring workflow
    - Provide backward-compatible API
    - Delegate to specialized components
    - Handle logging configuration
    - Expose factory function for agent creation

PATTERNS:
    - Facade Pattern: Simplifies complex subsystem interactions
    - Dependency Injection: Logger injection for flexible logging
    - Factory Pattern: create_refactoring_agent() factory function
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from .models import RefactoringAnalysis, RefactoringRule, PatternType, RefactoringPriority
from .analyzer import CodeSmellAnalyzer
from .suggestion_generator import RefactoringSuggestionGenerator
from .transformer import CodeTransformer, TransformationResult


class CodeRefactoringAgent:
    """
    Automated code refactoring agent for Python codebases.

    WHY: Provides unified interface for code analysis, suggestion generation,
         and automated refactoring. Orchestrates specialized components.

    RESPONSIBILITY:
        - Coordinate analyzer, generator, and transformer
        - Provide backward-compatible API
        - Handle logging configuration
        - Expose refactoring rules metadata

    PATTERN: Facade Pattern - simplifies subsystem interactions

    Attributes:
        REFACTORING_RULES: Class-level metadata about supported refactoring rules
    """

    # Class-level refactoring rules metadata
    REFACTORING_RULES = [
        RefactoringRule(
            name="loop_to_comprehension",
            pattern_type=PatternType.LOOP,
            description="Convert simple for loops to list/dict comprehensions",
            priority=RefactoringPriority.HIGH
        ),
        RefactoringRule(
            name="if_elif_to_mapping",
            pattern_type=PatternType.IF_ELIF,
            description="Convert long if/elif chains to dictionary mapping",
            priority=RefactoringPriority.HIGH
        ),
        RefactoringRule(
            name="extract_long_method",
            pattern_type=PatternType.LONG_METHOD,
            description="Extract methods longer than 50 lines",
            priority=RefactoringPriority.CRITICAL
        ),
        RefactoringRule(
            name="use_next_for_first_match",
            pattern_type=PatternType.GENERATOR,
            description="Use next() with generator for first-match patterns",
            priority=RefactoringPriority.MEDIUM
        ),
        RefactoringRule(
            name="use_collections_module",
            pattern_type=PatternType.COLLECTIONS,
            description="Use defaultdict, Counter, chain from collections",
            priority=RefactoringPriority.MEDIUM
        ),
    ]

    def __init__(self, logger: Optional[Any] = None, verbose: bool = True):
        """
        Initialize refactoring agent with dependencies.

        WHY: Dependency injection allows flexible logging backends.
             Component initialization is centralized.

        Args:
            logger: Optional logger instance for structured logging.
                   If None, uses simple print statements.
            verbose: Enable verbose logging to track refactoring analysis progress.
                    Useful for debugging but can be noisy in production.
        """
        self.logger = logger
        self.verbose = verbose

        # Initialize components with shared logging config
        self._analyzer = CodeSmellAnalyzer(logger=logger, verbose=verbose)
        self._suggestion_generator = RefactoringSuggestionGenerator()
        self._transformer = CodeTransformer(logger=logger, verbose=verbose)

    def analyze_file_for_refactoring(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a Python file for refactoring opportunities.

        WHY: Maintains backward compatibility with original API.
             Delegates to analyzer component for separation of concerns.

        Args:
            file_path: Path object pointing to Python source file.
                      Must be readable and contain valid Python syntax.

        Returns:
            Dict containing:
                - 'file': str path to analyzed file
                - 'long_methods': List[Dict] of methods exceeding 50 lines
                - 'simple_loops': List[Dict] of for loops that could be comprehensions
                - 'if_elif_chains': List[Dict] of if/elif chains (3+ branches)
                - 'total_issues': int count of all detected issues
                - 'error': str (only if parsing fails)
        """
        analysis = self._analyzer.analyze_file(file_path)
        return analysis.to_dict()

    def generate_refactoring_instructions(
        self,
        analysis: Dict[str, Any],
        code_review_issues: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate detailed, actionable refactoring instructions.

        WHY: Maintains backward compatibility with original API.
             Delegates to suggestion generator for formatting logic.

        Args:
            analysis: Dict from analyze_file_for_refactoring() containing:
                - long_methods, simple_loops, if_elif_chains lists
                - file path and total issue count
            code_review_issues: Optional list of code review findings to merge.
                Allows combining automated and human review feedback.

        Returns:
            Markdown-formatted instruction document with:
                - File header and issue count
                - Categorized refactoring suggestions
                - Code review issues (if provided)
                - Best practices summary
        """
        # Convert dict back to RefactoringAnalysis for internal use
        refactoring_analysis = self._dict_to_analysis(analysis)

        return self._suggestion_generator.generate_instructions(
            refactoring_analysis,
            code_review_issues
        )

    def apply_automated_refactoring(
        self,
        file_path: Path,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply automated refactoring to a file (currently suggestions-only).

        WHY: Maintains backward compatibility with original API.
             Delegates to transformer for future transformation logic.

        Args:
            file_path: Path to Python file to refactor
            analysis: Analysis results from analyze_file_for_refactoring()

        Returns:
            Dict with:
                - 'file': str path
                - 'status': 'SUGGESTIONS_ONLY'
                - 'message': Explanation of why automation is limited
                - 'suggestions': Copy of analysis for reference
                - 'modified': bool indicating if file was changed
        """
        # Convert dict to RefactoringAnalysis
        refactoring_analysis = self._dict_to_analysis(analysis)

        # Apply transformation (currently no-op)
        result = self._transformer.apply_refactoring(file_path, refactoring_analysis)

        return result.to_dict()

    def log(self, message: str, level: str = "INFO"):
        """
        Log a message with optional severity level.

        WHY: Provides consistent logging interface regardless of logger backend.
             Respects user's preference for verbosity to avoid log spam.

        Args:
            message: The log message text to output
            level: Severity level (INFO, WARNING, ERROR) for log filtering
        """
        if not self.verbose:
            return

        if self.logger:
            self.logger.log(message, level)
        else:
            print(f"[Refactoring] {message}")

    def _dict_to_analysis(self, analysis_dict: Dict[str, Any]) -> RefactoringAnalysis:
        """
        Convert dictionary analysis to RefactoringAnalysis object.

        WHY: Internal methods use typed objects for safety.
             Maintains backward compatibility by accepting dicts.

        Args:
            analysis_dict: Dictionary from analyze_file_for_refactoring()

        Returns:
            RefactoringAnalysis object
        """
        from .models import LongMethodSmell, SimpleLoopSmell, IfElifChainSmell

        # Guard: Handle error case
        if 'error' in analysis_dict:
            return RefactoringAnalysis(
                file_path=analysis_dict.get('file', ''),
                error=analysis_dict['error']
            )

        file_path = analysis_dict.get('file', '')

        # Convert long methods
        long_methods = [
            LongMethodSmell(
                file_path=file_path,
                line_number=method['line'],
                pattern_type=PatternType.LONG_METHOD,
                suggestion=method['suggestion'],
                priority=RefactoringPriority.CRITICAL,
                method_name=method['name'],
                method_length=method['length']
            )
            for method in analysis_dict.get('long_methods', [])
        ]

        # Convert simple loops
        simple_loops = [
            SimpleLoopSmell(
                file_path=file_path,
                line_number=loop['line'],
                pattern_type=PatternType.LOOP,
                suggestion=loop['suggestion'],
                priority=RefactoringPriority.HIGH
            )
            for loop in analysis_dict.get('simple_loops', [])
        ]

        # Convert if/elif chains
        if_elif_chains = [
            IfElifChainSmell(
                file_path=file_path,
                line_number=chain['line'],
                pattern_type=PatternType.IF_ELIF,
                suggestion=chain['suggestion'],
                priority=RefactoringPriority.HIGH,
                elif_count=chain['elif_count']
            )
            for chain in analysis_dict.get('if_elif_chains', [])
        ]

        return RefactoringAnalysis(
            file_path=file_path,
            long_methods=long_methods,
            simple_loops=simple_loops,
            if_elif_chains=if_elif_chains
        )


def create_refactoring_agent(logger: Optional[Any] = None, verbose: bool = True) -> CodeRefactoringAgent:
    """
    Factory function to create refactoring agent instance.

    WHY: Factory pattern provides consistent creation interface and
         allows future extensions (e.g., configuration file support)
         without changing client code.

    RESPONSIBILITY:
        - Create configured CodeRefactoringAgent
        - Provide single creation point for dependency injection

    PATTERN: Factory Pattern

    Args:
        logger: Optional logger for tracking refactoring operations.
               Defaults to None (uses print statements).
        verbose: Enable detailed logging of analysis steps.
                Recommended for development, disable in production.

    Returns:
        Fully initialized CodeRefactoringAgent ready for use.
    """
    return CodeRefactoringAgent(logger=logger, verbose=verbose)
