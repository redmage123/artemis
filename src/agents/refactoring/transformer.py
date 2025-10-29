from artemis_logger import get_logger
logger = get_logger('transformer')
'\nModule: Code Transformer - Automated Refactoring Application\n\nWHY: Provides infrastructure for applying automated code transformations.\n     Currently returns suggestions only, but extensible for future AST manipulation.\n\nRESPONSIBILITY:\n    - Define transformation strategy interface\n    - Provide safe transformation execution framework\n    - Handle transformation errors gracefully\n    - Return transformation results with metadata\n    - Support future AST-based transformations\n\nPATTERNS:\n    - Strategy Pattern: Different transformers for different refactoring types\n    - Template Method: Common transformation workflow\n    - Null Object Pattern: Safe no-op transformers\n'
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from .models import RefactoringAnalysis, PatternType, CodeSmell

class TransformationResult:
    """
    Encapsulates the result of a transformation attempt.

    WHY: Provides structured feedback about transformation success/failure.

    RESPONSIBILITY:
        - Store transformation status
        - Capture success/error messages
        - Track modified files
        - Preserve original analysis
    """

    def __init__(self, file_path: str, status: str, message: str, analysis: Optional[RefactoringAnalysis]=None, modified: bool=False):
        """
        Initialize transformation result.

        Args:
            file_path: Path to file that was transformed
            status: Status code (SUGGESTIONS_ONLY, SUCCESS, ERROR)
            message: Human-readable explanation
            analysis: Original analysis that prompted transformation
            modified: Whether file was actually modified
        """
        self.file_path = file_path
        self.status = status
        self.message = message
        self.analysis = analysis
        self.modified = modified

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary format.

        WHY: Maintains backward compatibility with original API.
        """
        result = {'file': self.file_path, 'status': self.status, 'message': self.message, 'modified': self.modified}
        if self.analysis:
            result['suggestions'] = self.analysis.to_dict()
        return result

    @property
    def is_successful(self) -> bool:
        """Check if transformation succeeded."""
        return self.status == 'SUCCESS'

    @property
    def is_error(self) -> bool:
        """Check if transformation encountered error."""
        return self.status == 'ERROR'

class TransformationStrategy:
    """
    Base class for refactoring transformation strategies.

    WHY: Defines contract for transformation implementations.
         Allows polymorphic transformation dispatch.

    RESPONSIBILITY:
        - Define transformation interface
        - Provide default no-op implementation
        - Handle errors consistently

    PATTERN: Strategy Pattern
    """

    def can_transform(self, smell: CodeSmell) -> bool:
        """
        Check if this strategy can transform the given smell.

        WHY: Guard clause for strategy selection.

        Args:
            smell: Code smell to check

        Returns:
            True if strategy can handle this smell type
        """
        return False

    def transform(self, file_path: Path, smell: CodeSmell) -> bool:
        """
        Apply transformation to fix code smell.

        WHY: Template method - subclasses override for actual transformation.

        Args:
            file_path: File to transform
            smell: Code smell to fix

        Returns:
            True if transformation succeeded, False otherwise
        """
        return False

class SuggestionsOnlyStrategy(TransformationStrategy):
    """
    Null object transformer that returns suggestions without modifying code.

    WHY: Automated AST transformation is risky and requires extensive validation.
         Better to provide suggestions and let developers review changes.

    RESPONSIBILITY:
        - Accept all smell types
        - Never modify source code
        - Return safe no-op results

    PATTERN: Null Object Pattern
    """

    def can_transform(self, smell: CodeSmell) -> bool:
        """Accept all smells but don't transform."""
        return True

    def transform(self, file_path: Path, smell: CodeSmell) -> bool:
        """No-op transformation - suggestions only."""
        return False

class ComprehensionTransformer(TransformationStrategy):
    """
    Future: Transform simple loops to comprehensions.

    WHY: Placeholder for future AST-based loop transformation.

    RESPONSIBILITY:
        - Identify simple loop patterns
        - Generate comprehension AST nodes
        - Preserve code semantics
        - Validate transformation correctness

    NOTE: Currently not implemented - returns False (no transformation)
    """

    def can_transform(self, smell: CodeSmell) -> bool:
        """Check if smell is a simple loop."""
        return smell.pattern_type == PatternType.LOOP

    def transform(self, file_path: Path, smell: CodeSmell) -> bool:
        """
        TODO: Implement comprehension transformation.

        WHY NOT IMPLEMENTED:
        - Requires complex AST manipulation
        - Must preserve variable scoping
        - Must handle edge cases (nested loops, side effects)
        - Needs extensive testing
        """
        return False

