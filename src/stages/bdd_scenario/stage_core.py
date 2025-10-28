#!/usr/bin/env python3
"""
Module: stages/bdd_scenario/stage_core.py

WHY: Orchestrates BDD scenario generation by coordinating retrieval,
     generation, validation, formatting, and storage components.

RESPONSIBILITY: Implement PipelineStage interface for BDD scenario generation.
                Coordinates all BDD components (retriever, generator, validator,
                formatter, storage) to produce valid Gherkin scenarios.

PATTERNS:
- Template Method Pattern: Implements PipelineStage execution contract
- Facade Pattern: Provides simple interface to complex subsystem
- Supervised Execution Pattern: Health monitoring via SupervisorAgent

Integration:
- Implements PipelineStage interface for pipeline execution
- Integrates with SupervisedStageMixin for health monitoring
- Stores artifacts in RAG for developer query
- Writes feature files to developer workspace
"""

from typing import Dict, Optional, Any
from pathlib import Path

from artemis_stage_interface import PipelineStage, LoggerInterface
from supervised_agent_mixin import SupervisedStageMixin
from kanban_manager import KanbanBoard
from rag_agent import RAGAgent
from llm_client import LLMClient
from artemis_exceptions import PipelineStageError

from .scenario_generator import ScenarioGenerator, RequirementsRetriever, ScenarioValidator
from .feature_extractor import FeatureExtractor, FeatureFileStorage


