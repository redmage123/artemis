"""
Module: agents/developer/developer.py

WHY: Main orchestrator for developer agent using composition pattern.
RESPONSIBILITY: Coordinate all developer workflows (TDD, quality-driven) using specialized components.
PATTERNS: Composition Pattern, Strategy Pattern, Facade Pattern.

This module:
- Composes FileManager, RAGIntegration, LLMClientWrapper, TDDPhases, ReportGenerator
- Provides public execute() method for backward compatibility
- Orchestrates workflow selection (TDD vs quality-driven)
- Delegates to specialized components (no God object!)

REPLACES: standalone_developer_agent.py (2,792 lines → ~350 lines orchestration)
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from artemis_stage_interface import LoggerInterface
from debug_mixin import DebugMixin
from llm_client import create_llm_client
from artemis_exceptions import (
    LLMClientError,
    DeveloperExecutionError,
    create_wrapped_exception
)

# Import extracted modules
from agents.developer.file_manager import FileManager
from agents.developer.test_runner_wrapper import DeveloperTestRunner
from agents.developer.report_generator import ReportGenerator
from agents.developer.rag_integration import RAGIntegration
from agents.developer.llm_client_wrapper import LLMClientWrapper
from agents.developer.tdd_phases import TDDPhases
from agents.developer.models import WorkflowType, WorkflowContext

# Import optional dependencies
try:
    from prompt_manager import PromptManager
    PROMPT_MANAGER_AVAILABLE = True
except ImportError:
    PROMPT_MANAGER_AVAILABLE = False

try:
    from ai_query_service import create_ai_query_service
    AI_QUERY_SERVICE_AVAILABLE = True
except ImportError:
    AI_QUERY_SERVICE_AVAILABLE = False

try:
    from retry_coordinator import RetryCoordinator
    RETRY_COORDINATOR_AVAILABLE = True
except ImportError:
    RETRY_COORDINATOR_AVAILABLE = False


class Developer(DebugMixin):
    """
    Modular developer agent using composition pattern

    WHY: Replaces monolithic StandaloneDeveloperAgent with clean component composition
    PATTERNS: Composition, Strategy, Facade
    """

    def __init__(
        self,
        developer_name: str,
        developer_type: str,
        llm_provider: str = "openai",
        llm_model: Optional[str] = None,
        logger: Optional[LoggerInterface] = None,
        rag_agent=None,
        ai_service: Optional['AIQueryService'] = None
    ):
        """
        Initialize developer with composed components

        Args:
            developer_name: "developer-a" or "developer-b"
            developer_type: "conservative" or "aggressive"
            llm_provider: "openai" or "anthropic"
            llm_model: Specific model (optional, uses default)
            logger: Logger implementation
            rag_agent: RAG agent for prompt retrieval (optional)
            ai_service: AI Query Service for KG-First queries (optional)
        """
        DebugMixin.__init__(self, component_name="developer")

        # Store developer identity
        self.developer_name = developer_name
        self.developer_type = developer_type
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.logger = logger

        self.debug_log("Developer initialized",
                      name=developer_name, type=developer_type, provider=llm_provider)

        # Create LLM client
        self.llm_client = self._create_llm_client()

        # Initialize optional dependencies
        self.prompt_manager = self._initialize_prompt_manager(rag_agent)
        self.ai_service = self._initialize_ai_service(ai_service, rag_agent)
        self.retry_coordinator = self._initialize_retry_coordinator()

        # Compose specialized components
        self.file_manager = FileManager(logger=logger)
        self.test_runner = DeveloperTestRunner(logger=logger)
        self.report_generator = ReportGenerator(
            developer_name=developer_name,
            developer_type=developer_type,
            llm_provider=llm_provider
        )
        self.rag_integration = RAGIntegration(
            developer_name=developer_name,
            developer_type=developer_type,
            logger=logger,
            prompt_manager=self.prompt_manager
        )
        self.llm_wrapper = LLMClientWrapper(
            llm_client=self.llm_client,
            developer_name=developer_name,
            developer_type=developer_type,
            llm_provider=llm_provider,
            llm_model=llm_model,
            logger=logger
        )
        self.tdd_phases = TDDPhases(
            file_manager=self.file_manager,
            test_runner=self.test_runner,
            llm_wrapper=self.llm_wrapper,
            logger=logger,
            retry_coordinator=self.retry_coordinator
        )

        self._log_info(f"✅ {developer_name} initialized with {llm_provider}")

    def execute(
        self,
        task_title: str,
        task_description: str,
        adr_content: str,
        adr_file: str,
        output_dir: Path,
        developer_prompt_file: str,
        card_id: str = "",
        rag_agent = None,
        parsed_requirements: Optional[Dict] = None
    ) -> Dict:
        """
        Execute task using REQUIREMENTS-DRIVEN workflow selection

        Workflow options:
        - TDD: For code (tests first, minimal implementation)
        - QUALITY_DRIVEN: For notebooks/demos (comprehensive output, rich validation)

        Args:
            task_title: Title of task
            task_description: Task description
            adr_content: ADR content
            adr_file: Path to ADR file
            output_dir: Output directory for implementation
            developer_prompt_file: Path to developer prompt file
            card_id: Card ID for querying RAG feedback (optional)
            rag_agent: RAG Agent for querying feedback (optional)
            parsed_requirements: Parsed requirements (optional)

        Returns:
            Dict with implementation results
        """
        self.debug_trace("execute", task_title=task_title, developer=self.developer_name, card_id=card_id)

        # Setup execution context
        context = self._setup_execution_context(
            task_title, task_description, adr_content, output_dir,
            developer_prompt_file, card_id, rag_agent
        )

        # Requirements-driven workflow selection
        strategy = self._select_workflow_strategy(task_title, task_description, parsed_requirements)

        self._log_info(f"📋 {self.developer_name} using {strategy.workflow.value.upper()} workflow")

        try:
            # Execute appropriate workflow
            results = self._execute_workflow(
                strategy, task_title, task_description, adr_content, output_dir, context
            )

            # Generate and save solution report
            solution_report = self.report_generator.finalize_solution_report(results, output_dir)

            self.debug_dump_if_enabled("solution", "Solution Report", {
                "workflow": strategy.workflow.value,
                "num_files": len(results.get('implementation_files', results.get('green', {}).get('implementation_files', [])))
            })

            return solution_report

        except Exception as e:
            self._log_error(f"❌ {self.developer_name} workflow failed: {e}")
            raise create_wrapped_exception(
                e,
                DeveloperExecutionError,
                f"Developer {self.developer_name} workflow failed",
                {
                    "developer_name": self.developer_name,
                    "developer_type": self.developer_type,
                    "task_title": task_title,
                    "card_id": card_id
                }
            )

    # ========== Workflow Orchestration ==========

    def _execute_workflow(self, strategy, task_title, task_description, adr_content, output_dir, context):
        """Execute workflow based on strategy - Strategy Pattern"""
        if strategy.workflow == WorkflowType.TDD:
            return self._execute_tdd_workflow(
                task_title, task_description, adr_content, output_dir, context
            )

        return self._execute_quality_driven_workflow(
            task_title, task_description, adr_content, output_dir, context
        )

    def _execute_tdd_workflow(self, task_title, task_description, adr_content, output_dir, context):
        """
        Execute TDD workflow: RED → GREEN → REFACTOR

        Delegates to TDDPhases orchestrator
        """
        # RED Phase: Generate failing tests
        red_results = self.tdd_phases.execute_red_phase(
            task_title, task_description, adr_content, output_dir, context
        )

        # GREEN Phase: Implement code to pass tests
        green_results = self.tdd_phases.execute_green_phase(
            task_title, task_description, adr_content, output_dir, context, red_results
        )

        # REFACTOR Phase: Improve code quality
        refactor_results = self.tdd_phases.execute_refactor_phase(
            task_title, output_dir, context, green_results
        )

        return {
            'red': {
                'test_files': red_results.files,
                'test_results': red_results.test_results
            },
            'green': {
                'implementation_files': green_results.files,
                'test_results': green_results.test_results
            },
            'refactor': {
                'refactored_files': refactor_results.files,
                'test_results': refactor_results.test_results
            }
        }

    def _execute_quality_driven_workflow(self, task_title, task_description, adr_content, output_dir, context):
        """
        Execute quality-driven workflow: Direct implementation with validation

        For notebooks, demos, presentations - prioritize comprehensive output
        """
        self._log_info("🎯 QUALITY-DRIVEN workflow: Generating comprehensive implementation...")

        # Query RAG for examples
        rag_examples = self.rag_integration.query_rag_for_examples(
            self.rag, task_title, task_description
        ) if hasattr(self, 'rag') else ""

        # Build quality-driven prompt
        prompt = self._build_quality_prompt(
            task_title, task_description, adr_content, context, rag_examples
        )

        # Generate implementation using LLM
        response = self.llm_wrapper.call_llm(prompt)
        implementation = self.llm_wrapper.parse_implementation(response.content)

        # Write files
        files_written = self.file_manager.write_implementation_files(implementation, output_dir)

        self._log_info(f"✅ Quality-driven workflow complete: {len(files_written)} files written")

        return {
            'implementation_files': implementation.get('implementation_files', []),
            'test_files': implementation.get('test_files', [])
        }

    # ========== Context Setup ==========

    def _setup_execution_context(self, task_title, task_description, adr_content,
                                  output_dir, developer_prompt_file, card_id, rag_agent):
        """
        Setup execution context by gathering all necessary data

        Returns:
            Dict containing all context data
        """
        self._log_info(f"🚀 {self.developer_name} starting workflow...")

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Query KG for similar implementations (if AI service available)
        kg_context = self._query_kg_context(task_title, task_description)

        # Query RAG for code review feedback
        code_review_feedback = None
        if rag_agent and card_id:
            code_review_feedback = self.rag_integration.query_code_review_feedback(rag_agent, card_id)

        # Get developer prompt (from RAG if available, else file-based)
        developer_prompt = self._get_developer_prompt(
            task_title, adr_content, code_review_feedback, rag_agent, developer_prompt_file
        )

        # Load example slides if task involves HTML/slides
        example_slides = None
        if "slide" in task_description.lower() or "html" in task_description.lower():
            example_slides = self.file_manager.load_example_slides(adr_content)

        # Query RAG for refactoring instructions
        refactoring_instructions = None
        if rag_agent:
            language = self._detect_language_from_task(task_description)
            refactoring_instructions = self.rag_integration.query_refactoring_instructions(
                rag_agent, task_title, language
            )

        return {
            'kg_context': kg_context,
            'code_review_feedback': code_review_feedback,
            'developer_prompt': developer_prompt,
            'example_slides': example_slides,
            'refactoring_instructions': refactoring_instructions
        }

    def _select_workflow_strategy(self, task_title, task_description, parsed_requirements):
        """
        Select workflow strategy based on requirements

        Uses RequirementsDrivenValidator if available, else task type detection
        """
        try:
            from requirements_driven_validator import RequirementsDrivenValidator
            validator = RequirementsDrivenValidator(self.logger)
            return validator.analyze_requirements(task_title, task_description, parsed_requirements)
        except ImportError:
            # Fallback: simple strategy based on task type detection
            from agents.developer.models import WorkflowType, TaskType, ExecutionStrategy

            task_type = self._detect_task_type(task_title, task_description)

            # Simple mapping: notebook/presentation → quality-driven, code → TDD
            workflow = (WorkflowType.QUALITY_DRIVEN
                       if task_type in [TaskType.NOTEBOOK, TaskType.PRESENTATION, TaskType.HTML]
                       else WorkflowType.TDD)

            # Create simple strategy object
            class SimpleStrategy:
                def __init__(self, workflow, artifact_type):
                    self.workflow = workflow
                    self.artifact_type = artifact_type

            return SimpleStrategy(workflow, task_type)

    def _detect_task_type(self, task_title, task_description):
        """Detect task type from title and description"""
        from agents.developer.models import TaskType

        combined = f"{task_title} {task_description}".lower()

        # Guard: notebook
        if any(kw in combined for kw in ['jupyter', 'notebook', 'ipynb']):
            return TaskType.NOTEBOOK

        # Guard: presentation
        if any(kw in combined for kw in ['slide', 'presentation', 'demo']):
            return TaskType.PRESENTATION

        # Guard: HTML
        if any(kw in combined for kw in ['html', 'webpage']):
            return TaskType.HTML

        # Default: code
        return TaskType.CODE

    def _detect_language_from_task(self, task_description: str) -> str:
        """
        Detect programming language from task description

        Args:
            task_description: Task description text

        Returns:
            Detected language string (python, java, javascript, go, rust)
            Defaults to "python" if not detected
        """
        # Normalize to lowercase for case-insensitive matching
        description_lower = task_description.lower()

        # Language detection keywords with priority order
        language_keywords = {
            'java': ['java', 'spring', 'maven', 'gradle', 'springboot', 'spring boot'],
            'javascript': ['javascript', 'typescript', 'node', 'react', 'nodejs', 'node.js',
                          'angular', 'vue', 'npm', 'yarn', 'jest', 'webpack'],
            'go': ['golang', 'go '],  # 'go ' with space to avoid matching 'django', etc.
            'rust': ['rust', 'cargo'],
            'python': ['python', 'django', 'flask', 'fastapi', 'pytest', 'pip']
        }

        # Check for language keywords
        for language, keywords in language_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return language

        # Default to python if no language detected
        return "python"

    # ========== Helper Methods (Delegation) ==========

    def _query_kg_context(self, task_title, task_description):
        """Query KG for similar implementations"""
        # Guard: no AI service
        if not self.ai_service:
            return None

        try:
            from ai_query_service import QueryType
            result = self.ai_service.query(
                query_type=QueryType.SIMILAR_IMPLEMENTATIONS,
                query_text=f"{task_title}: {task_description}",
                context={"task_title": task_title}
            )
            return result.data if result.success else None
        except Exception as e:
            self._log_warning(f"KG query failed: {e}")
            return None

    def _get_developer_prompt(self, task_title, adr_content, code_review_feedback, rag_agent, prompt_file):
        """Get developer prompt (RAG or file-based)"""
        # Try RAG first
        if self.prompt_manager and rag_agent:
            return self.rag_integration.get_developer_prompt_from_rag(
                task_title, adr_content, code_review_feedback, rag_agent
            )

        # Fallback: read from file
        return self.file_manager.read_developer_prompt(prompt_file)

    def _build_quality_prompt(self, task_title, task_description, adr_content, context, rag_examples):
        """Build prompt for quality-driven workflow"""
        # Simple prompt builder (can be enhanced with PromptManager)
        return f"""
