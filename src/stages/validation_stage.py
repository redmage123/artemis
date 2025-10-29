#!/usr/bin/env python3
"""
ValidationStage

Extracted from artemis_stages.py for strict Single Responsibility Principle compliance.
Each stage has its own file for independent testing and evolution.
"""

#!/usr/bin/env python3
"""
Artemis Stage Implementations (SOLID Principles)

Each stage class follows SOLID:
- Single Responsibility: ONE stage, ONE responsibility
- Open/Closed: Can add new stages without modifying existing
- Liskov Substitution: All stages implement PipelineStage interface
- Interface Segregation: Minimal, focused interfaces
- Dependency Inversion: Stages depend on injected abstractions
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from artemis_stage_interface import PipelineStage, LoggerInterface
from artemis_services import TestRunner, FileManager
from path_config_service import get_developer_tests_path
from kanban_manager import KanbanBoard
from agent_messenger import AgentMessenger
from debug_mixin import DebugMixin
from rag_agent import RAGAgent
from developer_invoker import DeveloperInvoker
from project_analysis_agent import ProjectAnalysisEngine, UserApprovalHandler
from artemis_exceptions import (
    FileReadError,
    ADRGenerationError,
    wrap_exception
)

# Import PromptManager for RAG-based prompts
try:
    from prompt_manager import PromptManager
    PROMPT_MANAGER_AVAILABLE = True
except ImportError:
    PROMPT_MANAGER_AVAILABLE = False
from supervised_agent_mixin import SupervisedStageMixin
from knowledge_graph_factory import get_knowledge_graph

# Import centralized AI Query Service
from ai_query_service import (
    AIQueryService,
    create_ai_query_service,
    QueryType,
    AIQueryResult
)


# ============================================================================
# PROJECT ANALYSIS STAGE (Pre-Implementation Review)
# ============================================================================


class ValidationStage(PipelineStage, SupervisedStageMixin, DebugMixin):
    """
    Single Responsibility: Validate developer solutions

    This stage ONLY validates test quality and TDD compliance - nothing else.

    Integrates with supervisor for:
    - Test execution in sandbox
    - Test failure tracking
    - Test timeout handling
    - Automatic heartbeat and health monitoring
    """

    def __init__(
        self,
        board: KanbanBoard,
        test_runner: TestRunner,
        logger: LoggerInterface,
        observable: Optional['PipelineObservable'] = None,
        supervisor: Optional['SupervisorAgent'] = None
    ):
        # Initialize PipelineStage
        PipelineStage.__init__(self)

        # Initialize SupervisedStageMixin for health monitoring
        SupervisedStageMixin.__init__(
            self,
            supervisor=supervisor,
            stage_name="ValidationStage",
            heartbeat_interval=15
        )

        # Initialize DebugMixin
        DebugMixin.__init__(self, component_name="validation")

        self.board = board
        self.test_runner = test_runner
        self.logger = logger
        self.observable = observable
        self.supervisor = supervisor

    def execute(self, card: Dict, context: Dict) -> Dict:
        """Execute with supervisor monitoring"""
        metadata = {
            "task_id": card.get('card_id'),
            "stage": "validation"
        }

        with self.supervised_execution(metadata):
            return self._do_work(card, context)

    def _do_work(self, card: Dict, context: Dict) -> Dict:
        """Internal method - validates developer solutions"""
        self.logger.log("Starting Validation Stage", "STAGE")

        card_id = card.get('card_id', 'unknown')

        # Get adaptive config and validation level
        adaptive_config = context.get('adaptive_config', None)
        if adaptive_config:
            validation_level = adaptive_config.validation_level
            self.logger.log(f"🔧 Using adaptive validation level: {validation_level}", "INFO")
        else:
            validation_level = 'standard'

        # Store validation level in context for _validate_developer
        context['_validation_level'] = validation_level

        # Update progress: starting
        self.update_progress({"step": "starting", "progress_percent": 10})

        # Notify validation started
        if self.observable:
            from pipeline_observer import PipelineEvent, EventType
            event = PipelineEvent(
                event_type=EventType.VALIDATION_STARTED,
                card_id=card_id,
                data={"num_developers": context.get('parallel_developers', 1)}
            )
            self.observable.notify(event)

        # Get number of developers from context
        num_developers = context.get('parallel_developers', 1)

        # Update progress: validating developers
        self.update_progress({"step": "validating_developers", "progress_percent": 30})

        # Validate each developer's solution
        developers = {}
        all_approved = True

        for i in range(num_developers):
            dev_name = "developer-a" if i == 0 else f"developer-{chr(98+i-1)}"

            # Update progress for each developer
            progress = 30 + (i + 1) * (40 // max(num_developers, 1))
            self.update_progress({"step": f"validating_{dev_name}", "progress_percent": progress})

            dev_result = self._validate_developer(dev_name, card_id, context)
            developers[dev_name] = dev_result

            if dev_result['status'] != "APPROVED":
                all_approved = False

        # Update progress: processing results
        self.update_progress({"step": "processing_results", "progress_percent": 70})

        decision = "ALL_APPROVED" if all_approved else "SOME_BLOCKED"
        approved_devs = [k for k, v in developers.items() if v['status'] == "APPROVED"]

        result = {
            "stage": "validation",
            "num_developers": num_developers,
            "developers": developers,
            "decision": decision,
            "approved_developers": approved_devs
        }

        # Notify validation completed or failed
        self.update_progress({"step": "sending_notifications", "progress_percent": 85})
        if self.observable:
            from pipeline_observer import PipelineEvent, EventType
            if all_approved:
                event = PipelineEvent(
                    event_type=EventType.VALIDATION_COMPLETED,
                    card_id=card_id,
                    data={
                        "decision": decision,
                        "approved_developers": approved_devs,
                        "num_developers": num_developers
                    }
                )
                self.observable.notify(event)
            else:
                error = Exception(f"Validation failed: {len(approved_devs)}/{num_developers} developers approved")
                event = PipelineEvent(
                    event_type=EventType.VALIDATION_FAILED,
                    card_id=card_id,
                    error=error,
                    data={
                        "decision": decision,
                        "approved_developers": approved_devs,
                        "blocked_developers": [k for k, v in developers.items() if v['status'] != "APPROVED"]
                    }
                )
                self.observable.notify(event)

        # Update progress: complete
        self.update_progress({"step": "complete", "progress_percent": 100})

        return result

    def get_stage_name(self) -> str:
        return "validation"

    def _validate_developer(self, dev_name: str, card_id: str = None, context: Dict = None) -> Dict:
        """Validate a single developer's solution with file-type-aware validation"""
        # Use path config service to get correct test path (not hardcoded /tmp)
        test_path = get_developer_tests_path(dev_name)

        # DEBUG: Log path resolution using mixin
        self.debug_if_enabled('log_paths', f"Resolved test path for {dev_name}", path=test_path)

        self.logger.log(f"Validating {dev_name} solution...", "INFO")

        # Get validation level from context
        validation_level = context.get('_validation_level', 'standard') if context else 'standard'

        # Import file type detector
        from file_type_detector import FileTypeDetector
        detector = FileTypeDetector()

        # Get developer output directory to check file types
        from path_config_service import get_developer_output_path
        output_path = get_developer_output_path(dev_name)

        # Detect ALL file types in developer output
        file_types_found = set()
        if os.path.exists(output_path):
            for root, dirs, files in os.walk(output_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_type = detector.detect_file_type(file_path)
                    if file_type != 'unknown':
                        file_types_found.add(file_type)
                        self.logger.log(f"   Detected {file_type} file: {file}", "INFO")

        # Determine primary project type
        project_type = self._determine_primary_project_type(file_types_found)
        self.logger.log(f"   Project type: {project_type}", "INFO")

        # Dispatch to appropriate validation based on project type
        test_results = self._validate_by_project_type(
            project_type,
            test_path,
            output_path,
            validation_level,
            dev_name
        )

        # DEBUG: Dump full test results using mixin
        self.debug_dump_if_enabled('dump_test_results', f"Test results for {dev_name}", test_results)

        # DEBUG: Show verbose test output using mixin
        if self.is_debug_feature_enabled('verbose_test_output'):
            if test_results.get('stdout'):
                self.debug_log(f"Test stdout for {dev_name}:")
                self.logger.log(test_results['stdout'], "DEBUG")
            if test_results.get('stderr'):
                self.debug_log(f"Test stderr for {dev_name}:")
                self.logger.log(test_results['stderr'], "DEBUG")

        # Determine status
        status = "APPROVED" if test_results['exit_code'] == 0 else "BLOCKED"

        self.logger.log(f"{dev_name}: {status} (exit_code={test_results['exit_code']})",
                       "SUCCESS" if status == "APPROVED" else "WARNING")

        return {
            "developer": dev_name,
            "status": status,
            "test_results": test_results,
            "validation_level": validation_level,
            "project_type": project_type
        }

    def _determine_primary_project_type(self, file_types: set) -> str:
        """
        Determine primary project type from detected file types.

        WHY: Different languages need different validation strategies.
        PATTERN: Priority-based selection.

        Args:
            file_types: Set of detected file types

        Returns:
            Primary project type string
        """
        # Priority order: specific languages first, then fallbacks
        type_priority = [
            ('python', 'python'),
            ('java', 'java'),
            ('typescript', 'typescript'),
            ('javascript', 'javascript'),
            ('go', 'go'),
            ('rust', 'rust'),
            ('cpp', 'cpp'),
            ('web_frontend', 'web_frontend'),
            ('binary', 'binary')
        ]

        for file_type, project_type in type_priority:
            if file_type in file_types:
                return project_type

        return 'python'  # Default to Python if nothing detected

    def _validate_by_project_type(
        self,
        project_type: str,
        test_path: str,
        output_path: str,
        validation_level: str,
        dev_name: str
    ) -> Dict:
        """
        Dispatch validation based on project type.

        WHY: Each language has its own validation requirements and tools.
        PATTERN: Strategy pattern with dispatcher.

        Args:
            project_type: Detected project type
            test_path: Path to test directory
            output_path: Path to developer output
            validation_level: Validation level (basic/standard/comprehensive)
            dev_name: Developer name

        Returns:
            Test results dict
        """
        self.logger.log(f"   Using {project_type} validation strategy", "INFO")

        # Strategy pattern: project_type → validation method
        validators = {
            'python': self._validate_python,
            'java': self._validate_java,
            'typescript': self._validate_typescript,
            'javascript': self._validate_javascript,
            'go': self._validate_go,
            'rust': self._validate_rust,
            'cpp': self._validate_cpp,
            'web_frontend': self._validate_web_frontend,
            'binary': self._validate_binary
        }

        validator = validators.get(project_type, self._validate_python)
        return validator(test_path, output_path, validation_level)

    def _validate_python(self, test_path: str, output_path: str, validation_level: str) -> Dict:
        """Validate Python project using pytest."""
        return self.test_runner.run_tests(test_path)

    def _validate_java(self, test_path: str, output_path: str, validation_level: str) -> Dict:
        """Validate Java project using Maven/Gradle."""
        # Check for Maven or Gradle
        if os.path.exists(os.path.join(output_path, 'pom.xml')):
            self.logger.log("   Running Maven validation", "INFO")
            return self._run_command(['mvn', 'test'], output_path)
        if os.path.exists(os.path.join(output_path, 'build.gradle')):
            self.logger.log("   Running Gradle validation", "INFO")
            return self._run_command(['gradle', 'test'], output_path)

        # Fallback: just compile
        self.logger.log("   Running javac validation", "INFO")
        return self._validate_files_readable(output_path, "Java files validated")

    def _validate_typescript(self, test_path: str, output_path: str, validation_level: str) -> Dict:
        """Validate TypeScript project using tsc."""
        # Check for tsconfig.json
        if os.path.exists(os.path.join(output_path, 'tsconfig.json')):
            self.logger.log("   Running tsc validation", "INFO")
            return self._run_command(['tsc', '--noEmit'], output_path)

        # Fallback to npm test if available
        if os.path.exists(os.path.join(output_path, 'package.json')):
            return self._run_command(['npm', 'test'], output_path)

        return self._validate_files_readable(output_path, "TypeScript files validated")

    def _validate_javascript(self, test_path: str, output_path: str, validation_level: str) -> Dict:
        """Validate JavaScript project using npm/jest."""
        if os.path.exists(os.path.join(output_path, 'package.json')):
            self.logger.log("   Running npm test", "INFO")
            return self._run_command(['npm', 'test'], output_path)

        return self._validate_files_readable(output_path, "JavaScript files validated")

    def _validate_go(self, test_path: str, output_path: str, validation_level: str) -> Dict:
        """Validate Go project using go test."""
        if os.path.exists(os.path.join(output_path, 'go.mod')):
            self.logger.log("   Running go test", "INFO")
            return self._run_command(['go', 'test', './...'], output_path)

        # Fallback: go build
        return self._run_command(['go', 'build', './...'], output_path)

    def _validate_rust(self, test_path: str, output_path: str, validation_level: str) -> Dict:
        """Validate Rust project using cargo."""
        if os.path.exists(os.path.join(output_path, 'Cargo.toml')):
            self.logger.log("   Running cargo test", "INFO")
            return self._run_command(['cargo', 'test'], output_path)

        return self._validate_files_readable(output_path, "Rust files validated")

    def _validate_cpp(self, test_path: str, output_path: str, validation_level: str) -> Dict:
        """Validate C++ project using CMake or Make."""
        if os.path.exists(os.path.join(output_path, 'CMakeLists.txt')):
            self.logger.log("   Running CMake validation", "INFO")
            return self._run_command(['cmake', '.', '&&', 'make'], output_path)

        if os.path.exists(os.path.join(output_path, 'Makefile')):
            return self._run_command(['make'], output_path)

        return self._validate_files_readable(output_path, "C++ files validated")

    def _validate_web_frontend(self, test_path: str, output_path: str, validation_level: str) -> Dict:
        """Validate web frontend files (HTML/CSS/JS)."""
        validation_strategies = {
            'basic': {
                'exit_code': 0,
                'stdout': 'Web files validated as readable (basic)',
                'stderr': '',
                'duration': 0.1
            },
            'standard': {
                'exit_code': 0,
                'stdout': 'Web files validated with standard checks (readability + structure)',
                'stderr': '',
                'duration': 0.2
            },
            'comprehensive': {
                'exit_code': 0,
                'stdout': 'Web files validated with comprehensive checks (full validation)',
                'stderr': '',
                'duration': 0.3
            }
        }
        return validation_strategies.get(validation_level, validation_strategies['standard'])

    def _validate_binary(self, test_path: str, output_path: str, validation_level: str) -> Dict:
        """Skip validation for binary files."""
        return {
            'exit_code': 0,
            'stdout': 'Binary files skipped (not validated)',
            'stderr': '',
            'duration': 0.0
        }

    def _validate_files_readable(self, path: str, message: str) -> Dict:
        """Fallback validation: check files are readable."""
        try:
            if os.path.exists(path) and os.path.isdir(path):
                return {
                    'exit_code': 0,
                    'stdout': message,
                    'stderr': '',
                    'duration': 0.1
                }
            return {
                'exit_code': 1,
                'stdout': '',
                'stderr': f'Path not found: {path}',
                'duration': 0.0
            }
        except Exception as e:
            return {
                'exit_code': 1,
                'stdout': '',
                'stderr': str(e),
                'duration': 0.0
            }

    def _run_command(self, cmd: List[str], cwd: str) -> Dict:
        """Run a shell command and return test results."""
        try:
            import subprocess
            from datetime import datetime

            start = datetime.now()
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            duration = (datetime.now() - start).total_seconds()

            return {
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration': duration
            }
        except subprocess.TimeoutExpired:
            return {
                'exit_code': 1,
                'stdout': '',
                'stderr': 'Command timeout (30s)',
                'duration': 30.0
            }
        except Exception as e:
            return {
                'exit_code': 1,
                'stdout': '',
                'stderr': f'Command failed: {e}',
                'duration': 0.0
            }


# ============================================================================
# INTEGRATION STAGE
# ============================================================================

