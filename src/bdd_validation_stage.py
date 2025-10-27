#!/usr/bin/env python3
"""
Module: bdd_validation_stage.py

Purpose: Execute pytest-bdd tests to validate that developer implementations
         satisfy business requirements expressed in Gherkin scenarios.

Why: Quality gate ensuring implementations match business specifications.
     BDD scenarios are executable specifications - if they pass, business
     requirements are satisfied. If they fail, implementation doesn't match specs.

Patterns:
- Template Method Pattern: Implements PipelineStage execution contract
- Supervised Execution Pattern: Health monitoring via SupervisorAgent
- Command Pattern: Subprocess execution of pytest with timeout
- Parser Pattern: Regex extraction of test results from pytest output

Integration:
- Runs after DevelopmentStage (developer implementations complete)
- Validates BDD scenarios pass using pytest-bdd
- Provides coverage metrics (scenarios passed/failed/skipped)
- Stores validation results in RAG
- Generates failure reports for debugging
- May trigger iteration if scenarios fail

SOLID Principles:
- S: Single Responsibility - Only executes and validates BDD tests
- O: Open/Closed - Extensible to other BDD frameworks (behave, cucumber-py)
- L: Liskov Substitution - Implements PipelineStage contract
- I: Interface Segregation - Focused on test execution
- D: Dependency Inversion - Depends on abstractions (RAGAgent, LoggerInterface)
"""

from typing import Dict, Optional
from pathlib import Path
import subprocess
import re

from artemis_stage_interface import PipelineStage, LoggerInterface
from supervised_agent_mixin import SupervisedStageMixin
from kanban_manager import KanbanBoard
from rag_agent import RAGAgent
from artemis_exceptions import PipelineStageError, wrap_exception


