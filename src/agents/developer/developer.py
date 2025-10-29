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
from artemis_exceptions import LLMClientError, DeveloperExecutionError, create_wrapped_exception
from agents.developer.file_manager import FileManager
from agents.developer.test_runner_wrapper import DeveloperTestRunner
from agents.developer.report_generator import ReportGenerator
from agents.developer.rag_integration import RAGIntegration
from agents.developer.llm_client_wrapper import LLMClientWrapper
from agents.developer.tdd_phases import TDDPhases
from agents.developer.models import WorkflowType, WorkflowContext
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

    def __init__(self, developer_name: str, developer_type: str,
        llm_provider: str='openai', llm_model: Optional[str]=None, logger:
        Optional[LoggerInterface]=None, rag_agent=None, ai_service:
        Optional['AIQueryService']=None):
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
        DebugMixin.__init__(self, component_name='developer')
        self.developer_name = developer_name
        self.developer_type = developer_type
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.logger = logger
        self.debug_log('Developer initialized', name=developer_name, type=
            developer_type, provider=llm_provider)
        self.llm_client = self._create_llm_client()
        self.prompt_manager = self._initialize_prompt_manager(rag_agent)
        self.ai_service = self._initialize_ai_service(ai_service, rag_agent)
        self.retry_coordinator = self._initialize_retry_coordinator()
        self.file_manager = FileManager(logger=logger)
        self.test_runner = DeveloperTestRunner(logger=logger)
        self.report_generator = ReportGenerator(developer_name=
            developer_name, developer_type=developer_type, llm_provider=
            llm_provider)
        self.rag_integration = RAGIntegration(developer_name=developer_name,
            developer_type=developer_type, logger=logger, prompt_manager=
            self.prompt_manager)
        self.llm_wrapper = LLMClientWrapper(llm_client=self.llm_client,
            developer_name=developer_name, developer_type=developer_type,
            llm_provider=llm_provider, llm_model=llm_model, logger=logger)
        self.tdd_phases = TDDPhases(file_manager=self.file_manager,
            test_runner=self.test_runner, llm_wrapper=self.llm_wrapper,
            logger=logger, retry_coordinator=self.retry_coordinator)
        self._log_info(f'✅ {developer_name} initialized with {llm_provider}')

    def execute(self, task_title: str, task_description: str, adr_content:
        str, adr_file: str, output_dir: Path, developer_prompt_file: str,
        card_id: str='', rag_agent=None, parsed_requirements: Optional[Dict
        ]=None) ->Dict:
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
        self.debug_trace('execute', task_title=task_title, developer=self.
            developer_name, card_id=card_id)
        context = self._setup_execution_context(task_title,
            task_description, adr_content, output_dir,
            developer_prompt_file, card_id, rag_agent)
        strategy = self._select_workflow_strategy(task_title,
            task_description, parsed_requirements)
        self._log_info(
            f'📋 {self.developer_name} using {strategy.workflow.value.upper()} workflow'
            )
        try:
            results = self._execute_workflow(strategy, task_title,
                task_description, adr_content, output_dir, context)
            solution_report = self.report_generator.finalize_solution_report(
                results, output_dir)
            self.debug_dump_if_enabled('solution', 'Solution Report', {
                'workflow': strategy.workflow.value, 'num_files': len(
                results.get('implementation_files', results.get('green', {}
                ).get('implementation_files', [])))})
            return solution_report
        except Exception as e:
            self._log_error(f'❌ {self.developer_name} workflow failed: {e}')
            raise create_wrapped_exception(e, DeveloperExecutionError,
                f'Developer {self.developer_name} workflow failed', {
                'developer_name': self.developer_name, 'developer_type':
                self.developer_type, 'task_title': task_title, 'card_id':
                card_id})

    def _execute_workflow(self, strategy, task_title, task_description,
        adr_content, output_dir, context):
        """Execute workflow based on strategy - Strategy Pattern"""
        if strategy.workflow == WorkflowType.TDD:
            return self._execute_tdd_workflow(task_title, task_description,
                adr_content, output_dir, context)
        return self._execute_quality_driven_workflow(task_title,
            task_description, adr_content, output_dir, context)

    def _execute_tdd_workflow(self, task_title, task_description,
        adr_content, output_dir, context):
        """
        Execute TDD workflow: RED → GREEN → REFACTOR

        Delegates to TDDPhases orchestrator
        """
        red_results = self.tdd_phases.execute_red_phase(task_title,
            task_description, adr_content, output_dir, context)
        green_results = self.tdd_phases.execute_green_phase(task_title,
            task_description, adr_content, output_dir, context, red_results)
        refactor_results = self.tdd_phases.execute_refactor_phase(task_title,
            output_dir, context, green_results)
        return {'red': {'test_files': red_results.files, 'test_results':
            red_results.test_results}, 'green': {'implementation_files':
            green_results.files, 'test_results': green_results.test_results
            }, 'refactor': {'refactored_files': refactor_results.files,
            'test_results': refactor_results.test_results}}

    def _execute_quality_driven_workflow(self, task_title, task_description,
        adr_content, output_dir, context):
        """
        Execute quality-driven workflow: Direct implementation with validation

        For notebooks, demos, presentations - prioritize comprehensive output
        """
        self._log_info(
            '🎯 QUALITY-DRIVEN workflow: Generating comprehensive implementation...'
            )
        rag_examples = self.rag_integration.query_rag_for_examples(self.rag,
            task_title, task_description) if hasattr(self, 'rag') else ''
        prompt = self._build_quality_prompt(task_title, task_description,
            adr_content, context, rag_examples)
        response = self.llm_wrapper.call_llm(prompt)
        implementation = self.llm_wrapper.parse_implementation(response.content
            )
        validation_result = self._validate_import_consistency(implementation)
        if not validation_result['valid']:
            self._log_warning('⚠️ Import consistency issues detected:')
            for issue in validation_result['issues']:
                self._log_warning(f'  {issue}')
            self._log_info('📋 Module exports detected:')
            for module, exports in validation_result['module_exports'].items():
                self._log_info(f"  {module}: {', '.join(exports)}")
            self._log_warning(
                '⚠️ Files will be written but may fail validation tests')
        else:
            self._log_info('✅ Import consistency validation passed')
        files_written = self.file_manager.write_implementation_files(
            implementation, output_dir)
        self._log_info(
            f'✅ Quality-driven workflow complete: {len(files_written)} files written'
            )
        return {'implementation_files': implementation.get(
            'implementation_files', []), 'test_files': implementation.get(
            'test_files', [])}

    def _setup_execution_context(self, task_title, task_description,
        adr_content, output_dir, developer_prompt_file, card_id, rag_agent):
        """
        Setup execution context by gathering all necessary data

        Returns:
            Dict containing all context data
        """
        self._log_info(f'🚀 {self.developer_name} starting workflow...')
        output_dir.mkdir(parents=True, exist_ok=True)
        kg_context = self._query_kg_context(task_title, task_description)
        code_review_feedback = None
        if rag_agent and card_id:
            code_review_feedback = (self.rag_integration.
                query_code_review_feedback(rag_agent, card_id))
        developer_prompt = self._get_developer_prompt(task_title,
            adr_content, code_review_feedback, rag_agent, developer_prompt_file
            )
        example_slides = None
        if 'slide' in task_description.lower(
            ) or 'html' in task_description.lower():
            example_slides = self.file_manager.load_example_slides(adr_content)
        refactoring_instructions = None
        if rag_agent:
            language = self._detect_language_from_task(task_description)
            refactoring_instructions = (self.rag_integration.
                query_refactoring_instructions(rag_agent, task_title, language)
                )
        return {'kg_context': kg_context, 'code_review_feedback':
            code_review_feedback, 'developer_prompt': developer_prompt,
            'example_slides': example_slides, 'refactoring_instructions':
            refactoring_instructions}

    def _select_workflow_strategy(self, task_title, task_description,
        parsed_requirements):
        """
        Select workflow strategy based on requirements

        Uses RequirementsDrivenValidator if available, else task type detection
        """
        try:
            from requirements_driven_validator import RequirementsDrivenValidator
            validator = RequirementsDrivenValidator(self.logger)
            return validator.analyze_requirements(task_title,
                task_description, parsed_requirements)
        except ImportError:
            from agents.developer.models import WorkflowType, TaskType, ExecutionStrategy
            task_type = self._detect_task_type(task_title, task_description)
            workflow = WorkflowType.QUALITY_DRIVEN if task_type in [TaskType
                .NOTEBOOK, TaskType.PRESENTATION, TaskType.HTML
                ] else WorkflowType.TDD


            class SimpleStrategy:

                def __init__(self, workflow, artifact_type):
                    self.workflow = workflow
                    self.artifact_type = artifact_type
            return SimpleStrategy(workflow, task_type)

    def _detect_task_type(self, task_title, task_description):
        """Detect task type from title and description"""
        from agents.developer.models import TaskType
        combined = f'{task_title} {task_description}'.lower()
        if any(kw in combined for kw in ['jupyter', 'notebook', 'ipynb']):
            return TaskType.NOTEBOOK
        if any(kw in combined for kw in ['slide', 'presentation', 'demo']):
            return TaskType.PRESENTATION
        if any(kw in combined for kw in ['html', 'webpage']):
            return TaskType.HTML
        return TaskType.CODE

    def _detect_language_from_task(self, task_description: str) ->str:
        """
        Detect programming language from task description

        Args:
            task_description: Task description text

        Returns:
            Detected language string (python, java, javascript, go, rust)
            Defaults to "python" if not detected
        """
        description_lower = task_description.lower()
        language_keywords = {'java': ['java', 'spring', 'maven', 'gradle',
            'springboot', 'spring boot'], 'javascript': ['javascript',
            'typescript', 'node', 'react', 'nodejs', 'node.js', 'angular',
            'vue', 'npm', 'yarn', 'jest', 'webpack'], 'go': ['golang',
            'go '], 'rust': ['rust', 'cargo'], 'python': ['python',
            'django', 'flask', 'fastapi', 'pytest', 'pip']}
        for language, keywords in language_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return language
        return 'python'

    def _query_kg_context(self, task_title, task_description):
        """Query KG for similar implementations"""
        if not self.ai_service:
            return None
        try:
            from ai_query_service import QueryType
            result = self.ai_service.query(query_type=QueryType.
                SIMILAR_IMPLEMENTATIONS, query_text=
                f'{task_title}: {task_description}', context={'task_title':
                task_title})
            return result.data if result.success else None
        except Exception as e:
            self._log_warning(f'KG query failed: {e}')
            return None

    def _get_developer_prompt(self, task_title, adr_content,
        code_review_feedback, rag_agent, prompt_file):
        """Get developer prompt (RAG or file-based)"""
        if self.prompt_manager and rag_agent:
            return self.rag_integration.get_developer_prompt_from_rag(
                task_title, adr_content, code_review_feedback, rag_agent)
        return self.file_manager.read_developer_prompt(prompt_file)

    def _build_quality_prompt(self, task_title, task_description,
        adr_content, context, rag_examples):
        """Build prompt for quality-driven workflow"""
        return f"""
Task: {task_title}
Description: {task_description}

Architecture Decision:
{adr_content}

{context.get('developer_prompt', '')}

{rag_examples}

Generate a comprehensive, high-quality implementation following all guidelines.

CRITICAL CONSISTENCY REQUIREMENTS:
1. **Import Consistency**: Every imported function/class MUST be defined in the imported module
   - Before importing from a module, ensure that module exports those exact names
   - Example: If you write "from database import get_user, validate_password"
            then database/__init__.py MUST define both get_user() and validate_password()

2. **Complete Implementation**: NO placeholder functions or missing implementations
   - All functions must be fully implemented with working logic
   - All helper functions must be defined before use
   - All dependencies must be included in the generated files

3. **Self-Contained Code**: Generated code must work without external dependencies
   - If a function is called, it must be defined somewhere in your generated files
   - If a module is imported, it must be in your generated files or Python stdlib

4. **Test Compatibility**: Tests must import only what implementation provides
   - Review all test imports and ensure implementation files export those names
   - Ensure test function calls match implementation function signatures

LOGIC CORRECTNESS REQUIREMENTS:
5. **Edge Case Handling**: Handle ALL edge cases explicitly
   - Empty inputs (empty strings, empty lists, None values)
   - Boundary conditions (zero, negative numbers, maximum values)
   - Invalid data types or formats
   - Example: Always check if user is None before accessing user properties

6. **Error Handling**: Implement comprehensive error handling
   - Use try/except blocks for operations that can fail (I/O, parsing, external calls)
   - Provide meaningful error messages
   - Don't silently fail - log or raise exceptions appropriately
   - Handle timeouts and resource exhaustion

7. **Logic Flow**: Ensure correct control flow
   - Early returns for invalid inputs (guard clauses)
   - Proper boolean logic (avoid double negatives)
   - Clear conditional branches
   - No unreachable code

8. **Data Validation**: Validate all inputs
   - Type checking where appropriate
   - Range validation for numbers
   - Format validation for strings (email, phone, etc.)
   - Length limits for collections

9. **Test Quality**: Write comprehensive, meaningful tests
   - Happy path: Test normal/expected behavior
   - Error cases: Test error handling
   - Edge cases: Test boundary conditions
   - Integration: Test components working together
   - Aim for >80% code coverage

VALIDATION CHECKLIST (verify before returning):
☐ All imports in implementation files have matching exports
☐ All imports in test files have matching exports in implementation
☐ No undefined functions are called
☐ No placeholder comments (TODO, FIXME, etc.)
☐ All async functions properly use await for async calls
☐ All error cases are handled with try/except or validation
☐ Edge cases (None, empty, invalid) are explicitly handled
☐ Input validation is present for all public functions
☐ Tests cover happy path, error cases, and edge cases
☐ Error messages are clear and actionable

IMPORTANT: Return your response as a JSON object with the following structure:
{{
  "implementation_files": [
    {{
      "path": "relative/path/to/file.py",
      "content": "file content here..."
    }}
  ],
  "test_files": [
    {{
      "path": "tests/test_file.py",
      "content": "test content here..."
    }}
  ]
}}

Include all necessary files to complete the task. Each file must have a "path" and "content" field.
"""

    def _resolve_import_module(self, node_level: int, import_module: str, current_dir: str) ->str:
        """
        Resolve module path for relative/absolute imports.

        WHY: Centralize complex import resolution logic to avoid nested ifs.
        PATTERN: Early returns for simple cases.

        Args:
            node_level: Import level (0=absolute, 1+=relative)
            import_module: Module being imported
            current_dir: Current directory path

        Returns:
            Resolved module path
        """
        from pathlib import Path

        # Absolute imports
        if node_level == 0:
            return import_module

        # Level 1 relative imports with module
        if node_level == 1 and import_module:
            return f'{current_dir}.{import_module}' if current_dir else import_module

        # Level 1 relative imports without module
        if node_level == 1 and not import_module:
            return current_dir if current_dir else None

        # Level 2+ relative imports (parent directory)
        parent = str(Path(current_dir).parent) if current_dir else None
        return f'{parent}.{import_module}' if parent and import_module else parent

    def _process_assign_exports(self, node: 'ast.Assign', exports: set) -> None:
        """
        Process assignment nodes to extract __all__ exports.

        WHY: Extract nested logic for handling __all__ assignments.
        PATTERN: Early return for non-matching targets.

        Args:
            node: AST Assign node
            exports: Set to add exports to
        """
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == '__all__':
                exports.add('__all__')
                return

    def _process_import_from_exports(self, node: 'ast.ImportFrom', path: str, exports: set) -> None:
        """
        Process ImportFrom nodes in __init__.py to extract re-exported names.

        WHY: Extract nested logic for handling re-exports in package __init__.py files.
        PATTERN: Early return for non-__init__.py files.

        Args:
            node: AST ImportFrom node
            path: File path being processed
            exports: Set to add exports to
        """
        if not path.endswith('__init__.py'):
            return

        for alias in node.names:
            if alias.name != '*':
                exports.add(alias.asname if alias.asname else alias.name)

    def _determine_module_name(self, path: str) -> 'Optional[str]':
        """
        Determine Python module name from file path.

        WHY: Extract module name determination logic to avoid elif chain.
        PATTERN: Early returns for clear control flow.

        Args:
            path: File path to determine module name for

        Returns:
            Module name string or None if not a module
        """
        from pathlib import Path

        # Test files don't have module names
        if path.startswith('tests/'):
            return None

        path_obj = Path(path)

        # __init__.py files use parent directory as module name
        if path_obj.name == '__init__.py':
            return str(path_obj.parent) if path_obj.parent != Path('.') else None

        # Python files use path as module name
        if path_obj.suffix == '.py':
            parts = path_obj.with_suffix('').parts
            return '.'.join(parts)

        # Non-Python files don't have module names
        return None

    def _validate_import_consistency(self, generated_code: Dict) ->Dict:
        """
        Validate that all imports have matching exports

        WHY: Catches import inconsistencies before files are written,
             preventing ValidationStage failures due to missing functions.

        IMPROVEMENTS:
        - Handles relative imports (from .module import X)
        - Resolves __init__.py re-exports
        - Better distinguishes between callables and variables

        Args:
            generated_code: Dict with 'implementation_files' and 'test_files'

        Returns:
            Dict with validation results and issues found
        """
        import ast
        from pathlib import Path
        issues = []
        all_files = generated_code.get('implementation_files', []
            ) + generated_code.get('test_files', [])
        file_map = {}
        module_exports = {}
        for file_dict in all_files:
            path = file_dict.get('path', '')
            content = file_dict.get('content', '')
            module_name = self._determine_module_name(path)

            try:
                tree = ast.parse(content)
                file_map[path] = module_name, content, tree
            except SyntaxError:
                issues.append(
                    f'⚠️ Syntax error in {path} - cannot validate imports')
                file_map[path] = module_name, content, None
                continue
        for path, (module_name, content, tree) in file_map.items():
            if not module_name or not tree:
                continue
            exports = set()
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    exports.add(node.name)
                    continue

                if isinstance(node, ast.ClassDef):
                    exports.add(node.name)
                    continue

                if isinstance(node, ast.Assign):
                    self._process_assign_exports(node, exports)
                    continue

                if isinstance(node, ast.ImportFrom):
                    self._process_import_from_exports(node, path, exports)
                    continue
            base_module = module_name.split('.')[0]
            module_exports.setdefault(module_name, set()).update(exports)
            if '.' in module_name:
                module_exports.setdefault(base_module, set()).update(exports)
        for path, (module_name, content, tree) in file_map.items():
            if not tree:
                continue
            current_dir = str(Path(path).parent) if Path(path).parent != Path(
                '.') else ''
            for node in tree.body:
                if not isinstance(node, ast.ImportFrom):
                    continue

                import_module = node.module
                resolved_module = self._resolve_import_module(
                    node.level, import_module, current_dir)

                if not resolved_module or resolved_module not in module_exports:
                    continue

                for alias in node.names:
                    name = alias.name
                    if name == '*':
                        continue

                    if name in module_exports[resolved_module]:
                        continue

                    # Check base module as fallback
                    base_module = resolved_module.split('.')[0]
                    if base_module in module_exports and name in module_exports[base_module]:
                        continue

                    # Name not found - add issue
                    available = sorted(module_exports[resolved_module])
                    issues.append(
                        f"""❌ {path}: imports '{name}' from '{import_module or '(relative)'}' but '{resolved_module}' doesn't export '{name}'
   Available in '{resolved_module}': {', '.join(available) if available else 'none'}"""
                    )
        return {'valid': len(issues) == 0, 'issues': issues,
            'module_exports': {k: sorted(list(v)) for k, v in
            module_exports.items()}}

    def _create_llm_client(self):
        """Create LLM client with error handling"""
        try:
            llm_client = create_llm_client(self.llm_provider)
            return llm_client
        except Exception as e:
            self._log_error(f'❌ Failed to initialize LLM client: {e}')
            raise create_wrapped_exception(e, LLMClientError,
                f'Failed to initialize LLM client for {self.developer_name}',
                {'developer_name': self.developer_name, 'llm_provider':
                self.llm_provider})

    def _initialize_prompt_manager(self, rag_agent):
        """Initialize PromptManager with early returns"""
        if not PROMPT_MANAGER_AVAILABLE:
            return None
        if not rag_agent:
            return None
        try:
            manager = PromptManager(rag_agent, verbose=False)
            self._log_info('✅ Prompt manager initialized (RAG-based prompts)')
            return manager
        except Exception as e:
            self._log_warning(f'⚠️  Could not initialize prompt manager: {e}')
            return None

    def _initialize_ai_service(self, ai_service, rag_agent):
        """Initialize AI Query Service with early returns"""
        if not AI_QUERY_SERVICE_AVAILABLE:
            return None
        if ai_service:
            self._log_info('✅ Using provided AI Query Service')
            return ai_service
        try:
            service = create_ai_query_service(llm_client=self.llm_client,
                rag=rag_agent, logger=self.logger, verbose=False)
            self._log_info('✅ AI Query Service initialized (KG-First enabled)')
            return service
        except Exception as e:
            self._log_warning(f'⚠️  Could not initialize AI Query Service: {e}'
                )
            return None

    def _initialize_retry_coordinator(self):
        """Initialize Retry Coordinator with early returns"""
        if not RETRY_COORDINATOR_AVAILABLE:
            return None
        try:
            max_retries = int(os.getenv('ARTEMIS_MAX_VALIDATION_RETRIES', '3'))
            acceptance_threshold = float(os.getenv(
                'ARTEMIS_CONFIDENCE_THRESHOLD', '0.85'))
            coordinator = RetryCoordinator(logger=self.logger, max_retries=
                max_retries, acceptance_threshold=acceptance_threshold)
            self._log_info(
                f'✅ Retry Coordinator initialized (max={max_retries}, threshold={acceptance_threshold:.2f})'
                )
            return coordinator
        except Exception as e:
            self._log_warning(
                f'⚠️  Could not initialize Retry Coordinator: {e}')
            return None

    def _log_info(self, message: str):
        """Log info message"""
        if self.logger:
            self.logger.log(message, 'INFO')

    def _log_warning(self, message: str):
        """Log warning message"""
        if self.logger:
            self.logger.log(message, 'WARNING')

    def _log_error(self, message: str):
        """Log error message"""
        if self.logger:
            self.logger.log(message, 'ERROR')


__all__ = ['Developer']
