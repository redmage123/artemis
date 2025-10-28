#!/usr/bin/env python3
"""
WHY: Invoke developer agents with validation, RAG integration, and parallel execution
RESPONSIBILITY: Coordinate developer invocation with validation pipeline and event notification
PATTERNS: Facade (simplified API), Strategy (execution modes), Template Method (invocation flow)

Developer invocation provides:
- Single developer invocation
- Multi-developer parallel/sequential execution
- Validation pipeline integration (Layer 3)
- RAG-enhanced validation (Layer 3.5)
- Event notification (Observer pattern)
- Requirements parsing for validation
"""

from typing import Dict, List, Optional
from pathlib import Path
import os

from artemis_stage_interface import LoggerInterface
from standalone_developer_agent import StandaloneDeveloperAgent
from validated_developer_mixin import create_validated_developer_agent
from artemis_constants import get_developer_prompt_path
from pipeline_observer import PipelineObservable
from path_config_service import get_path_config
from debug_mixin import DebugMixin
from requirements_parser_agent import RequirementsParserAgent
from developer_invoker.prompt_builder import DeveloperPromptBuilder
from developer_invoker.event_notifier import DeveloperEventNotifier
from developer_invoker.execution_strategy import ExecutionStrategyFactory


class DeveloperInvoker(DebugMixin):
    """
    Invoke Developer A and Developer B as autonomous agents

    Single Responsibility: Launch and coordinate developer agents
    - Invokes agents via validated developer creation
    - Passes ADR and task context to each developer
    - Waits for completion
    - Collects results
    - Emits pipeline events
    """

    def __init__(self, logger: LoggerInterface, observable: Optional[PipelineObservable] = None):
        """
        Initialize developer invoker

        Args:
            logger: Logger for progress tracking
            observable: Pipeline observable for event emission
        """
        DebugMixin.__init__(self, component_name="developer_invoker")
        self.logger = logger
        self.observable = observable

        # Get developer output base directory from path config service
        self.developer_base_dir = get_path_config().developer_output_dir

        # Initialize components
        self.prompt_builder = DeveloperPromptBuilder()
        self.event_notifier = DeveloperEventNotifier(observable)

        # Initialize requirements parser
        llm_provider = os.getenv("ARTEMIS_LLM_PROVIDER", "openai")
        self.requirements_parser = RequirementsParserAgent(
            llm_provider=llm_provider,
            logger=logger
        )

    def invoke_developer(
        self,
        developer_name: str,
        developer_type: str,
        card: Dict,
        adr_content: str,
        adr_file: str,
        output_dir: Path,
        rag_agent=None
    ) -> Dict:
        """
        Invoke a single developer agent

        Args:
            developer_name: "developer-a" or "developer-b"
            developer_type: "conservative" or "aggressive"
            card: Kanban card with task details
            adr_content: Full ADR content
            adr_file: Path to ADR file
            output_dir: Directory for developer output
            rag_agent: RAG Agent for querying feedback (optional)

        Returns:
            Dict with developer results
        """
        self.debug_trace("invoke_developer",
                        developer_name=developer_name,
                        developer_type=developer_type,
                        card_id=card.get('card_id', 'unknown'),
                        output_dir=str(output_dir))

        self.logger.log(f"Invoking {developer_name} ({developer_type} approach)", "INFO")

        # Notify developer started
        card_id = card.get('card_id', 'unknown')
        self.event_notifier.notify_developer_started(
            card_id=card_id,
            developer_name=developer_name,
            developer_type=developer_type,
            task_title=card.get('title')
        )

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get developer prompt file path
        prompt_file = str(get_developer_prompt_path(developer_name))

        # Get LLM provider from env
        llm_provider = os.getenv("ARTEMIS_LLM_PROVIDER", "openai")

        # Parse requirements for validation
        parsed_requirements = self._parse_requirements_for_task(card, adr_content)

        # Check validation flags
        enable_validation = os.getenv("ARTEMIS_ENABLE_VALIDATION", "true").lower() == "true"
        enable_rag_validation = os.getenv("ARTEMIS_ENABLE_RAG_VALIDATION", "true").lower() == "true"

        # Create validated developer agent
        agent = create_validated_developer_agent(
            developer_name=developer_name,
            developer_type=developer_type,
            llm_provider=llm_provider,
            logger=self.logger,
            rag_agent=rag_agent,
            enable_validation=enable_validation,
            enable_rag_validation=enable_rag_validation
        )

        # Execute implementation
        with self.debug_section("Developer Execution", developer=developer_name):
            result = agent.execute(
                task_title=card.get('title', 'Untitled Task'),
                task_description=card.get('description', 'No description provided'),
                adr_content=adr_content,
                adr_file=adr_file,
                output_dir=output_dir,
                developer_prompt_file=prompt_file,
                card_id=card.get('card_id', ''),
                rag_agent=rag_agent,
                parsed_requirements=parsed_requirements
            )

        self.debug_log("Developer execution completed",
                      developer=developer_name,
                      success=result.get('success', False),
                      files_created=len(result.get('files', [])))

        # Collect validation statistics
        if enable_validation and hasattr(agent, 'get_validation_stats'):
            validation_stats = agent.get_validation_stats()
            result['validation_stats'] = validation_stats

            # Log validation summary
            if validation_stats.get('total_validations', 0) > 0:
                self.logger.log(
                    f"📊 {developer_name} validation: "
                    f"{validation_stats.get('passed', 0)}/{validation_stats.get('total_validations', 0)} passed, "
                    f"{validation_stats.get('regenerations', 0)} regenerations",
                    "INFO"
                )

        self.logger.log(f"✅ {developer_name} completed", "SUCCESS")

        # Notify developer completed or failed
        if result.get('success', False):
            self.event_notifier.notify_developer_completed(
                card_id=card_id,
                developer_name=developer_name,
                files_created=len(result.get('files', [])),
                result=result
            )
        else:
            error = Exception(result.get('error', 'Developer failed'))
            self.event_notifier.notify_developer_failed(
                card_id=card_id,
                developer_name=developer_name,
                error=error,
                result=result
            )

        return result

    def _parse_requirements_for_task(self, card: Dict, adr_content: str) -> Optional[Dict]:
        """
        Parse requirements for validation system

        Args:
            card: Kanban card with task details
            adr_content: ADR content

        Returns:
            Parsed requirements dict or None
        """
        self.debug_trace("_parse_requirements_for_task", card_id=card.get('card_id'))

        try:
            parsed = self.requirements_parser.parse_requirements_for_validation(
                task_title=card.get('title', ''),
                task_description=card.get('description', ''),
                adr_content=adr_content
            )

            self.debug_log("Requirements parsed", artifact_type=parsed.get('artifact_type'))
            return parsed

        except Exception as e:
            self.debug_log("Requirements parsing failed", error=str(e))
            self.logger.log(f"⚠️  Requirements parsing failed: {e}", "WARNING")
            return None

    def invoke_parallel_developers(
        self,
        num_developers: int,
        card: Dict,
        adr_content: str,
        adr_file: str,
        rag_agent=None,
        parallel_execution: bool = True
    ) -> List[Dict]:
        """
        Invoke multiple developers in parallel or sequential mode

        Args:
            num_developers: Number of developers to invoke (1-3)
            card: Kanban card
            adr_content: ADR content
            adr_file: ADR file path
            rag_agent: RAG Agent for developers to query feedback (optional)
            parallel_execution: Run developers in parallel threads (default: True)

        Returns:
            List of developer results
        """
        self.debug_trace("invoke_parallel_developers",
                        num_developers=num_developers,
                        parallel_execution=parallel_execution,
                        card_id=card.get('card_id', 'unknown'))

        mode = 'parallel' if parallel_execution else 'sequential'
        self.logger.log(f"Invoking {num_developers} developer(s) ({mode})", "INFO")

        # Prepare developer configurations
        dev_configs = self._prepare_developer_configs(
            num_developers, card, adr_content, adr_file, rag_agent
        )

        # Create execution strategy (parallel or sequential)
        strategy = ExecutionStrategyFactory.create_strategy(
            parallel=parallel_execution and num_developers > 1,
            logger=self.logger
        )

        # Execute developers using strategy
        developers = strategy.execute(dev_configs, self.invoke_developer)

        return developers

    def _prepare_developer_configs(
        self,
        num_developers: int,
        card: Dict,
        adr_content: str,
        adr_file: str,
        rag_agent
    ) -> List[Dict]:
        """
        Prepare developer configurations

        Args:
            num_developers: Number of developers
            card: Kanban card
            adr_content: ADR content
            adr_file: ADR file path
            rag_agent: RAG agent

        Returns:
            List of developer configuration dicts
        """
        # Dispatch table for developer configurations
        DEVELOPER_CONFIGS = [
            ("developer-a", "conservative"),
            ("developer-b", "aggressive"),
            ("developer-c", "innovative")
        ]

        dev_configs = []

        for i in range(num_developers):
            # Guard clause - don't exceed config table
            if i >= len(DEVELOPER_CONFIGS):
                break

            dev_name, dev_type = DEVELOPER_CONFIGS[i]
            output_dir = Path(self.developer_base_dir) / dev_name

            dev_configs.append({
                "developer_name": dev_name,
                "developer_type": dev_type,
                "card": card,
                "adr_content": adr_content,
                "adr_file": adr_file,
                "output_dir": output_dir,
                "rag_agent": rag_agent
            })

        return dev_configs
