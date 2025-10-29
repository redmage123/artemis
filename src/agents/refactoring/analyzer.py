from artemis_logger import get_logger
logger = get_logger('analyzer')
'\nModule: Code Smell Analyzer - AST-Based Anti-Pattern Detection\n\nWHY: Separates code analysis logic from business logic and presentation.\n     Provides focused, testable components for each type of code smell.\n\nRESPONSIBILITY:\n    - Parse Python source code into AST\n    - Detect long methods (>50 lines)\n    - Identify simple loops convertible to comprehensions\n    - Find if/elif chains suitable for dictionary dispatch\n    - Aggregate analysis results into structured reports\n\nPATTERNS:\n    - Strategy Pattern: Different analyzers for different smell types\n    - Visitor Pattern: AST traversal for code inspection\n    - Single Responsibility: One analyzer per smell type\n'
import ast
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from .models import RefactoringAnalysis, LongMethodSmell, SimpleLoopSmell, IfElifChainSmell, PatternType, RefactoringPriority

class LongMethodAnalyzer:
    """
    Detects methods exceeding the 50-line threshold.

    WHY: Long methods violate Single Responsibility Principle and
         are harder to test, understand, and maintain.

    RESPONSIBILITY:
        - Traverse AST to find FunctionDef nodes
        - Measure method line counts
        - Generate long method smells for methods >50 lines
    """
    MAX_METHOD_LINES = 50

    def analyze(self, tree: ast.AST, file_path: str) -> List[LongMethodSmell]:
        """
        Find methods longer than MAX_METHOD_LINES.

        Args:
            tree: Python AST from ast.parse()
            file_path: Path to source file (for smell reporting)

        Returns:
            List of LongMethodSmell objects
        """
        smells = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            if not (hasattr(node, 'end_lineno') and hasattr(node, 'lineno')):
                continue
            length = node.end_lineno - node.lineno
            if length <= self.MAX_METHOD_LINES:
                continue
            smells.append(LongMethodSmell(file_path=file_path, line_number=node.lineno, pattern_type=PatternType.LONG_METHOD, suggestion=f'Extract helper methods from {node.name} ({length} lines)', priority=RefactoringPriority.CRITICAL, method_name=node.name, method_length=length))
        return smells

class SimpleLoopAnalyzer:
    """
    Detects simple for loops convertible to list/dict comprehensions.

    WHY: List comprehensions are more readable, faster (C-optimized),
         and more Pythonic than equivalent for loops.

    RESPONSIBILITY:
        - Find for loops with single-statement bodies
        - Identify append/add/update operations
        - Generate comprehension suggestions
    """
    SIMPLE_OPERATIONS = {'append', 'add', 'update'}

    def analyze(self, tree: ast.AST, file_path: str) -> List[SimpleLoopSmell]:
        """
        Find simple for loops suitable for comprehension conversion.

        Args:
            tree: Python AST from ast.parse()
            file_path: Path to source file

        Returns:
            List of SimpleLoopSmell objects
        """
        smells = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.For):
                continue
            if len(node.body) != 1:
                continue
            stmt = node.body[0]
            if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)):
                continue
            if not isinstance(stmt.value.func, ast.Attribute):
                continue
            method_name = stmt.value.func.attr
            if method_name not in self.SIMPLE_OPERATIONS:
                continue
            smells.append(SimpleLoopSmell(file_path=file_path, line_number=node.lineno, pattern_type=PatternType.LOOP, suggestion='Convert for loop to list/set/dict comprehension', priority=RefactoringPriority.HIGH, loop_operation=method_name))
        return smells

