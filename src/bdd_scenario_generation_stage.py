#!/usr/bin/env python3
"""
Module: bdd_scenario_generation_stage.py

Purpose: Transform structured requirements into executable Gherkin BDD scenarios
         using LLM-powered generation.

Why: Bridges the gap between business requirements and executable specifications.
     BDD scenarios serve as both documentation and automated test specifications,
     ensuring implementation matches business intent.

Patterns:
- Template Method Pattern: Implements PipelineStage execution contract
- Strategy Pattern: AI Query Service fallback to direct LLM calls
- Supervised Execution Pattern: Health monitoring via SupervisorAgent
- Observer Pattern: Integrates with PipelineObservable for stage events

Integration:
- Runs after SprintPlanningStage (requirements are available)
- Provides Gherkin scenarios to DevelopmentStage for reference
- Feeds into BDD Test Generation Stage (converts scenarios to pytest-bdd)
- Stores scenarios in RAG for developer query
- Stores feature files in developer workspace

SOLID Principles:
- S: Single Responsibility - Only generates BDD scenarios
- O: Open/Closed - Extensible to new Gherkin formats without modification
- L: Liskov Substitution - Implements PipelineStage contract
- I: Interface Segregation - Focused on scenario generation
- D: Dependency Inversion - Depends on abstractions (LLMClient, RAGAgent)
"""

from typing import Dict, Optional
from pathlib import Path

from artemis_stage_interface import PipelineStage, LoggerInterface
from supervised_agent_mixin import SupervisedStageMixin
from kanban_manager import KanbanBoard
from rag_agent import RAGAgent
from llm_client import LLMClient
from artemis_exceptions import PipelineStageError, wrap_exception