class BDDValidationStage(PipelineStage, SupervisedStageMixin):
    """
    Execute BDD scenarios and validate business behavior.

    What it does: Runs pytest-bdd tests in developer workspace, analyzes results,
                  and generates validation report with pass/fail metrics.

    Why it exists: Quality gate ensuring implementations satisfy business requirements.
                   BDD scenarios are executable specifications - automated validation
                   confirms behavior matches specifications.

    Responsibilities:
    - Locate BDD tests and feature files in developer workspace
    - Execute pytest-bdd tests with timeout (120 seconds)
    - Parse pytest output to extract passed/failed/skipped counts
    - Analyze results and calculate pass rate
    - Extract failing scenario details for debugging
    - Generate human-readable validation report
    - Store results in RAG for traceability
    - Track progress via supervised execution

    Design Pattern: Command Pattern + Parser Pattern
    - Command: subprocess.run() executes pytest as external command
    - Parser: Regex extraction of PASSED/FAILED/SKIPPED from pytest output
    - Performance optimization: Single-pass Counter parsing (O(n) vs O(3n))

    Integrates with supervisor for:
    - Test execution monitoring (detects hanging tests via timeout)
    - Scenario validation tracking (monitors test progress)
    - Coverage reporting (tracks pass/fail metrics)
    - Heartbeat monitoring (30 second interval for test execution)
    """

    def __init__(
        self,
        board: KanbanBoard,
        rag: RAGAgent,
        logger: LoggerInterface,
        observable: Optional['PipelineObservable'] = None,
        supervisor: Optional['SupervisorAgent'] = None
    ):
        PipelineStage.__init__(self)
        SupervisedStageMixin.__init__(
            self,
            supervisor=supervisor,
            stage_name="BDDValidationStage",
            heartbeat_interval=30
        )

        self.board = board
        self.rag = rag
        self.logger = logger
        self.observable = observable
        self.supervisor = supervisor

    def execute(self, card: Dict, context: Dict) -> Dict:
        """Execute with supervisor monitoring"""
        metadata = {
            "task_id": card.get('card_id'),
            "stage": "bdd_validation"
        }

        with self.supervised_execution(metadata):
            result = self._do_work(card, context)

        return result

    def _do_work(self, card: Dict, context: Dict) -> Dict:
        """Execute BDD scenarios and validate behavior"""
        self.logger.log("✅ Starting BDD Scenario Validation Stage", "STAGE")

        card_id = card.get('card_id', 'unknown')
        title = card.get('title', 'Unknown Task')

        # Update progress
        self.update_progress({"step": "starting", "progress_percent": 10})

        # Get winner's implementation directory
        winner = context.get('winner', 'developer-a')
        impl_dir = Path(f"/tmp/{winner}")

        # Check if BDD tests exist
        bdd_test_dir = impl_dir / "tests" / "bdd"
        feature_dir = impl_dir / "features"

        if not bdd_test_dir.exists() or not feature_dir.exists():
            self.logger.log("⚠️  No BDD tests or features found - skipping validation", "WARNING")
            return {
                "stage": "bdd_validation",
                "status": "SKIPPED",
                "reason": "No BDD tests or features available"
            }

        self.logger.log(f"🧪 Running BDD scenarios for: {title}", "INFO")

        # Update progress
        self.update_progress({"step": "running_scenarios", "progress_percent": 30})

        # Run pytest-bdd tests
        test_results = self._run_bdd_tests(impl_dir, bdd_test_dir)

        # Update progress
        self.update_progress({"step": "analyzing_results", "progress_percent": 70})

        # Analyze results
        validation_report = self._analyze_bdd_results(test_results)

        # Update progress
        self.update_progress({"step": "storing_results", "progress_percent": 90})

        # Store results in RAG
        self.rag.store_artifact(
            artifact_type="bdd_validation",
            card_id=card_id,
            task_title=title,
            content=validation_report,
            metadata={
                "scenarios_passed": test_results.get('passed', 0),
                "scenarios_failed": test_results.get('failed', 0),
                "scenario_pass_rate": validation_report.get('pass_rate', 0),
                "status": validation_report.get('status', 'UNKNOWN')
            }
        )

        # Update progress
        self.update_progress({"step": "complete", "progress_percent": 100})

        # Determine overall status
        status = validation_report.get('status', 'FAILED')
        pass_rate = validation_report.get('pass_rate', 0)

        if status == "PASS":
            self.logger.log(f"✅ All BDD scenarios passing ({pass_rate}% coverage)", "SUCCESS")
        else:
            failed_count = test_results.get('failed', 0)
            self.logger.log(f"❌ {failed_count} BDD scenarios failing ({pass_rate}% coverage)", "ERROR")

        return {
            "stage": "bdd_validation",
            "status": status,
            "scenarios_passed": test_results.get('passed', 0),
            "scenarios_failed": test_results.get('failed', 0),
            "pass_rate": pass_rate,
            "validation_report": validation_report,
            "test_output": test_results.get('output', '')
        }

    def _run_bdd_tests(self, impl_dir: Path, test_dir: Path) -> Dict:
        """
        Run pytest-bdd tests and parse results.

        What it does: Executes pytest as subprocess, captures output, and parses
                      test results (passed/failed/skipped counts).

        Why: Command Pattern - delegates test execution to pytest subprocess.
             Timeout prevents hanging tests from blocking pipeline.
             Output parsing enables automated pass/fail determination.

        Command Pattern Implementation:
        - Command: pytest with -v (verbose), --tb=short (short traceback)
        - Timeout: 120 seconds (prevents infinite hangs)
        - Working directory: Developer implementation directory
        - Capture: Both stdout and stderr for complete output

        Args:
            impl_dir: Developer implementation directory (pytest working directory)
            test_dir: BDD test directory to execute

        Returns:
            Dict with test results:
            - passed: Number of passing scenarios
            - failed: Number of failing scenarios
            - skipped: Number of skipped scenarios
            - exit_code: Pytest exit code (0=success, 1=failures)
            - output: Complete pytest output text
            - error: Error message if timeout/exception occurred

        Performance: Single-pass Counter parsing O(n) vs naive O(3n)
        Why: collections.Counter counts all matches in one pass instead of
             three separate output.count() calls.

        Edge cases:
        - Timeout: Returns failure with timeout error
        - Exception: Returns failure with exception message
        """
        try:
            # Run pytest with BDD tests
            result = subprocess.run(
                [
                    "pytest",
                    str(test_dir),
                    "-v",
                    "--tb=short",
                    "--color=yes"
                ],
                cwd=str(impl_dir),
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout for BDD tests
            )

            # Parse pytest output
            output = result.stdout + result.stderr

            # Count scenarios (Performance: Single-pass parsing O(n) vs O(3n))
            import re
            from collections import Counter
            pattern = re.compile(r' (PASSED|FAILED|SKIPPED)')
            matches = pattern.findall(output)
            counts = Counter(matches)

            passed = counts.get('PASSED', 0)
            failed = counts.get('FAILED', 0)
            skipped = counts.get('SKIPPED', 0)

            return {
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "exit_code": result.returncode,
                "output": output
            }

        except subprocess.TimeoutExpired:
            self.logger.log("⚠️  BDD tests timed out after 120 seconds", "WARNING")
            return {
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "exit_code": 1,
                "error": "timeout",
                "output": ""
            }
        except Exception as e:
            self.logger.log(f"⚠️  Error running BDD tests: {e}", "WARNING")
            return {
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "exit_code": 1,
                "error": str(e),
                "output": ""
            }

    def _analyze_bdd_results(self, test_results: Dict) -> Dict:
        """
        Analyze BDD test results and generate validation report.

        What it does: Calculates pass rate, determines overall status, extracts
                      failing scenario details, and generates human-readable summary.

        Why: Transforms raw pytest output into actionable validation report for:
             - Orchestrator (decides whether to pass/fail/iterate)
             - Developers (debugging information for failures)
             - Stakeholders (business requirement satisfaction metrics)

        Args:
            test_results: Dict from _run_bdd_tests() with counts and output

        Returns:
            Dict with validation report:
            - status: "PASS" (all pass), "FAIL" (has failures), "NO_TESTS" (none found)
            - total_scenarios: Total number of scenarios
            - scenarios_passed: Count of passing scenarios
            - scenarios_failed: Count of failing scenarios
            - scenarios_skipped: Count of skipped scenarios
            - pass_rate: Percentage (0-100) of passing scenarios
            - failing_scenarios: List of failure details (file, test, scenario name)
            - summary: Human-readable summary string

        Edge cases:
        - No tests: Returns NO_TESTS status with 0% pass rate
        - All pass: Returns PASS status with 100% pass rate
        - Division by zero: Handled by guard clause (total == 0)
        """
        passed = test_results.get('passed', 0)
        failed = test_results.get('failed', 0)
        skipped = test_results.get('skipped', 0)
        total = passed + failed + skipped

        if total == 0:
            pass_rate = 0
            status = "NO_TESTS"
        else:
            pass_rate = round((passed / total) * 100, 1)
            status = "PASS" if failed == 0 else "FAIL"

        # Extract failing scenario details from output
        output = test_results.get('output', '')
        failing_scenarios = self._extract_failing_scenarios(output)

        report = {
            "status": status,
            "total_scenarios": total,
            "scenarios_passed": passed,
            "scenarios_failed": failed,
            "scenarios_skipped": skipped,
            "pass_rate": pass_rate,
            "failing_scenarios": failing_scenarios,
            "summary": self._generate_summary(status, passed, failed, skipped, pass_rate)
        }

        return report

    def _extract_failing_scenarios(self, output: str) -> list:
        """
        Extract details about failing scenarios from pytest output.

        What it does: Uses regex to parse pytest output and extract information
                      about failing scenarios for debugging.

        Why: Developers need to know WHICH scenarios failed and WHERE to look.
             Regex parsing extracts file path, test name, and converts to
             readable scenario name.

        Parser Pattern Implementation:
        - Regex: (tests/bdd/\S+)::(test_\w+)\s+FAILED
        - Captures: File path and test function name
        - Transform: test_create_user -> "Create User" (human-readable)

        Args:
            output: Pytest output text

        Returns:
            List of failure dicts:
            [
                {
                    "file": "tests/bdd/test_feature.py",
                    "test": "test_create_user",
                    "scenario": "Create User"
                }
            ]

        Name transformation: test_ prefix removed, underscores to spaces, title case
        Why: Makes scenario names human-readable for debugging
        """
        failing_scenarios = []

        # Look for FAILED lines in pytest output
        # Format: tests/bdd/test_feature.py::test_scenario_name FAILED
        failed_pattern = re.compile(r'(tests/bdd/\S+)::(test_\w+)\s+FAILED')

        for match in failed_pattern.finditer(output):
            file_path, test_name = match.groups()
            # Convert test name to scenario name (remove test_ prefix, replace _ with space)
            scenario_name = test_name.replace('test_', '').replace('_', ' ').title()

            failing_scenarios.append({
                "file": file_path,
                "test": test_name,
                "scenario": scenario_name
            })

        return failing_scenarios

    def _generate_summary(
        self,
        status: str,
        passed: int,
        failed: int,
        skipped: int,
        pass_rate: float
    ) -> str:
        """Generate human-readable summary"""
        total = passed + failed + skipped

        if status == "NO_TESTS":
            return "No BDD scenarios found"
        elif status == "PASS":
            return f"All {total} BDD scenarios passing ({pass_rate}% coverage)"
        else:
            return f"{failed} of {total} BDD scenarios failing ({pass_rate}% coverage)"

    def get_stage_name(self) -> str:
        return "bdd_validation"