class DictionaryDispatchTransformer(TransformationStrategy):
    """
    Future: Transform if/elif chains to dictionary dispatch.

    WHY: Placeholder for future dictionary refactoring.

    RESPONSIBILITY:
        - Extract branch conditions and values
        - Generate dictionary mapping
        - Preserve default case handling
        - Validate semantic equivalence

    NOTE: Currently not implemented
    """

    def can_transform(self, smell: CodeSmell) -> bool:
        """Check if smell is an if/elif chain."""
        return smell.pattern_type == PatternType.IF_ELIF

    def transform(self, file_path: Path, smell: CodeSmell) -> bool:
        """
        TODO: Implement dictionary dispatch transformation.

        WHY NOT IMPLEMENTED:
        - Complex condition extraction
        - Must preserve side effects
        - Requires semantic analysis
        - Risk of changing behavior
        """
        return False

class CodeTransformer:
    """
    Orchestrates code transformations using strategy pattern.

    WHY: Provides single entry point for all transformation operations.
         Safely applies transformations with error handling.

    RESPONSIBILITY:
        - Select appropriate transformation strategy
        - Apply transformations safely
        - Handle errors gracefully
        - Return structured results
        - Log transformation attempts

    PATTERN: Strategy Pattern with dispatch table
    """

    def __init__(self, logger: Optional[Any]=None, verbose: bool=True):
        """
        Initialize transformer with transformation strategies.

        Args:
            logger: Optional logger instance
            verbose: Enable verbose logging
        """
        self.logger = logger
        self.verbose = verbose
        self._default_strategy = SuggestionsOnlyStrategy()
        self._strategies: List[TransformationStrategy] = [self._default_strategy]

    def apply_refactoring(self, file_path: Path, analysis: RefactoringAnalysis) -> TransformationResult:
        """
        Apply automated refactoring to a file.

        WHY: Currently returns suggestions only, but provides API for
             future automated transformations.

        Args:
            file_path: Path to file to refactor
            analysis: Analysis results with detected smells

        Returns:
            TransformationResult with status and suggestions
        """
        self._log(f'Applying automated refactoring to {file_path.name}...')
        if analysis.has_errors:
            return TransformationResult(file_path=str(file_path), status='ERROR', message=f'Analysis failed: {analysis.error}', analysis=analysis, modified=False)
        transformable_smells = self._get_transformable_smells(analysis)
        if not transformable_smells:
            return TransformationResult(file_path=str(file_path), status='SUGGESTIONS_ONLY', message='No automated transformations available - review suggestions', analysis=analysis, modified=False)
        modified = self._apply_transformations(file_path, transformable_smells)
        return TransformationResult(file_path=str(file_path), status='SUGGESTIONS_ONLY', message='Automated refactoring requires LLM or manual intervention', analysis=analysis, modified=modified)

    def _get_transformable_smells(self, analysis: RefactoringAnalysis) -> List[CodeSmell]:
        """
        Get list of smells that can be transformed.

        WHY: Filters smells by transformer capabilities.

        Args:
            analysis: Analysis results

        Returns:
            List of transformable code smells
        """
        transformable = []
        for smell in analysis.all_smells:
            for strategy in self._strategies:
                if strategy.can_transform(smell):
                    transformable.append(smell)
                    break
        return transformable

    def _apply_transformations(self, file_path: Path, smells: List[CodeSmell]) -> bool:
        """
        Apply transformations for all smells.

        WHY: Iterates through smells and applies appropriate strategy.

        Args:
            file_path: File to transform
            smells: List of code smells to fix

        Returns:
            True if any transformations were applied
        """
        modified = False
        for smell in smells:
            strategy = self._select_strategy(smell)
            if not strategy:
                continue
            try:
                if strategy.transform(file_path, smell):
                    modified = True
                    self._log(f'Transformed {smell.pattern_type.value} at line {smell.line_number}')
            except Exception as e:
                self._log(f'Transformation failed: {e}', 'ERROR')
        return modified

    def _select_strategy(self, smell: CodeSmell) -> Optional[TransformationStrategy]:
        """
        Select appropriate transformation strategy for smell.

        WHY: Strategy pattern dispatch logic.

        Args:
            smell: Code smell to transform

        Returns:
            Transformer strategy or None
        """
        for strategy in self._strategies:
            if strategy.can_transform(smell):
                return strategy
        return self._default_strategy

    def _log(self, message: str, level: str='INFO'):
        """Log message if verbose mode enabled."""
        if not self.verbose:
            return
        if self.logger:
            self.logger.log(message, level)
        else:
            
            logger.log(f'[Transformer] {message}', 'INFO')