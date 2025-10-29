"""
Adaptive Pipeline Builder

WHY: Artemis should intelligently choose pipeline complexity based on task type.
     A simple HTML file doesn't need 114 minutes and 11 stages!

RESPONSIBILITY:
- Detect task complexity (simple/medium/complex)
- Build appropriate pipeline (fast/medium/full)
- Optimize for speed without sacrificing quality

PATTERNS:
- Strategy Pattern: Different pipeline strategies for different complexities
- Builder Pattern: Construct pipelines step-by-step
- Decision Tree: Rule-based task classification

DESIGN DECISION:
Instead of always running the full enterprise pipeline, intelligently detect:
- Simple tasks (HTML/CSS only) → Fast path (5-10 min)
- Medium tasks (multi-file, some logic) → Medium path (30-40 min)
- Complex tasks (full-stack, databases) → Full path (60-120 min)
"""

from typing import Dict, List, Optional
from enum import Enum
from artemis_logger import get_logger

logger = get_logger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels."""
    SIMPLE = "simple"      # Single file, frontend only, no backend
    MEDIUM = "medium"      # Multiple files, some backend logic
    COMPLEX = "complex"    # Full-stack, databases, services


class PipelinePath(Enum):
    """Pipeline execution paths."""
    FAST = "fast"          # 5-10 minutes: Minimal stages
    MEDIUM = "medium"      # 30-40 minutes: Core stages
    FULL = "full"          # 60-120 minutes: All stages


class TaskComplexityDetector:
    """
    Intelligently detect task complexity from requirements.

    WHY: Avoid over-engineering simple tasks with complex pipelines.
    """

    def __init__(self):
        """Initialize detector with classification rules."""
        self.simple_indicators = {
            # File type indicators
            'single_file': ['single html', 'one file', 'static page'],
            'frontend_only': ['html', 'css', 'static', 'presentation', 'demo page'],
            'no_backend': ['no server', 'no api', 'no database', 'client-side only'],

            # Complexity indicators
            'low_complexity': ['simple', 'basic', 'straightforward', 'minimal'],
            'small_scope': ['quick', 'small', 'brief', 'short'],

            # Task type indicators (ADDED)
            'refactor': ['refactor', 'modernize', 'update function', 'replace callback', 'async/await'],
            'bugfix': ['fix', 'bug', 'issue', 'alignment', 'styling'],
        }

        self.medium_indicators = {
            # Dashboard and visualization (ADDED)
            'dashboard': ['dashboard', 'analytics', 'visualization', 'chart', 'metrics'],
            'single_feature': ['single', 'one', 'add endpoint', 'new api'],

            # Multiple files but not full stack (ADDED)
            'moderate_scope': ['multiple files', 'few components', 'several modules'],
        }

        self.complex_indicators = {
            # Architecture indicators
            'backend': ['microservice', 'service mesh', 'multi-service'],
            'database': ['database design', 'multiple databases', 'data migration'],
            'services': ['multiple services', 'service integration', 'distributed system'],

            # Scale indicators
            'high_scale': ['production scale', 'load balancing', 'high availability', 'fault tolerance'],
            'security': ['security audit', 'encryption', 'compliance', 'gdpr', 'hipaa', 'penetration test'],

            # Real complexity indicators (ADDED)
            'platform': ['platform', 'infrastructure', 'deployment pipeline', 'ci/cd'],
            'multiple_systems': ['e-commerce', 'payment processing', 'real-time chat', 'websocket'],
        }

    def detect(self, requirements: Dict, card: Dict) -> TaskComplexity:
        """
        Detect task complexity from requirements and card details.

        Args:
            requirements: Parsed requirements dict
            card: Task card with title, description, etc.

        Returns:
            TaskComplexity level (SIMPLE, MEDIUM, COMPLEX)
        """
        logger.log("🔍 Detecting task complexity...", "INFO")

        # Extract text to analyze
        text_to_analyze = self._extract_analyzable_text(requirements, card)
        text_lower = text_to_analyze.lower()

        # Count indicators
        simple_score = self._count_indicators(text_lower, self.simple_indicators)
        medium_score = self._count_indicators(text_lower, self.medium_indicators)
        complex_score = self._count_indicators(text_lower, self.complex_indicators)

        # Check functional requirements (handle both dict and dataclass)
        if hasattr(requirements, 'functional'):
            # Dataclass format
            func_reqs = requirements.functional
        elif isinstance(requirements, dict):
            # Dict format
            func_reqs = requirements.get('functional', [])
        else:
            func_reqs = []

        num_requirements = len(func_reqs)

        # Classify based on scores
        complexity = self._classify_complexity(
            simple_score,
            medium_score,
            complex_score,
            num_requirements
        )

        logger.log(f"✅ Task complexity: {complexity.value}", "INFO")
        logger.log(f"   Simple indicators: {simple_score}", "INFO")
        logger.log(f"   Medium indicators: {medium_score}", "INFO")
        logger.log(f"   Complex indicators: {complex_score}", "INFO")
        logger.log(f"   Requirements count: {num_requirements}", "INFO")

        return complexity

    def _extract_analyzable_text(self, requirements: Dict, card: Dict) -> str:
        """Extract all text that should be analyzed for complexity."""
        parts = [
            card.get('title', ''),
            card.get('description', ''),
        ]

        # Add requirement descriptions using comprehensions
        # Handle both dict and dataclass formats
        def extract_description(req):
            """Extract description from requirement (dataclass or dict)."""
            return req.description if hasattr(req, 'description') else req.get('description', '') if isinstance(req, dict) else ''

        if hasattr(requirements, 'functional'):
            # Dataclass format
            parts.extend(extract_description(req) for req in requirements.functional)
        elif isinstance(requirements, dict):
            # Dict format
            parts.extend(req.get('description', '') for req in requirements.get('functional', []) if isinstance(req, dict))

        if hasattr(requirements, 'non_functional'):
            # Dataclass format
            parts.extend(extract_description(req) for req in requirements.non_functional)
        elif isinstance(requirements, dict):
            # Dict format
            parts.extend(req.get('description', '') for req in requirements.get('non_functional', []) if isinstance(req, dict))

        return ' '.join(parts)

    def _count_indicators(self, text: str, indicator_dict: Dict[str, List[str]]) -> int:
        """Count how many indicators match in the text."""
        return sum(1 for indicators in indicator_dict.values() for indicator in indicators if indicator in text)

    def _classify_complexity(
        self,
        simple_score: int,
        medium_score: int,
        complex_score: int,
        num_requirements: int
    ) -> TaskComplexity:
        """
        Classify based on scores and requirements count.

        Enhanced Rules (with medium indicators):
        - If complex_score > 3 → COMPLEX
        - If num_requirements > 20 → COMPLEX
        - If simple_score > 4 and complex_score == 0 and medium_score == 0 → SIMPLE
        - If simple_score > medium_score and simple_score > complex_score → SIMPLE
        - If medium_score > 2 → MEDIUM
        - If num_requirements < 8 and complex_score < 2 and medium_score < 2 → SIMPLE
        - Otherwise → MEDIUM
        """
        # Guard: Strong complex signals
        if complex_score > 3 or num_requirements > 20:
            return TaskComplexity.COMPLEX

        # Guard: Strong simple signals (pure simple task)
        if simple_score > 4 and complex_score == 0 and medium_score == 0:
            return TaskComplexity.SIMPLE

        # Guard: Simple dominates
        if simple_score > medium_score and simple_score > complex_score and simple_score > 2:
            return TaskComplexity.SIMPLE

        # Guard: Medium indicators present
        if medium_score > 2:
            return TaskComplexity.MEDIUM

        # Guard: Few requirements and low complexity
        if num_requirements < 8 and complex_score < 2 and medium_score < 2:
            return TaskComplexity.SIMPLE

        # Default to medium for unclear cases
        return TaskComplexity.MEDIUM


class AdaptivePipelineBuilder:
    """
    Build optimal pipeline based on task complexity.

    WHY: Stop wasting 114 minutes on tasks that need 10 minutes.
    """

    def __init__(self):
        """Initialize builder with pipeline templates."""
        self.detector = TaskComplexityDetector()

    def build_pipeline(
        self,
        requirements: Dict,
        card: Dict,
        force_path: Optional[PipelinePath] = None
    ) -> Dict:
        """
        Build appropriate pipeline for the task.

        Args:
            requirements: Parsed requirements
            card: Task card
            force_path: Optional forced path (for testing)

        Returns:
            Pipeline configuration dict with stages and settings
        """
        # Detect complexity
        complexity = self.detector.detect(requirements, card)

        # Determine pipeline path
        if force_path:
            path = force_path
            logger.log(f"⚙️  Forced pipeline path: {path.value}", "INFO")
        else:
            path = self._complexity_to_path(complexity)
            logger.log(f"🎯 Selected pipeline path: {path.value}", "INFO")

        # Build pipeline based on path
        if path == PipelinePath.FAST:
            return self._build_fast_pipeline(requirements, card, complexity)
        elif path == PipelinePath.MEDIUM:
            return self._build_medium_pipeline(requirements, card, complexity)
        else:
            return self._build_full_pipeline(requirements, card, complexity)

    def _complexity_to_path(self, complexity: TaskComplexity) -> PipelinePath:
        """Map complexity to pipeline path."""
        mapping = {
            TaskComplexity.SIMPLE: PipelinePath.FAST,
            TaskComplexity.MEDIUM: PipelinePath.MEDIUM,
            TaskComplexity.COMPLEX: PipelinePath.FULL,
        }
        return mapping[complexity]

    def _build_fast_pipeline(
        self,
        requirements: Dict,
        card: Dict,
        complexity: TaskComplexity
    ) -> Dict:
        """
        Build fast pipeline for simple tasks.

        Fast Path (5-10 minutes):
        1. Requirements Parsing (already done)
        2. Research (quick code examples lookup - 2 min)
        3. Development (single developer - 3 min)
        4. Basic Validation (syntax/structure check - 1 min)

        Total: ~6 minutes
        """
        logger.log("🚀 Building FAST pipeline (5-10 minutes)", "INFO")

        return {
            'path': 'fast',
            'complexity': complexity.value,
            'estimated_duration_minutes': 8,
            'parallel_developers': 1,  # Single developer only
            'skip_sprint_planning': True,  # No planning poker
            'skip_project_analysis': True,  # No deep analysis
            'skip_arbitration': True,  # No competing solutions
            'skip_code_review': True,  # Basic validation instead
            'skip_uiux_eval': True,  # Not needed for simple tasks
            'stages': [
                'research',           # Quick code examples (2 min)
                'development',        # Single developer (3-5 min)
                'validation',         # Basic checks (1 min)
            ],
            'validation_level': 'basic',  # Syntax and structure only
            'reasoning': 'Simple task detected: minimal pipeline for speed'
        }

    def _build_medium_pipeline(
        self,
        requirements: Dict,
        card: Dict,
        complexity: TaskComplexity
    ) -> Dict:
        """
        Build medium pipeline for moderate tasks.

        Medium Path (30-40 minutes):
        1. Requirements Parsing (done)
        2. Project Review (quick analysis - 5 min)
        3. Research (code examples - 5 min)
        4. Development (single developer - 15 min)
        5. Code Review (automated checks - 5 min)
        6. Validation (thorough - 5 min)

        Total: ~35 minutes
        """
        logger.log("⚡ Building MEDIUM pipeline (30-40 minutes)", "INFO")

        return {
            'path': 'medium',
            'complexity': complexity.value,
            'estimated_duration_minutes': 35,
            'parallel_developers': 1,  # Single developer
            'skip_sprint_planning': True,  # Skip planning poker
            'skip_arbitration': True,  # Single developer = no arbitration
            'skip_uiux_eval': False,  # Include if UI components
            'stages': [
                'project_review',     # Quick analysis (5 min)
                'research',           # Code examples (5 min)
                'development',        # Development (15 min)
                'code_review',        # Automated review (5 min)
                'validation',         # Thorough validation (5 min)
            ],
            'validation_level': 'thorough',
            'reasoning': 'Medium complexity: balanced pipeline with core stages'
        }

    def _build_full_pipeline(
        self,
        requirements: Dict,
        card: Dict,
        complexity: TaskComplexity
    ) -> Dict:
        """
        Build full pipeline for complex tasks.

        Full Path (60-120 minutes):
        - All stages
        - Parallel developers
        - Arbitration
        - Complete validation

        Total: ~90 minutes
        """
        logger.log("🏗️  Building FULL pipeline (60-120 minutes)", "INFO")

        return {
            'path': 'full',
            'complexity': complexity.value,
            'estimated_duration_minutes': 90,
            'parallel_developers': 2,  # Parallel development
            'skip_sprint_planning': False,
            'skip_project_analysis': False,
            'skip_arbitration': False,
            'stages': [
                'sprint_planning',
                'project_analysis',
                'project_review',
                'research',
                'dependency_validation',
                'development',
                'arbitration',
                'code_review',
                'uiux',
                'validation',
                'integration',
                'testing',
            ],
            'validation_level': 'comprehensive',
            'reasoning': 'Complex task: full enterprise pipeline for quality assurance'
        }


def detect_and_recommend_pipeline(requirements: Dict, card: Dict) -> Dict:
    """
    Convenience function to detect complexity and recommend pipeline.

    Usage:
        pipeline_config = detect_and_recommend_pipeline(requirements, card)

        if pipeline_config['path'] == 'fast':
            # Run fast pipeline (5-10 min)
        elif pipeline_config['path'] == 'medium':
            # Run medium pipeline (30-40 min)
        else:
            # Run full pipeline (60-120 min)

    Returns:
        Pipeline configuration dict
    """
    builder = AdaptivePipelineBuilder()
    return builder.build_pipeline(requirements, card)


if __name__ == '__main__':
    # Example: Simple HTML task
    simple_card = {
        'title': 'Create HTML Presentation',
        'description': 'Single HTML file with CSS for demo presentation'
    }
    simple_reqs = {
        'functional': [
            {'description': 'Display hero section with title'},
            {'description': 'Add responsive CSS styling'},
            {'description': 'Include charts for data visualization'},
        ]
    }

    config = detect_and_recommend_pipeline(simple_reqs, simple_card)
    logger.log(f"\n✅ Recommended: {config['path'].upper()} path", "INFO")
    logger.log(f"   Duration: {config['estimated_duration_minutes']} minutes", "INFO")
    logger.log(f"   Stages: {len(config['stages'])}", "INFO")
    logger.log(f"   Reasoning: {config['reasoning']}", "INFO")
