#!/usr/bin/env python3
"""
SSD Generation Stage Orchestrator

WHY: Orchestrates the entire SSD generation pipeline.
RESPONSIBILITY: Coordinate all services to produce complete SSD.
PATTERNS:
- Facade pattern (simplifies complex subsystem)
- Dependency injection
- Guard clauses (Pattern #10)
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from artemis_stage_interface import PipelineStage, LoggerInterface
from artemis_exceptions import PipelineStageError, wrap_exception
from llm_client import LLMClient
from rag_agent import RAGAgent

from ssd_generation.models.ssd_document import SSDDocument
from ssd_generation.services.ssd_decision_service import SSDDecisionService
from ssd_generation.services.requirements_analyzer import RequirementsAnalyzer
from ssd_generation.services.diagram_generator import DiagramGenerator
from ssd_generation.services.rag_storage_service import RAGStorageService
from ssd_generation.generators.output_file_generator import OutputFileGenerator


class SSDGenerationStage(PipelineStage):
    """
    Software Specification Document Generation Stage

    WHY: Creates comprehensive SSD documents for architecture guidance.
    WHEN: Called after workflow planning, before architecture design.
    Implements PipelineStage interface following SOLID principles.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        rag: Optional[RAGAgent] = None,
        logger: Optional[LoggerInterface] = None,
        output_dir: Optional[Path] = None,
        verbose: bool = True
    ):
        """
        Initialize SSD Generation Stage

        Args:
            llm_client: LLM client for generating specifications
            rag: RAG agent for storing SSD artifacts
            logger: Logger interface
            output_dir: Directory for output files (default: .artemis_data/ssd)
            verbose: Enable verbose logging
        """
        self.llm_client = llm_client
        self.rag = rag
        self.logger = logger
        self.verbose = verbose

        # Set output directory
        self.output_dir = output_dir or Path(".artemis_data/ssd")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize services
        self.decision_service = SSDDecisionService()
        self.requirements_analyzer = RequirementsAnalyzer(
            llm_client=llm_client,
            logger=logger,
            verbose=verbose
        )
        self.diagram_generator = DiagramGenerator(
            llm_client=llm_client,
            logger=logger,
            verbose=verbose
        )
        self.output_generator = OutputFileGenerator(
            output_dir=self.output_dir,
            logger=logger,
            verbose=verbose
        )

        # Initialize RAG storage service if RAG available
        self.rag_storage = None
        if self.rag:
            self.rag_storage = RAGStorageService(
                rag=rag,
                logger=logger,
                verbose=verbose
            )

        if self.verbose and self.logger:
            self.logger.log(f"[SSD] Output directory: {self.output_dir}", "INFO")

    def get_stage_name(self) -> str:
        """Return the stage name for identification"""
        return "ssd_generation"

    def execute(self, card_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute SSD generation stage

        This stage intelligently decides whether a full SSD is needed based on:
        - Task complexity (simple tasks like refactoring skip SSD)
        - Task type (documentation, small fixes skip SSD)
        - Project scope (new features need SSD, bug fixes may not)

        Args:
            card_id: Kanban card ID
            context: Pipeline context containing card and workflow plan

        Returns:
            Dict with SSD document, file paths, and metadata
            OR Dict with status="skipped" if SSD not needed
        """
        # Guard clause: Validate inputs
        if not card_id:
            raise PipelineStageError("SSD Generation", "card_id is required")

        if not context or 'card' not in context:
            raise PipelineStageError("SSD Generation", "context must contain 'card'")

        card = context['card']

        if self.verbose and self.logger:
            self.logger.log("=" * 60, "STAGE")
            self.logger.log("📄 SOFTWARE SPECIFICATION DOCUMENT GENERATION", "STAGE")
            self.logger.log("=" * 60, "STAGE")

        try:
            # STEP 0: Decide if SSD is needed (Pattern #10: Early return for skip case)
            ssd_decision = self.decision_service.should_generate_ssd(card, context)

            if not ssd_decision['needed']:
                return self._handle_skip(ssd_decision)

            if self.verbose and self.logger:
                self.logger.log(
                    f"✅ SSD generation required: {ssd_decision['reason']}",
                    "INFO"
                )

            # Step 1: Analyze requirements from card
            requirements_analysis = self.requirements_analyzer.analyze_requirements(
                card,
                context
            )

            # Step 2: Generate executive summary and business case
            executive_content = self.requirements_analyzer.generate_executive_summary(
                card,
                requirements_analysis
            )

            # Step 3: Extract structured requirements
            structured_requirements = self.requirements_analyzer.extract_requirements(
                card,
                requirements_analysis
            )

            # Step 4: Generate diagram specifications
            diagram_specs = self.diagram_generator.generate_diagram_specifications(
                card,
                structured_requirements,
                context
            )

            # Step 5: Generate constraints, assumptions, risks
            additional_sections = self.requirements_analyzer.generate_additional_sections(
                card,
                requirements_analysis
            )

            # Step 6: Build complete SSD document
            ssd_document = self._build_ssd_document(
                card,
                card_id,
                executive_content,
                structured_requirements,
                diagram_specs,
                additional_sections
            )

            # Step 7: Generate output files (JSON, Markdown, HTML, PDF)
            file_paths = self.output_generator.generate_output_files(
                card_id,
                ssd_document
            )

            # Step 8: Store in RAG for architecture agent
            if self.rag_storage:
                self.rag_storage.store_ssd(card_id, ssd_document)

            if self.verbose and self.logger:
                self._log_success(file_paths)

            return {
                "status": "success",
                "ssd_document": ssd_document.to_dict(),
                "file_paths": file_paths,
                "requirements_count": {
                    "functional": len(ssd_document.functional_requirements),
                    "non_functional": len(ssd_document.non_functional_requirements),
                    "business": len(ssd_document.business_requirements),
                },
                "diagrams_count": len(ssd_document.diagrams)
            }

        except Exception as e:
            error_msg = f"Failed to generate SSD: {str(e)}"
            if self.logger:
                self.logger.log(f"❌ {error_msg}", "ERROR")
            raise wrap_exception(e, PipelineStageError, "SSD Generation", error_msg)

    def _handle_skip(self, ssd_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SSD skip case"""
        if self.verbose and self.logger:
            self.logger.log(
                f"⏭️  SSD generation skipped: {ssd_decision['reason']}",
                "INFO"
            )
            self.logger.log(
                f"   Complexity: {ssd_decision['complexity']}",
                "INFO"
            )
            self.logger.log(
                f"   Task type: {ssd_decision['task_type']}",
                "INFO"
            )

        return {
            "status": "skipped",
            "reason": ssd_decision['reason'],
            "complexity": ssd_decision['complexity'],
            "task_type": ssd_decision['task_type'],
            "ssd_needed": False
        }

    def _build_ssd_document(
        self,
        card: Dict[str, Any],
        card_id: str,
        executive_content: Dict[str, str],
        structured_requirements: Dict[str, Any],
        diagram_specs: Any,
        additional_sections: Dict[str, Any]
    ) -> SSDDocument:
        """Build complete SSD document"""
        return SSDDocument(
            project_name=card.get('title', 'Untitled Project'),
            card_id=card_id,
            generated_at=datetime.now().isoformat(),
            executive_summary=executive_content['executive_summary'],
            business_case=executive_content['business_case'],
            functional_requirements=structured_requirements['functional'],
            non_functional_requirements=structured_requirements['non_functional'],
            business_requirements=structured_requirements['business'],
            diagrams=diagram_specs,
            constraints=additional_sections['constraints'],
            assumptions=additional_sections['assumptions'],
            risks=additional_sections['risks'],
            success_criteria=additional_sections['success_criteria']
        )

    def _log_success(self, file_paths: Dict[str, str]) -> None:
        """Log successful generation"""
        self.logger.log("✅ SSD Generation Complete", "SUCCESS")
        self.logger.log(f"   - JSON: {file_paths['json']}", "INFO")
        self.logger.log(f"   - Markdown: {file_paths['markdown']}", "INFO")
        self.logger.log(f"   - HTML: {file_paths['html']}", "INFO")
        if 'pdf' in file_paths:
            self.logger.log(f"   - PDF: {file_paths['pdf']}", "INFO")
