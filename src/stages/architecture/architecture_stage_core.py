#!/usr/bin/env python3
"""
Architecture Stage Core

WHY: Orchestrate the architecture stage workflow
RESPONSIBILITY: Coordinate ADR creation, user stories, and storage
PATTERNS: Facade Pattern, Single Responsibility, Guard Clauses
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from artemis_stage_interface import PipelineStage, LoggerInterface
from artemis_services import FileManager
from kanban_manager import KanbanBoard
from agent_messenger import AgentMessenger
from rag_agent import RAGAgent
from supervised_agent_mixin import SupervisedStageMixin
from debug_mixin import DebugMixin

from ai_query_service import AIQueryService, create_ai_query_service

from .adr_file_manager import ADRFileManager
from .adr_generator import ADRGenerator
from .user_story_generator import UserStoryGenerator
from .kg_storage import KGArchitectureStorage
from .rag_storage import RAGArchitectureStorage

# Import PromptManager for RAG-based prompts
try:
    from prompt_manager import PromptManager
    PROMPT_MANAGER_AVAILABLE = True
except ImportError:
    PROMPT_MANAGER_AVAILABLE = False


class ArchitectureStage(PipelineStage, SupervisedStageMixin, DebugMixin):
    """
    Architecture Stage - Create Architecture Decision Records (ADRs).

    WHY: Orchestrate ADR creation and user story generation
    RESPONSIBILITY: Coordinate architecture workflow components
    PATTERNS: Facade Pattern, Dependency Injection, Guard Clauses

    Integrates with supervisor for:
    - Unexpected state handling (ADR generation failures)
    - LLM cost tracking (if using LLM for ADR generation)
    - Automatic heartbeat and health monitoring
    """

    def __init__(
        self,
        board: KanbanBoard,
        messenger: AgentMessenger,
        rag: RAGAgent,
        logger: LoggerInterface,
        adr_dir: Optional[Path] = None,
        supervisor: Optional['SupervisorAgent'] = None,
        llm_client: Optional[Any] = None,
        ai_service: Optional[AIQueryService] = None
    ):
        """
        Initialize Architecture Stage.

        Args:
            board: Kanban board for task management
            messenger: Agent messenger for notifications
            rag: RAG agent for storage
            logger: Logger interface
            adr_dir: Directory for ADRs (optional)
            supervisor: Supervisor agent (optional)
            llm_client: LLM client for generation (optional)
            ai_service: AI Query Service (optional)

        WHY: Dependency injection for all components
        PATTERN: Constructor injection with defaults
        """
        # Initialize PipelineStage
        PipelineStage.__init__(self)

        # Set ADR directory from config or use default
        if adr_dir is None:
            adr_dir = self._resolve_adr_directory()

        # Initialize SupervisedStageMixin for health monitoring
        SupervisedStageMixin.__init__(
            self,
            supervisor=supervisor,
            stage_name="ArchitectureStage",
            heartbeat_interval=15
        )

        # Initialize DebugMixin
        DebugMixin.__init__(self, component_name="architecture")

        self.board = board
        self.messenger = messenger
        self.rag = rag
        self.logger = logger
        self.llm_client = llm_client

        # Initialize file manager
        self.file_manager = ADRFileManager(adr_dir)

        # Initialize PromptManager if available
        self.prompt_manager = self._initialize_prompt_manager()

        # Initialize centralized AI Query Service
        self.ai_service = self._initialize_ai_service(ai_service, llm_client, rag)

        # Initialize component modules
        self.adr_generator = ADRGenerator(
            ai_service=self.ai_service,
            logger=logger,
            debug_mixin=self
        )

        self.user_story_generator = UserStoryGenerator(
            llm_client=llm_client,
            prompt_manager=self.prompt_manager,
            logger=logger
        )

        self.kg_storage = KGArchitectureStorage(logger=logger)
        self.rag_storage = RAGArchitectureStorage(rag=rag, logger=logger)

    def execute(self, card: Dict, context: Dict) -> Dict:
        """
        Create ADR for the task with supervisor monitoring.

        Args:
            card: Task card
            context: Execution context

        Returns:
            Execution result with ADR details

        WHY: Main entry point for stage execution
        PATTERN: Supervised execution wrapper
        """
        metadata = {
            "task_id": card.get('card_id'),
            "stage": "architecture"
        }

        with self.supervised_execution(metadata):
            return self._create_adr(card, context)

    def get_stage_name(self) -> str:
        """Get stage name"""
        return "architecture"

    def _create_adr(self, card: Dict, context: Dict) -> Dict:
        """
        Internal method that performs ADR creation.

        WHY: Core business logic separated from supervision
        PATTERN: Step-by-step workflow with progress tracking
        """
        self.logger.log("Starting Architecture Stage", "STAGE")

        card_id = card['card_id']

        # DEBUG: Log architecture stage start
        self.debug_log("Starting ADR creation", card_id=card_id, title=card.get('title'))

        # Check for structured requirements
        structured_requirements = self._get_structured_requirements(context)

        # Step 1: Get next ADR number
        self.update_progress({"step": "getting_adr_number", "progress_percent": 10})
        adr_number = self.file_manager.get_next_adr_number()

        # Step 2: Generate ADR
        self.update_progress({"step": "generating_adr", "progress_percent": 30})
        adr_content = self.adr_generator.generate_adr(card, adr_number, structured_requirements)

        # Step 3: Write ADR file
        self.update_progress({"step": "writing_adr_file", "progress_percent": 50})
        adr_filename = self.file_manager.create_adr_filename(card['title'], adr_number)
        adr_path = self.file_manager.get_adr_path(adr_filename)
        FileManager.write_text(adr_path, adr_content)
        self.logger.log(f"ADR created: {adr_filename}", "SUCCESS")

        # Step 4: Send notifications
        self.update_progress({"step": "sending_notifications", "progress_percent": 65})
        self._send_adr_notification(card_id, str(adr_path), adr_number)

        # Step 5: Update Kanban
        self.update_progress({"step": "updating_kanban", "progress_percent": 80})
        self._update_kanban(card_id, adr_number, str(adr_path))

        # Step 6: Store ADR in RAG
        self.update_progress({"step": "storing_adr_in_rag", "progress_percent": 70})
        self.rag_storage.store_adr(
            card_id=card_id,
            task_title=card.get('title', 'Unknown'),
            adr_content=adr_content,
            adr_number=adr_number,
            adr_path=str(adr_path),
            card=card
        )

        # Step 7: Store ADR in Knowledge Graph
        self.kg_storage.store_adr(
            card_id=card_id,
            adr_number=adr_number,
            adr_path=str(adr_path),
            structured_requirements=structured_requirements
        )

        # Step 8: Generate user stories
        self.update_progress({"step": "generating_user_stories", "progress_percent": 80})
        user_stories = self.user_story_generator.generate_user_stories(
            adr_content, adr_number, card
        )

        # Step 9: Add user stories to Kanban
        self.update_progress({"step": "adding_stories_to_kanban", "progress_percent": 90})
        story_cards = self._add_user_stories_to_kanban(user_stories, card, adr_number)

        # Step 10: Store Kanban state in RAG
        self.update_progress({"step": "storing_kanban_in_rag", "progress_percent": 95})
        self.rag_storage.store_kanban_state(card_id, story_cards, self.board)

        # Complete
        self.update_progress({"step": "complete", "progress_percent": 100})

        return {
            "stage": "architecture",
            "adr_number": adr_number,
            "adr_file": str(adr_path),
            "user_stories_created": len(story_cards),
            "story_card_ids": story_cards,
            "status": "COMPLETE"
        }

    def _get_structured_requirements(self, context: Dict) -> Optional[Any]:
        """
        Get structured requirements from context.

        WHY: Check for requirements from earlier stage
        PATTERN: Guard clause with logging
        """
        structured_requirements = context.get('structured_requirements')

        if not structured_requirements:
            return None

        self.logger.log("✅ Using structured requirements from requirements parsing stage", "INFO")
        self.logger.log(
            f"   Found {len(structured_requirements.functional_requirements)} functional requirements",
            "INFO"
        )
        self.logger.log(
            f"   Found {len(structured_requirements.non_functional_requirements)} non-functional requirements",
            "INFO"
        )

        # DEBUG: Dump structured requirements info
        self.debug_dump_if_enabled('dump_design', "Structured Requirements Summary", {
            "project": structured_requirements.project_name,
            "functional_count": len(structured_requirements.functional_requirements),
            "non_functional_count": len(structured_requirements.non_functional_requirements),
            "use_cases": len(structured_requirements.use_cases)
        })

        return structured_requirements

    def _send_adr_notification(self, card_id: str, adr_path: str, adr_number: str) -> None:
        """
        Send ADR notification to downstream agents.

        WHY: Notify other agents of ADR completion
        PATTERN: Fire-and-forget messaging
        """
        self.messenger.send_data_update(
            to_agent="dependency-validation-agent",
            card_id=card_id,
            update_type="adr_created",
            data={
                "adr_file": adr_path,
                "adr_number": adr_number
            },
            priority="high"
        )

        self.messenger.update_shared_state(
            card_id=card_id,
            updates={
                "current_stage": "architecture_complete",
                "adr_file": adr_path,
                "adr_number": adr_number
            }
        )

    def _update_kanban(self, card_id: str, adr_number: str, adr_path: str) -> None:
        """
        Update Kanban board with ADR information.

        WHY: Track ADR creation in project board
        PATTERN: Simple update and move
        """
        self.board.update_card(card_id, {
            "architecture_status": "complete",
            "adr_number": adr_number,
            "adr_file": adr_path
        })
        self.board.move_card(card_id, "development", "pipeline-orchestrator")

    def _add_user_stories_to_kanban(
        self,
        user_stories: List[Dict],
        parent_card: Dict,
        adr_number: str
    ) -> List[str]:
        """
        Add user stories to Kanban board.

        WHY: Create actionable tasks from ADR
        PATTERN: Builder pattern for card creation
        """
        story_cards = []

        for idx, story in enumerate(user_stories):
            story_task_id = f"{parent_card['card_id']}-story-{idx+1}"

            # Use CardBuilder pattern to create story card
            story_card = (
                self.board.new_card(story_task_id, story['title'])
                .with_description(story['description'])
                .with_priority(story.get('priority', parent_card.get('priority', 'medium')))
                .with_story_points(story.get('points', 3))
                .build()
            )

            # Add metadata
            story_card['metadata'] = {
                'parent_adr': adr_number,
                'parent_card': parent_card['card_id'],
                'acceptance_criteria': story.get('acceptance_criteria', [])
            }

            # Add card to board
            self.board.add_card(story_card)
            story_cards.append(story_task_id)
            self.logger.log(f"  ✅ Created user story: {story['title']}", "INFO")

        return story_cards

    def _resolve_adr_directory(self) -> Path:
        """
        Resolve ADR directory path from environment or default.

        WHY: Support configurable ADR location
        PATTERN: Environment variable with fallback
        """
        adr_path = os.getenv("ARTEMIS_ADR_DIR", "../../.artemis_data/adrs")

        if os.path.isabs(adr_path):
            return Path(adr_path)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        adr_path = os.path.join(script_dir, adr_path)
        return Path(adr_path)

    def _initialize_prompt_manager(self) -> Optional[Any]:
        """
        Initialize PromptManager if available.

        WHY: Support RAG-based prompts
        PATTERN: Guard clause with error handling
        """
        if not PROMPT_MANAGER_AVAILABLE:
            return None

        if not self.rag:
            return None

        try:
            prompt_manager = PromptManager(self.rag, verbose=False)
            self.logger.log("✅ Prompt manager initialized (RAG-based prompts)", "INFO")
            return prompt_manager
        except Exception as e:
            self.logger.log(f"⚠️  Could not initialize PromptManager: {e}", "WARNING")
            return None

    def _initialize_ai_service(
        self,
        ai_service: Optional[AIQueryService],
        llm_client: Optional[Any],
        rag: RAGAgent
    ) -> Optional[AIQueryService]:
        """
        Initialize centralized AI Query Service.

        WHY: Support KG→RAG→LLM pipeline
        PATTERN: Guard clause with error handling
        """
        try:
            if ai_service:
                self.logger.log("✅ Using provided AI Query Service", "INFO")
                return ai_service

            service = create_ai_query_service(
                llm_client=llm_client,
                rag=rag,
                logger=self.logger,
                verbose=False
            )
            self.logger.log("✅ AI Query Service initialized (KG→RAG→LLM)", "INFO")
            return service

        except Exception as e:
            self.logger.log(f"⚠️  Could not initialize AI Query Service: {e}", "WARNING")
            return None