class BDDScenarioStageCore(PipelineStage, SupervisedStageMixin):
    """
    Core orchestrator for BDD scenario generation.

    WHY: Facade Pattern - provides simple interface to complex BDD
         generation subsystem. Coordinates multiple components
         (retrieval, generation, validation, storage) into single
         coherent stage execution.

    Responsibilities:
    - Retrieve requirements (context or RAG)
    - Extract feature data from requirements
    - Generate Gherkin scenarios via LLM
    - Validate scenario syntax
    - Store feature files in developer workspace
    - Store scenarios in RAG
    - Track progress via supervised execution

    Design: Template Method - implements PipelineStage execute() contract
            with consistent execution flow for all scenarios.
    """

    def __init__(
        self,
        board: KanbanBoard,
        rag: RAGAgent,
        logger: LoggerInterface,
        llm_client: LLMClient,
        observable: Optional[Any] = None,
        supervisor: Optional[Any] = None,
        ai_service: Optional[Any] = None
    ):
        """
        Initialize BDD scenario generation stage.

        WHY: Dependency Inversion - injects all dependencies rather than
             creating them internally. Enables testability and loose coupling.

        Args:
            board: Kanban board for task tracking
            rag: RAG agent for storing and retrieving artifacts
            logger: Logger interface for consistent logging
            llm_client: LLM client for scenario generation
            observable: Pipeline observable for event notifications
            supervisor: Supervisor agent for health monitoring
            ai_service: AI query service for optimized LLM routing
        """
        PipelineStage.__init__(self)
        SupervisedStageMixin.__init__(
            self,
            supervisor=supervisor,
            stage_name="BDDScenarioGenerationStage",
            heartbeat_interval=20  # LLM calls can be slow
        )

        self.board = board
        self.rag = rag
        self.logger = logger
        self.llm_client = llm_client
        self.observable = observable
        self.supervisor = supervisor
        self.ai_service = ai_service

        # Initialize components
        self._init_components()

    def _init_components(self) -> None:
        """
        Initialize BDD generation components.

        WHY: Single Responsibility - separates component initialization
             from main initialization logic. Makes dependencies explicit.
        """
        self.requirements_retriever = RequirementsRetriever(
            rag=self.rag,
            logger=self.logger
        )

        self.scenario_generator = ScenarioGenerator(
            llm_client=self.llm_client,
            logger=self.logger,
            ai_service=self.ai_service
        )

        self.scenario_validator = ScenarioValidator()

        self.feature_extractor = FeatureExtractor()

        self.feature_storage = FeatureFileStorage(logger=self.logger)

    def execute(self, card: Dict, context: Dict) -> Dict:
        """
        Execute BDD scenario generation with supervisor monitoring.

        WHY: Template Method Pattern - implements PipelineStage contract.
             Supervised execution enables health monitoring, hang detection,
             and progress tracking.

        Args:
            card: Kanban card with task details
            context: Pipeline context from previous stages

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

        WHY: Separates supervised execution wrapper from actual work.
             Allows monitoring logic to remain clean and focused.

        Args:
            card: Kanban card with task details
            context: Pipeline context

        Returns:
            Dict with scenario generation results

        Execution flow:
        1. Extract card information (10%)
        2. Retrieve requirements (20%)
        3. Extract feature data (30%)
        4. Generate scenarios via LLM (60%)
        5. Validate syntax (80%)
        6. Store feature file and RAG artifact (90%)
        7. Return results (100%)
        """
        self.logger.log("🥒 Starting BDD Scenario Generation Stage", "STAGE")

        # Extract card information
        card_id = card.get('card_id', 'unknown')
        title = card.get('title', 'Unknown Task')

        self.update_progress({"step": "starting", "progress_percent": 10})

        # Retrieve requirements from context or RAG
        self.update_progress({"step": "retrieving_requirements", "progress_percent": 20})
        requirements = self.requirements_retriever.retrieve(context, card_id, title)

        # Extract feature data
        self.update_progress({"step": "extracting_feature", "progress_percent": 30})
        feature_data = self.feature_extractor.extract(title, requirements)

        self.logger.log(f"📋 Generating BDD scenarios for: {title}", "INFO")

        # Generate Gherkin scenarios using LLM
        self.update_progress({"step": "generating_scenarios", "progress_percent": 40})
        scenarios_content = self.scenario_generator.generate(
            card_id=card_id,
            title=title,
            requirements=requirements
        )

        # Validate scenario structure
        self.update_progress({"step": "validating_scenarios", "progress_percent": 80})
        validation_result = self.scenario_validator.validate(scenarios_content)

        if not validation_result['valid']:
            self.logger.log(
                f"⚠️  Scenario validation issues: {validation_result['errors']}",
                "WARNING"
            )

        # Store feature file and RAG artifact
        self.update_progress({"step": "storing_scenarios", "progress_percent": 90})
        feature_path = self._store_artifacts(
            card_id=card_id,
            title=title,
            content=scenarios_content,
            validation_result=validation_result,
            context=context
        )

        self.update_progress({"step": "complete", "progress_percent": 100})

        scenario_count = scenarios_content.count("Scenario:")
        self.logger.log(f"✅ Generated {scenario_count} BDD scenarios", "SUCCESS")

        return {
            "stage": "bdd_scenario_generation",
            "feature_path": str(feature_path),
            "scenarios_content": scenarios_content,
            "scenario_count": scenario_count,
            "validation": validation_result
        }

    def _store_artifacts(
        self,
        card_id: str,
        title: str,
        content: str,
        validation_result: Dict[str, Any],
        context: Dict
    ) -> str:
        """
        Store feature file and RAG artifact.

        WHY: Guard clauses prevent nested conditionals and make
             storage logic explicit.

        Args:
            card_id: Card identifier
            title: Feature title
            content: Gherkin content
            validation_result: Validation results
            context: Pipeline context

        Returns:
            Path to stored feature file
        """
        # Determine developer from context
        winner = context.get('winner', 'developer-a')

        # Store feature file in developer workspace
        feature_path = self.feature_storage.store(
            developer=winner,
            title=title,
            content=content
        )

        # Store in RAG for developer query
        self.rag.store_artifact(
            artifact_type="bdd_scenarios",
            card_id=card_id,
            task_title=title,
            content=content,
            metadata={
                "feature_path": feature_path,
                "scenario_count": content.count("Scenario:"),
                "validation_status": "valid" if validation_result['valid'] else "has_issues"
            }
        )

        return feature_path

    def get_stage_name(self) -> str:
        """
        Return stage name identifier.

        WHY: PipelineStage interface requirement. Used by orchestrator
             for tracking, logging, and dependency resolution.

        Returns:
            "bdd_scenario_generation"
        """
        return "bdd_scenario_generation"
