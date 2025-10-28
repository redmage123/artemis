"""
WHY: UI/UX evaluation subpackage
RESPONSIBILITY: Provide backward compatibility and expose public API
PATTERNS: Facade pattern for package exports

Part of: src

This package contains the modularized UI/UX evaluation components:
- models: Value objects for evaluation results (DeveloperEvaluation)
- score_calculator: UX score calculation and status determination
- accessibility_evaluator: WCAG 2.1 AA accessibility evaluation
- gdpr_evaluator: GDPR compliance evaluation
- ui_analyzer: UI file detection and analysis
- feedback_manager: Developer feedback and agent notifications
- kg_storage: Knowledge Graph and RAG storage
- uiux_stage_core: Main UIUXStage orchestrator

BACKWARD COMPATIBILITY:
All components are re-exported for backward compatibility with existing code.
"""

# Import all public components
from .models import DeveloperEvaluation
from .score_calculator import ScoreCalculator
from .accessibility_evaluator import AccessibilityEvaluator
from .gdpr_evaluator import GDPRComplianceEvaluator
from .ui_analyzer import UIFileAnalyzer
from .feedback_manager import FeedbackManager
from .kg_storage import EvaluationStorage
from .uiux_stage_core import UIUXStage

__all__ = [
    # Main stage class
    "UIUXStage",

    # Value objects
    "DeveloperEvaluation",

    # Evaluators
    "AccessibilityEvaluator",
    "GDPRComplianceEvaluator",
    "UIFileAnalyzer",

    # Support components
    "ScoreCalculator",
    "FeedbackManager",
    "EvaluationStorage",
]
