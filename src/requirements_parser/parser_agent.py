from artemis_logger import get_logger
logger = get_logger('parser_agent')
'\nRequirements Parser Agent\n\nWHY: Orchestrate requirements parsing with multiple strategies\nRESPONSIBILITY: Coordinate extraction, conversion, and output\nPATTERNS: Facade pattern - simplifies complex parsing workflow\n'
import json
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime
from requirements_models import StructuredRequirements
from llm_client import LLMClient, LLMMessage
from document_reader import DocumentReader
from debug_mixin import DebugMixin
from artemis_exceptions import RequirementsFileError, RequirementsParsingError, wrap_exception
from requirements_parser.extraction_engine import ExtractionEngine
from requirements_parser.conversion_utils import RequirementsConverter
from requirements_parser.prompt_integration import PromptManagerIntegration
from requirements_parser.ai_service_integration import AIServiceIntegration

class RequirementsParserAgent(DebugMixin):
    """
    Parse free-form requirements into structured format

    WHY: Convert unstructured requirements → structured requirements
    RESPONSIBILITY: Orchestrate parsing workflow with fallback strategies

    Input: Free-form text file (requirements.txt, requirements.md, etc.)
    Output: StructuredRequirements object → YAML/JSON

    Uses LLM to:
    1. Extract functional requirements
    2. Identify non-functional requirements
    3. Detect use cases and user stories
    4. Identify stakeholders, constraints, assumptions
    5. Extract data and integration requirements
    6. Assign priorities and categorize requirements

    Strategies (in order of preference):
    1. PromptManager + AI Service (production-grade single-call)
    2. Multi-step extraction (fallback legacy mode)
    """

    def __init__(self, llm_provider: str='openai', llm_model: Optional[str]=None, verbose: bool=True, rag: Optional[Any]=None, ai_service: Optional[Any]=None, logger: Optional[Any]=None):
        """
        Initialize Requirements Parser Agent

        Args:
            llm_provider: LLM provider (openai, anthropic)
            llm_model: Specific model to use
            verbose: Enable verbose logging
            rag: RAG agent for PromptManager (optional)
            ai_service: Centralized AI Query Service (optional, created if not provided)
            logger: Logger instance (optional)
        """
        DebugMixin.__init__(self, component_name='requirements_parser')
        self.verbose = verbose
        self.logger = logger
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.debug_log('RequirementsParserAgent initialized', provider=self.llm_provider, verbose=verbose)
        from llm_client import LLMClientFactory, LLMProvider
        import os
        self.llm_provider = llm_provider or os.getenv('ARTEMIS_LLM_PROVIDER', 'openai')
        self.llm_model = llm_model or os.getenv('ARTEMIS_LLM_MODEL')
        provider_enum = LLMProvider.OPENAI if self.llm_provider == 'openai' else LLMProvider.ANTHROPIC
        self.llm = LLMClientFactory.create(provider_enum)
        self.llm_client = self.llm
        self.doc_reader = DocumentReader(verbose=self.verbose)
        self.extraction_engine = ExtractionEngine(self.llm, verbose=self.verbose)
        self.converter = RequirementsConverter(verbose=self.verbose)
        self.prompt_integration = PromptManagerIntegration(self.llm, rag=rag, verbose=self.verbose)
        self.ai_integration = AIServiceIntegration(self.llm, rag=rag, ai_service=ai_service, logger=logger, verbose=self.verbose)

    def parse_requirements_file(self, input_file: str, project_name: Optional[str]=None, output_format: str='yaml') -> StructuredRequirements:
        """
        Parse requirements and return StructuredRequirements

        WHY: Main entry point for file-based parsing
        RESPONSIBILITY: Read file and delegate to internal parsing

        Args:
            input_file: Path to requirements document
            project_name: Name of the project (extracted from file if not provided)
            output_format: Output format (yaml or json)

        Returns:
            StructuredRequirements object
        """
        return self._parse_and_return_structured(input_file, project_name, output_format)

    def parse_requirements_for_validation(self, task_title: str, task_description: str, adr_content: str='') -> Dict:
        """
        Parse requirements into format for validation system

        WHY: Validation system needs specific format
        RESPONSIBILITY: Extract validation criteria from requirements

        Returns:
            Dict with:
            - artifact_type: str
            - quality_criteria: Dict
            - functional_requirements: List
            - non_functional_requirements: List
        """
        combined = f'{task_title}\n\n{task_description}\n\n{adr_content}'
        prompt = f'Analyze these requirements and extract validation criteria.\n\nRequirements:\n{combined}\n\nExtract and return JSON:\n{{\n    "artifact_type": "code|notebook|ui|documentation|demo|visualization",\n    "quality_criteria": {{\n        "min_cells": <int>,\n        "requires_visualizations": <bool>,\n        "visualization_library": "<string>",\n        "data_source": "<string>",\n        "accessibility_required": <bool>,\n        "responsive_required": <bool>,\n        "min_test_coverage": <float>,\n        "requires_unit_tests": <bool>\n    }},\n    "functional_requirements": ["<requirement>", ...],\n    "non_functional_requirements": ["<requirement>", ...]\n}}\n'
        messages = [LLMMessage(role='system', content='You are a requirements analyst. Extract structured validation criteria.'), LLMMessage(role='user', content=prompt)]
        response = self.llm_client.complete(messages=messages, model=self.llm_model, temperature=0.3, response_format={'type': 'json_object'} if self.llm_provider == 'openai' else None)
        return json.loads(response.content)

    @wrap_exception(RequirementsParsingError, 'Failed to parse requirements file')
    def _parse_and_return_structured(self, input_file: str, project_name: Optional[str]=None, output_format: str='yaml') -> StructuredRequirements:
        """
        Parse requirements from a document file

        WHY: Internal method with exception wrapping
        RESPONSIBILITY: Execute complete parsing workflow

        Supports multiple formats:
        - PDF (.pdf)
        - Microsoft Word (.docx, .doc)
        - Microsoft Excel (.xlsx, .xls)
        - LibreOffice Writer (.odt)
        - LibreOffice Calc (.ods)
        - Plain Text (.txt)
        - Markdown (.md)
        - CSV (.csv)
        - HTML (.html)

        Args:
            input_file: Path to requirements document
            project_name: Name of the project (extracted from file if not provided)
            output_format: Output format (yaml or json)

        Returns:
            StructuredRequirements object
        """
        self.debug_trace('parse_requirements_file', input_file=input_file, project_name=project_name)
        self.log(f'📄 Reading requirements from: {input_file}')
        try:
            raw_requirements = self.doc_reader.read_document(input_file)
        except FileNotFoundError as e:
            raise RequirementsFileError(f'Requirements file not found: {input_file}', context={'input_file': input_file}, original_exception=e)
        except (ValueError, RuntimeError) as e:
            raise RequirementsFileError(f'Error reading requirements file: {str(e)}', context={'input_file': input_file, 'format': Path(input_file).suffix}, original_exception=e)
        if not project_name:
            project_name = Path(input_file).stem.replace('_', ' ').replace('-', ' ').title()
        self.log(f'🔍 Parsing requirements for project: {project_name}')
        structured_reqs = self._parse_with_llm(raw_requirements, project_name)
        self.log(f'✅ Parsed {len(structured_reqs.functional_requirements)} functional requirements')
        self.log(f'✅ Parsed {len(structured_reqs.non_functional_requirements)} non-functional requirements')
        self.log(f'✅ Identified {len(structured_reqs.use_cases)} use cases')
        self.log(f'✅ Identified {len(structured_reqs.stakeholders)} stakeholders')
        self.debug_dump_if_enabled('requirements_summary', 'Requirements Summary', {'functional': len(structured_reqs.functional_requirements), 'non_functional': len(structured_reqs.non_functional_requirements), 'use_cases': len(structured_reqs.use_cases), 'stakeholders': len(structured_reqs.stakeholders)})
        return structured_reqs

    def _parse_with_llm(self, raw_text: str, project_name: str) -> StructuredRequirements:
        """
        Use LLM to parse requirements from raw text

        WHY: Choose best parsing strategy
        RESPONSIBILITY: Try PromptManager first, fallback to multi-step

        First tries production-grade single-call extraction via PromptManager.
        Falls back to multi-step extraction if PromptManager unavailable.

        Multi-step extraction performs:
        1. Extract metadata and overview
        2. Extract functional requirements
        3. Extract non-functional requirements
        4. Extract use cases
        5. Extract data requirements
        6. Extract integration requirements
        7. Identify stakeholders, constraints, assumptions
        """
        self.log('🤖 Using LLM to structure requirements...')
        if self.prompt_integration.is_available():
            try:
                self.log('📝 Using PromptManager for structured extraction')
                llm_output = self.prompt_integration.parse_with_prompt_manager(raw_text, project_name)
                if llm_output.get('result') == 'Refuse':
                    raise RequirementsParsingError(f"LLM refused to parse requirements: {llm_output.get('reason')}", context={'missing_fields': llm_output.get('missing_fields', [])})
                structured_reqs = self.converter.convert_llm_output_to_structured_requirements(llm_output, project_name)
                self.log('✅ Successfully used PromptManager-based extraction')
                return structured_reqs
            except Exception as e:
                self.log(f'⚠️  PromptManager extraction failed: {e}')
                self.log('   Falling back to multi-step extraction')
        return self._multi_step_extraction(raw_text, project_name)

    def _multi_step_extraction(self, raw_text: str, project_name: str) -> StructuredRequirements:
        """
        Multi-step LLM extraction (legacy fallback)

        WHY: Fallback when PromptManager unavailable
        RESPONSIBILITY: Execute 7-step extraction process
        """
        self.log('📝 Using multi-step extraction (legacy mode)')
        overview = self.extraction_engine.extract_overview(raw_text, project_name)
        functional_reqs = self.extraction_engine.extract_functional_requirements(raw_text)
        non_functional_reqs = self.extraction_engine.extract_non_functional_requirements(raw_text)
        use_cases = self.extraction_engine.extract_use_cases(raw_text)
        data_reqs = self.extraction_engine.extract_data_requirements(raw_text)
        integration_reqs = self.extraction_engine.extract_integration_requirements(raw_text)
        stakeholders = self.extraction_engine.extract_stakeholders(raw_text)
        constraints = self.extraction_engine.extract_constraints(raw_text)
        assumptions = self.extraction_engine.extract_assumptions(raw_text)
        return StructuredRequirements(project_name=project_name, version='1.0', created_date=datetime.now().strftime('%Y-%m-%d'), executive_summary=overview.get('executive_summary'), business_goals=overview.get('business_goals', []), success_criteria=overview.get('success_criteria', []), stakeholders=stakeholders, constraints=constraints, assumptions=assumptions, functional_requirements=functional_reqs, non_functional_requirements=non_functional_reqs, use_cases=use_cases, data_requirements=data_reqs, integration_requirements=integration_reqs, glossary=overview.get('glossary', {}))

    def log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            
            logger.log(f'[RequirementsParser] {message}', 'INFO')