class IfElifChainAnalyzer:
    """
    Detects long if/elif chains (3+ branches) suitable for dict dispatch.

    WHY: Long if/elif chains are:
         - Harder to maintain (update multiple places)
         - Slower (linear vs constant-time dict lookup)
         - Less Pythonic (dict dispatch is idiomatic)

    RESPONSIBILITY:
        - Find if statements with multiple elif branches
        - Count branch depth
        - Generate dictionary dispatch suggestions
    """
    MIN_ELIF_COUNT = 3

    def analyze(self, tree: ast.AST, file_path: str) -> List[IfElifChainSmell]:
        """
        Find if/elif chains with 3+ branches.

        Args:
            tree: Python AST from ast.parse()
            file_path: Path to source file

        Returns:
            List of IfElifChainSmell objects
        """
        smells = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            elif_count = self._count_elif_branches(node)
            if elif_count < self.MIN_ELIF_COUNT:
                continue
            total_branches = elif_count + 1
            smells.append(IfElifChainSmell(file_path=file_path, line_number=node.lineno, pattern_type=PatternType.IF_ELIF, suggestion=f'Convert {total_branches}-branch if/elif to dictionary mapping', priority=RefactoringPriority.HIGH, elif_count=elif_count))
        return smells

    def _count_elif_branches(self, node: ast.If) -> int:
        """
        Count number of elif branches in an if statement.

        WHY: Guard clause pattern prevents deep nesting.
        """
        elif_count = 0
        current = node
        while hasattr(current, 'orelse') and len(current.orelse) == 1:
            if not isinstance(current.orelse[0], ast.If):
                break
            elif_count += 1
            current = current.orelse[0]
        return elif_count

class CodeSmellAnalyzer:
    """
    Orchestrates multiple smell analyzers to produce comprehensive analysis.

    WHY: Provides single entry point for all code smell detection.
         Uses Strategy Pattern to delegate to specialized analyzers.

    RESPONSIBILITY:
        - Coordinate multiple analyzer strategies
        - Handle file I/O and AST parsing
        - Aggregate analysis results
        - Handle errors gracefully

    PATTERN: Strategy Pattern with dispatch table
    """

    def __init__(self, logger: Optional[Any]=None, verbose: bool=True):
        """
        Initialize analyzer with logging configuration.

        Args:
            logger: Optional logger instance
            verbose: Enable verbose logging
        """
        self.logger = logger
        self.verbose = verbose
        self._analyzers: Dict[str, Callable] = {'long_methods': LongMethodAnalyzer().analyze, 'simple_loops': SimpleLoopAnalyzer().analyze, 'if_elif_chains': IfElifChainAnalyzer().analyze}

    def analyze_file(self, file_path: Path) -> RefactoringAnalysis:
        """
        Analyze a Python file for all code smell types.

        WHY: Single method provides complete analysis, simplifying client code.

        Args:
            file_path: Path to Python source file

        Returns:
            RefactoringAnalysis with all detected smells

        Raises:
            No exceptions - errors stored in analysis.error field
        """
        self._log(f'Analyzing {file_path.name} for refactoring opportunities...')
        try:
            source, tree = self._parse_file(file_path)
        except Exception as e:
            return RefactoringAnalysis(file_path=str(file_path), error=str(e))
        return RefactoringAnalysis(file_path=str(file_path), long_methods=self._analyzers['long_methods'](tree, str(file_path)), simple_loops=self._analyzers['simple_loops'](tree, str(file_path)), if_elif_chains=self._analyzers['if_elif_chains'](tree, str(file_path)))

    def _parse_file(self, file_path: Path) -> tuple:
        """
        Read and parse Python source file.

        WHY: Separate I/O from analysis logic.

        Returns:
            Tuple of (source_code, ast_tree)
        """
        with open(file_path, 'r') as f:
            source = f.read()
        tree = ast.parse(source)
        return (source, tree)

    def _log(self, message: str, level: str='INFO'):
        """
        Log message if verbose mode enabled.

        WHY: Consistent logging interface with optional backend.
        """
        if not self.verbose:
            return
        if self.logger:
            self.logger.log(message, level)
        else:
            
            logger.log(f'[Refactoring] {message}', 'INFO')