Task: {task_title}
Description: {task_description}

Architecture Decision:
{adr_content}

{context.get('developer_prompt', '')}

{rag_examples}

Generate a comprehensive, high-quality implementation following all guidelines.
"""

    # ========== Initialization Helpers ==========

    def _create_llm_client(self):
        """Create LLM client with error handling"""
        try:
            llm_client = create_llm_client(self.llm_provider)
            return llm_client
        except Exception as e:
            self._log_error(f"❌ Failed to initialize LLM client: {e}")
            raise create_wrapped_exception(
                e,
                LLMClientError,
                f"Failed to initialize LLM client for {self.developer_name}",
                {"developer_name": self.developer_name, "llm_provider": self.llm_provider}
            )

    def _initialize_prompt_manager(self, rag_agent):
        """Initialize PromptManager with early returns"""
        # Guard: not available
        if not PROMPT_MANAGER_AVAILABLE:
            return None

        # Guard: no RAG agent
        if not rag_agent:
            return None

        try:
            manager = PromptManager(rag_agent, verbose=False)
            self._log_info("✅ Prompt manager initialized (RAG-based prompts)")
            return manager
        except Exception as e:
            self._log_warning(f"⚠️  Could not initialize prompt manager: {e}")
            return None

    def _initialize_ai_service(self, ai_service, rag_agent):
        """Initialize AI Query Service with early returns"""
        # Guard: not available
        if not AI_QUERY_SERVICE_AVAILABLE:
            return None

        # Guard: already provided
        if ai_service:
            self._log_info("✅ Using provided AI Query Service")
            return ai_service

        try:
            service = create_ai_query_service(
                llm_client=self.llm_client,
                rag=rag_agent,
                logger=self.logger,
                verbose=False
            )
            self._log_info("✅ AI Query Service initialized (KG-First enabled)")
            return service
        except Exception as e:
            self._log_warning(f"⚠️  Could not initialize AI Query Service: {e}")
            return None

    def _initialize_retry_coordinator(self):
        """Initialize Retry Coordinator with early returns"""
        # Guard: not available
        if not RETRY_COORDINATOR_AVAILABLE:
            return None

        try:
            max_retries = int(os.getenv("ARTEMIS_MAX_VALIDATION_RETRIES", "3"))
            acceptance_threshold = float(os.getenv("ARTEMIS_CONFIDENCE_THRESHOLD", "0.85"))

            coordinator = RetryCoordinator(
                logger=self.logger,
                max_retries=max_retries,
                acceptance_threshold=acceptance_threshold
            )
            self._log_info(f"✅ Retry Coordinator initialized (max={max_retries}, threshold={acceptance_threshold:.2f})")
            return coordinator
        except Exception as e:
            self._log_warning(f"⚠️  Could not initialize Retry Coordinator: {e}")
            return None

    # ========== Logging Helpers ==========

    def _log_info(self, message: str):
        """Log info message"""
        if self.logger:
            self.logger.log(message, "INFO")

    def _log_warning(self, message: str):
        """Log warning message"""
        if self.logger:
            self.logger.log(message, "WARNING")

    def _log_error(self, message: str):
        """Log error message"""
        if self.logger:
            self.logger.log(message, "ERROR")


__all__ = [
    "Developer"
]