class BDDScenarioGenerationStage(PipelineStage, SupervisedStageMixin):
    """
    Generate BDD scenarios in Gherkin format from requirements.

    What it does: Uses LLM to convert structured requirements into business-readable
                  Gherkin scenarios (Given/When/Then format) and validates syntax.

    Why it exists: BDD scenarios serve dual purpose as executable specifications AND
                   documentation. They ensure developers build what the business needs
                   while providing automated test specifications.

    Responsibilities:
    - Retrieve requirements from context or RAG
    - Generate Gherkin scenarios using LLM (with AI Query Service optimization)
    - Validate Gherkin syntax (Feature, Scenario, Given/When/Then structure)
    - Store feature files in developer workspace
    - Store scenarios in RAG for developer reference
    - Track progress via supervised execution

    Design Pattern: Strategy Pattern - AI Query Service with fallback to direct LLM
    Why: Optimizes token usage and cost by routing through AI Query Service first,
         falling back to direct LLM calls if service unavailable.

    Integrates with supervisor for:
    - LLM call monitoring (tracks token usage and cost)
    - Scenario validation tracking (monitors syntax errors)
    - Feature file generation tracking (monitors I/O operations)
    - Heartbeat monitoring (20 second interval for LLM-heavy stage)
    """

    def __init__(
        self,
        board: KanbanBoard,
        rag: RAGAgent,
        logger: LoggerInterface,
        llm_client: LLMClient,
        observable: Optional['PipelineObservable'] = None,
        supervisor: Optional['SupervisorAgent'] = None,
        ai_service: Optional['AIQueryService'] = None
    ):
        """
        Initialize BDD Scenario Generation Stage.

        What it does: Sets up dependencies and configures supervised execution monitoring.

        Why: Dependency Inversion Principle - injects all dependencies rather than
             creating them internally, enabling testability and loose coupling.

        Args:
            board: Kanban board for task tracking
                   Why: May update card status during scenario generation
            rag: RAG agent for storing and retrieving artifacts
                 Why: Stores scenarios for developer query; retrieves requirements
            logger: Logger interface for consistent logging
                    Why: Interface Segregation - depends on minimal logging interface
            llm_client: LLM client for scenario generation
                        Why: Abstraction allows swapping OpenAI/Anthropic/local models
            observable: Pipeline observable for event notifications (optional)
                        Why: Observer Pattern - notifies orchestrator of stage events
            supervisor: Supervisor agent for health monitoring (optional)
                        Why: Monitors LLM calls, validates progress, detects hangs
            ai_service: AI query service for optimized LLM routing (optional)
                        Why: Reduces token usage and cost via intelligent routing

        Initializes:
        - SupervisedStageMixin with 20 second heartbeat (LLM calls can be slow)
        - PipelineStage base class for execution contract
        """
        PipelineStage.__init__(self)
        SupervisedStageMixin.__init__(
            self,
            supervisor=supervisor,
            stage_name="BDDScenarioGenerationStage",
            heartbeat_interval=20
        )

        self.board = board
        self.rag = rag
        self.logger = logger
        self.llm_client = llm_client
        self.observable = observable
        self.supervisor = supervisor
        self.ai_service = ai_service

    def execute(self, card: Dict, context: Dict) -> Dict:
        """
        Execute BDD scenario generation with supervisor monitoring.

        What it does: Wraps internal work with supervised execution context for health monitoring.

        Why: Supervised Execution Pattern - enables SupervisorAgent to monitor LLM calls,
             track progress, detect hangs, and measure token costs.

        Args:
            card: Kanban card with task details (card_id, title, requirements)
            context: Pipeline context from previous stages (may contain requirements)

        Returns:
            Dict with scenario generation results:
            - stage: "bdd_scenario_generation"
            - feature_path: Path to generated .feature file
            - scenarios_content: Gherkin scenario text
            - scenario_count: Number of scenarios generated
            - validation: Syntax validation results

        Raises:
            PipelineStageError: If scenario generation fails critically
        """
        metadata = {
            "task_id": card.get('card_id'),
            "stage": "bdd_scenario_generation"
        }

        # Supervised execution context monitors heartbeat and progress
        with self.supervised_execution(metadata):
            result = self._do_work(card, context)

        return result

    def _do_work(self, card: Dict, context: Dict) -> Dict:
        """
        Internal method - performs BDD scenario generation.

        What it does:
        1. Retrieves requirements from context or RAG
        2. Generates Gherkin scenarios using LLM
        3. Validates scenario syntax
        4. Stores feature files in developer workspace
        5. Stores scenarios in RAG

        Why separated from execute(): Allows supervised execution wrapper to monitor
        the actual work without adding complexity to monitoring logic.

        Args:
            card: Kanban card with task details
            context: Pipeline context (may contain requirements from previous stages)

        Returns:
            Dict with scenario generation results and paths

        Progress tracking:
        - 10%: Starting
        - 30%: Generating scenarios (LLM call)
        - 60%: Validating syntax
        - 80%: Storing files
        - 100%: Complete
        """
        self.logger.log("🥒 Starting BDD Scenario Generation Stage", "STAGE")

        card_id = card.get('card_id', 'unknown')
        title = card.get('title', 'Unknown Task')

        # Update progress
        self.update_progress({"step": "starting", "progress_percent": 10})

        # Get requirements from context or RAG
        requirements = context.get('requirements', {})
        if not requirements:
            # Try to fetch from RAG
            requirements_artifact = self.rag.query(
                query_text=f"requirements for {title}",
                filter_metadata={"card_id": card_id, "artifact_type": "requirements"}
            )
            if requirements_artifact:
                requirements = requirements_artifact[0].get('content', {})

        self.logger.log(f"📋 Generating BDD scenarios for: {title}", "INFO")

        # Update progress
        self.update_progress({"step": "generating_scenarios", "progress_percent": 30})

        # Generate Gherkin scenarios using LLM
        scenarios_content = self._generate_gherkin_scenarios(
            card_id=card_id,
            title=title,
            requirements=requirements
        )

        # Update progress
        self.update_progress({"step": "validating_scenarios", "progress_percent": 60})

        # Validate scenario structure
        validation_result = self._validate_gherkin_syntax(scenarios_content)

        if not validation_result['valid']:
            self.logger.log(f"⚠️  Scenario validation issues: {validation_result['errors']}", "WARNING")

        # Update progress
        self.update_progress({"step": "storing_scenarios", "progress_percent": 80})

        # Store feature files for each developer
        winner = context.get('winner', 'developer-a')
        feature_path = self._store_feature_file(winner, title, scenarios_content)

        # Store in RAG
        self.rag.store_artifact(
            artifact_type="bdd_scenarios",
            card_id=card_id,
            task_title=title,
            content=scenarios_content,
            metadata={
                "feature_path": str(feature_path),
                "scenario_count": scenarios_content.count("Scenario:"),
                "validation_status": "valid" if validation_result['valid'] else "has_issues"
            }
        )

        # Update progress
        self.update_progress({"step": "complete", "progress_percent": 100})

        self.logger.log(f"✅ Generated {scenarios_content.count('Scenario:')} BDD scenarios", "SUCCESS")

        return {
            "stage": "bdd_scenario_generation",
            "feature_path": str(feature_path),
            "scenarios_content": scenarios_content,
            "scenario_count": scenarios_content.count("Scenario:"),
            "validation": validation_result
        }

    def _generate_gherkin_scenarios(
        self,
        card_id: str,
        title: str,
        requirements: Dict
    ) -> str:
        """
        Generate Gherkin scenarios using LLM.

        What it does: Uses LLM to transform structured requirements into business-readable
                      Gherkin scenarios following Given/When/Then format.

        Why: LLM excels at converting technical requirements into natural language
             specifications that both business stakeholders and developers understand.

        Strategy Pattern Implementation:
        - Primary: AI Query Service (token-optimized routing)
        - Fallback: Direct LLM call (if service unavailable)

        Args:
            card_id: Card ID for context tracking
            title: Feature title for Gherkin Feature header
            requirements: Structured requirements dict

        Returns:
            Complete Gherkin .feature file content as string

        LLM Prompt Design:
        - Temperature: 0.3 (deterministic, consistent scenarios)
        - Max tokens: 2000 (sufficient for 5-10 comprehensive scenarios)
        - Prompt includes: Feature description, requirements, format guidelines
        - Instructs LLM to generate: happy path, edge cases, error handling
        """

        prompt = f"""You are a BDD expert. Generate comprehensive Gherkin scenarios for the following feature.

Feature: {title}

Requirements:
{requirements}

Generate a complete .feature file with:
1. Feature description (As a/I want/So that format)
2. Multiple scenarios covering:
   - Happy path (normal expected behavior)
   - Edge cases
   - Error handling
   - User interactions
3. Use Given/When/Then format
4. Make scenarios specific and testable
5. Include scenario outlines for data-driven tests where appropriate

Format the output as a valid Gherkin feature file."""

        # Use AI Query Service if available for token optimization
        if self.ai_service:
            result = self.ai_service.query(
                query=prompt,
                context={"card_id": card_id, "title": title},
                temperature=0.3,
                max_tokens=2000
            )
            if result.success:
                return result.response
            else:
                self.logger.log(f"AI Query Service failed: {result.error}, falling back to direct LLM", "WARNING")

        # Fallback to direct LLM call
        response = self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )

        return response

    def _validate_gherkin_syntax(self, content: str) -> Dict:
        """
        Validate Gherkin scenario structure.

        What it does: Checks that generated content follows valid Gherkin syntax.

        Why: LLM-generated content may have structural errors that would break
             pytest-bdd execution. Early validation catches these issues before
             developers attempt to run tests.

        Validation checks:
        1. Has Feature: declaration
        2. Has at least one Scenario: or Scenario Outline:
        3. Each scenario has Given/When steps (setup and action)
        4. Each scenario has Then steps (assertions)

        Args:
            content: Gherkin scenario text

        Returns:
            Dict with validation results:
            - valid: Boolean (True if all checks pass)
            - errors: List of error messages (empty if valid)

        Performance: O(n) single-pass parsing using string operations
        """
        errors = []

        # Check for required keywords
        if "Feature:" not in content:
            errors.append("Missing 'Feature:' declaration")

        if "Scenario:" not in content and "Scenario Outline:" not in content:
            errors.append("No scenarios defined")

        # Check scenario structure
        scenarios = content.split("Scenario:")
        for i, scenario in enumerate(scenarios[1:], 1):  # Skip feature description
            if "Given" not in scenario and "When" not in scenario:
                errors.append(f"Scenario {i} missing Given/When steps")
            if "Then" not in scenario:
                errors.append(f"Scenario {i} missing Then assertions")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def _store_feature_file(self, developer: str, title: str, content: str) -> Path:
        """
        Store feature file in developer's workspace directory.

        What it does: Writes Gherkin scenarios to .feature file in developer's
                      features/ directory.

        Why: Developers need feature files in their workspace to:
             1. Run pytest-bdd tests against scenarios
             2. Reference business requirements during development
             3. Update scenarios as requirements evolve

        Args:
            developer: Developer identifier (e.g., "developer-a")
            title: Feature title (sanitized for filename)
            content: Gherkin scenario content

        Returns:
            Path to created .feature file

        File naming: title.lower().replace(' ', '_') + '.feature'
        Why: Follows Python naming conventions; pytest-bdd auto-discovers *.feature files
        """
        feature_dir = Path(f"/tmp/{developer}/features")
        feature_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        filename = title.lower().replace(' ', '_').replace('/', '_')
        feature_path = feature_dir / f"{filename}.feature"

        with open(feature_path, 'w') as f:
            f.write(content)

        self.logger.log(f"📝 Stored feature file: {feature_path}", "INFO")

        return feature_path

    def get_stage_name(self) -> str:
        """
        Return stage name identifier.

        What it does: Returns unique stage identifier string.

        Why: PipelineStage interface requirement. Orchestrator uses this for:
             - Tracking stage execution order
             - Logging and monitoring
             - Context key namespacing
             - Stage dependency resolution

        Returns:
            "bdd_scenario_generation"
        """
        return "bdd_scenario_generation"
