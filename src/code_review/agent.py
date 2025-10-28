#!/usr/bin/env python3
"""
WHY: Code Review Agent - Main Orchestrator
RESPONSIBILITY: Coordinate code review process using AI services
PATTERNS: Dependency injection, strategy pattern, guard clauses
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from llm_client import create_llm_client, LLMMessage
from artemis_exceptions import (
    CodeReviewExecutionError,
    FileReadError,
    LLMAPIError,
    wrap_exception
)
from review_request_builder import (
    ImplementationFile,
    read_implementation_files
)
from ai_query_service import (
    AIQueryService,
    create_ai_query_service,
    QueryType
)

from code_review.strategies import (
    build_base_review_prompt,
    build_review_request_legacy,
    extract_file_types,
    read_review_prompt
)
from code_review.response_parser import parse_review_response
from code_review.report_generator import write_review_report


class CodeReviewAgent:
    """
    Autonomous code review agent that analyzes implementations for quality,
    security, GDPR compliance, and accessibility.

    WHY: Centralized code review with AI-enhanced analysis.
    RESPONSIBILITY: Orchestrate review process (KG→RAG→LLM pipeline).
    PATTERNS: Dependency injection, strategy pattern, template method.
    """

    def __init__(
        self,
        developer_name: str,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        rag_agent: Optional[Any] = None,
        ai_service: Optional[AIQueryService] = None
    ):
        """
        Initialize the code review agent.

        Args:
            developer_name: Name of the developer whose code to review (e.g., "developer-a")
            llm_provider: LLM provider ("openai" or "anthropic")
            llm_model: Specific model to use (optional)
            logger: Logger instance (optional)
            rag_agent: RAG agent for prompt management (optional)
            ai_service: Centralized AI Query Service (optional)
        """
        self.developer_name = developer_name
        self.llm_provider = llm_provider or os.getenv("ARTEMIS_LLM_PROVIDER", "openai")
        self.llm_model = llm_model or os.getenv("ARTEMIS_LLM_MODEL")
        self.logger = logger or self._setup_logger()

        # Initialize LLM client
        self.llm_client = create_llm_client(provider=self.llm_provider)

        # Initialize PromptManager if RAG is available
        self.prompt_manager = self._initialize_prompt_manager(rag_agent)

        # Initialize centralized AI Query Service
        self.ai_service = self._initialize_ai_service(ai_service, rag_agent)

        self._log_initialization()

    def _initialize_prompt_manager(self, rag_agent: Optional[Any]) -> Optional[Any]:
        """
        Initialize PromptManager if available.

        WHY: Extracted to avoid nested if in __init__.
        RESPONSIBILITY: Conditional PromptManager setup.
        PATTERN: Guard clauses.

        Args:
            rag_agent: RAG agent instance

        Returns:
            PromptManager instance or None
        """
        try:
            from prompt_manager import PromptManager

            if not rag_agent:
                return None

            prompt_manager = PromptManager(rag_agent, verbose=False)
            self.logger.info("✅ Prompt manager initialized (RAG-based prompts)")
            return prompt_manager

        except ImportError:
            return None
        except Exception as e:
            self.logger.warning(f"⚠️  Could not initialize PromptManager: {e}")
            return None

    def _initialize_ai_service(
        self,
        ai_service: Optional[AIQueryService],
        rag_agent: Optional[Any]
    ) -> Optional[AIQueryService]:
        """
        Initialize AI Query Service.

        WHY: Extracted to avoid nested if in __init__.
        RESPONSIBILITY: AI service setup with fallback.
        PATTERN: Guard clauses with early returns.

        Args:
            ai_service: Pre-configured AI service
            rag_agent: RAG agent instance

        Returns:
            AIQueryService instance or None
        """
        if ai_service:
            self.logger.info("✅ Using provided AI Query Service")
            return ai_service

        try:
            service = create_ai_query_service(
                llm_client=self.llm_client,
                rag=rag_agent,
                logger=self.logger,
                verbose=False
            )
            self.logger.info("✅ AI Query Service initialized (KG→RAG→LLM)")
            return service

        except Exception as e:
            self.logger.warning(f"⚠️  Could not initialize AI Query Service: {e}")
            return None

    def _log_initialization(self) -> None:
        """
        Log initialization details.

        WHY: Extracted for clarity in __init__.
        RESPONSIBILITY: Informative logging.
        """
        self.logger.info(f"🔍 Code Review Agent initialized for {self.developer_name}")
        self.logger.info(f"   LLM Provider: {self.llm_provider}")

        if self.llm_model:
            self.logger.info(f"   Model: {self.llm_model}")
        else:
            self.logger.info(f"   Model: default for {self.llm_provider}")

    def _setup_logger(self) -> logging.Logger:
        """
        Setup default logger.

        WHY: Consistent logging configuration.
        RESPONSIBILITY: Logger creation and configuration.
        """
        logger = logging.getLogger(f"CodeReviewAgent-{self.developer_name}")

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        return logger

    def review_implementation(
        self,
        implementation_dir: str,
        task_title: str,
        task_description: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code review using AIQueryService (KG→RAG→LLM pipeline).

        Uses centralized AIQueryService to automatically query Knowledge Graph
        for similar code reviews, get RAG recommendations, and call LLM with
        enhanced context, reducing token usage by 30-40%.

        Args:
            implementation_dir: Directory containing implementation files
            task_title: Title of the task
            task_description: Description of what was implemented
            output_dir: Directory to write review report

        Returns:
            Dictionary with review results
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🔍 Starting Code Review for {self.developer_name}")
        self.logger.info(f"{'='*80}")

        try:
            # Prepare review context
            review_context = self._prepare_review_context(
                implementation_dir, task_title, task_description
            )

            # Execute review using AI service or fallback
            review_response_data = self._execute_review_analysis(review_context)

            # Process and finalize review
            return self._finalize_review_results(
                review_response_data, task_title, output_dir
            )

        except CodeReviewExecutionError:
            raise
        except Exception as e:
            raise wrap_exception(
                e,
                CodeReviewExecutionError,
                f"Code review execution failed for {self.developer_name}",
                {
                    "developer_name": self.developer_name,
                    "implementation_dir": implementation_dir,
                    "task_title": task_title
                }
            )

    def _prepare_review_context(
        self,
        implementation_dir: str,
        task_title: str,
        task_description: str
    ) -> Dict[str, Any]:
        """
        Prepare all context needed for code review.

        WHY: Separate context preparation from execution.
        RESPONSIBILITY: Gather all inputs for review.
        PATTERN: Template method.

        Args:
            implementation_dir: Directory with implementation
            task_title: Task title
            task_description: Task description

        Returns:
            Dict with implementation files, prompts, and base prompt

        Raises:
            CodeReviewExecutionError: If no files found
        """
        # Step 1: Read implementation files
        implementation_files = self._read_implementation_files(implementation_dir)

        if not implementation_files:
            raise CodeReviewExecutionError(
                "No implementation files found",
                context={"implementation_dir": implementation_dir}
            )

        self.logger.info(f"📁 Read {len(implementation_files)} implementation files")

        # Step 2: Read code review prompt
        review_prompt = read_review_prompt(self.prompt_manager, self.logger)

        # Step 3: Build base review prompt
        base_prompt = build_base_review_prompt(
            review_prompt=review_prompt,
            implementation_files=implementation_files,
            task_title=task_title,
            task_description=task_description
        )

        return {
            'implementation_files': implementation_files,
            'review_prompt': review_prompt,
            'base_prompt': base_prompt
        }

    def _execute_review_analysis(self, review_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code review analysis using AI service or fallback.

        WHY: Strategy pattern for execution path selection.
        RESPONSIBILITY: Route to AI service or legacy path.
        PATTERN: Strategy pattern with dispatch.

        Args:
            review_context: Prepared review context

        Returns:
            Dict with review_content, tokens_used, and model_used
        """
        if self.ai_service:
            return self._execute_review_with_ai_service(review_context)
        else:
            return self._execute_review_legacy(review_context)

    def _execute_review_with_ai_service(self, review_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute review using AI Query Service (KG→RAG→LLM pipeline).

        WHY: Leverage knowledge graph and RAG for enhanced reviews.
        RESPONSIBILITY: AI service invocation with KG context.
        PATTERN: Strategy implementation.

        Args:
            review_context: Prepared review context

        Returns:
            Dict with review content and metadata

        Raises:
            CodeReviewExecutionError: If AI service fails
        """
        self.logger.info("🔄 Using AI Query Service for KG→RAG→LLM pipeline")

        # Extract file types for KG query
        file_types = extract_file_types(review_context['implementation_files'])

        result = self.ai_service.query(
            query_type=QueryType.CODE_REVIEW,
            prompt=review_context['base_prompt'],
            kg_query_params={'file_types': file_types},
            temperature=0.2,
            max_tokens=4000
        )

        if not result.success:
            raise CodeReviewExecutionError(
                f"AI Query Service failed: {result.error}",
                context={"developer_name": self.developer_name}
            )

        # Log token savings
        if result.kg_context and result.kg_context.pattern_count > 0:
            self.logger.info(
                f"📊 KG found {result.kg_context.pattern_count} review patterns, "
                f"saved ~{result.llm_response.tokens_saved} tokens"
            )

        return {
            'review_content': result.llm_response.content,
            'tokens_used': result.llm_response.tokens_used,
            'model_used': result.llm_response.model
        }

    def _execute_review_legacy(self, review_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute review using direct LLM call (fallback).

        WHY: Graceful degradation when AI service unavailable.
        RESPONSIBILITY: Direct LLM invocation.
        PATTERN: Fallback strategy.

        Args:
            review_context: Prepared review context

        Returns:
            Dict with review content and metadata
        """
        self.logger.warning("⚠️  AI Query Service unavailable - using direct LLM call")

        review_request = build_review_request_legacy(review_context['base_prompt'])
        review_response = self._call_llm_for_review(review_request)

        return {
            'review_content': review_response.content,
            'tokens_used': review_response.usage,
            'model_used': review_response.model
        }

    def _finalize_review_results(
        self,
        review_response_data: Dict[str, Any],
        task_title: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Parse review response, add metadata, write report, and return results.

        WHY: Separate finalization concerns from execution.
        RESPONSIBILITY: Result assembly and output generation.
        PATTERN: Template method.

        Args:
            review_response_data: Raw review response data
            task_title: Task title
            output_dir: Output directory

        Returns:
            Dict with review results for the stage
        """
        # Parse review JSON
        review_data = parse_review_response(
            review_response_data['review_content'],
            self.developer_name,
            self.logger
        )

        # Add metadata
        review_data['metadata'] = {
            'developer_name': self.developer_name,
            'task_title': task_title,
            'reviewed_at': datetime.now().isoformat(),
            'llm_provider': self.llm_provider,
            'llm_model': review_response_data['model_used'],
            'tokens_used': review_response_data['tokens_used']
        }

        # Write review report
        report_file = write_review_report(
            review_data,
            output_dir,
            self.developer_name,
            self.logger
        )

        # Return results
        return {
            'status': 'COMPLETED',
            'developer_name': self.developer_name,
            'review_status': review_data['review_summary']['overall_status'],
            'total_issues': review_data['review_summary']['total_issues'],
            'critical_issues': review_data['review_summary']['critical_issues'],
            'high_issues': review_data['review_summary']['high_issues'],
            'overall_score': review_data['review_summary']['score']['overall'],
            'report_file': report_file,
            'tokens_used': review_response_data['tokens_used']
        }

    def _read_implementation_files(self, implementation_dir: str) -> List[ImplementationFile]:
        """
        Read all implementation files from directory using Builder pattern.

        WHY: Use existing builder for consistency.
        RESPONSIBILITY: File reading with error handling.
        PATTERN: Adapter to review_request_builder.

        Args:
            implementation_dir: Directory path

        Returns:
            List of ImplementationFile value objects

        Raises:
            FileReadError: If file reading fails
        """
        try:
            files = read_implementation_files(implementation_dir)

            # Log file details
            for file in files:
                self.logger.debug(f"  Read {file.path} ({file.lines} lines)")

            return files

        except FileNotFoundError:
            self.logger.warning(f"Implementation directory not found: {implementation_dir}")
            return []
        except Exception as e:
            raise wrap_exception(
                e,
                FileReadError,
                "Failed to read implementation files",
                {
                    "implementation_dir": implementation_dir,
                    "developer_name": self.developer_name
                }
            )

    def _call_llm_for_review(self, messages: List[LLMMessage]) -> Any:
        """
        Call LLM API to perform code review.

        WHY: Centralized LLM invocation with error handling.
        RESPONSIBILITY: LLM API call with proper configuration.
        PATTERN: Guard clauses for parameters.

        Args:
            messages: List of LLM messages

        Returns:
            LLM response object

        Raises:
            LLMAPIError: If LLM call fails
        """
        try:
            # Prepare kwargs for LLM call
            kwargs = {
                "messages": messages,
                "temperature": 0.3,  # Lower temperature for more consistent analysis
                "max_tokens": 4000  # Large enough for detailed review
            }

            # Only pass model if explicitly specified
            if self.llm_model:
                kwargs["model"] = self.llm_model

            response = self.llm_client.complete(**kwargs)

            self.logger.info("✅ LLM review completed")
            self.logger.info(f"   Tokens used: {response.usage.get('total_tokens', 'unknown')}")

            return response

        except Exception as e:
            raise wrap_exception(
                e,
                LLMAPIError,
                "LLM API call failed during code review",
                {
                    "developer_name": self.developer_name,
                    "llm_provider": self.llm_provider,
                    "llm_model": self.llm_model
                }
            )

    def create_error_result(self, error_message: str) -> Dict[str, Any]:
        """
        Create an error result dictionary.

        WHY: Consistent error result format.
        RESPONSIBILITY: Error result construction.

        Args:
            error_message: Error description

        Returns:
            Error result dictionary
        """
        return {
            'status': 'ERROR',
            'developer_name': self.developer_name,
            'error': error_message,
            'review_status': 'FAIL',
            'total_issues': 0,
            'critical_issues': 0,
            'high_issues': 0,
            'overall_score': 0
        }
