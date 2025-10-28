#!/usr/bin/env python3
"""
WHY: Build detailed prompts for developer agents with TDD and SOLID instructions
RESPONSIBILITY: Generate comprehensive prompts with task context, ADR, and requirements
PATTERNS: Builder (prompt construction), Template Method (structured format)

Prompt building provides:
- Developer-specific instructions (conservative/aggressive/innovative)
- TDD workflow guidance (RED-GREEN-REFACTOR)
- SOLID compliance requirements
- Mock guidance for external dependencies
- Output directory structure
"""

from typing import Dict
from pathlib import Path
from artemis_constants import get_developer_prompt_path
from environment_context import get_environment_context_short


class DeveloperPromptBuilder:
    """
    Builds detailed prompts for developer agents

    Generates structured prompts with task details, ADR content,
    TDD workflow, and SOLID requirements.
    """

    def build_prompt(
        self,
        developer_name: str,
        developer_type: str,
        card: Dict,
        adr_content: str,
        adr_file: str,
        output_dir: Path
    ) -> str:
        """
        Build detailed prompt for developer agent

        Args:
            developer_name: Name of developer (developer-a, developer-b, etc.)
            developer_type: Type of developer (conservative, aggressive, innovative)
            card: Kanban card with task details
            adr_content: ADR content
            adr_file: Path to ADR file
            output_dir: Output directory for implementation

        Returns:
            Complete developer prompt
        """
        # Determine which developer prompt to use
        prompt_file = str(get_developer_prompt_path(developer_name))

        task_title = card.get('title', 'Untitled Task')
        task_description = card.get('description', 'No description provided')

        # Build prompt sections
        header = self._build_header(developer_name, developer_type)
        critical_instructions = self._build_critical_instructions(
            prompt_file, adr_file, developer_name, developer_type
        )
        task_section = self._build_task_section(
            task_title, task_description, developer_type, output_dir
        )
        tdd_workflow = self._build_tdd_workflow(output_dir)
        solid_compliance = self._build_solid_compliance(developer_type)
        storage_instructions = self._build_storage_instructions(output_dir)
        report_instructions = self._build_report_instructions(output_dir)
        scoring_reminder = self._build_scoring_reminder(developer_type)

        # Assemble complete prompt
        return f"""{header}

{critical_instructions}

{task_section}

{tdd_workflow}

{solid_compliance}

{storage_instructions}

{report_instructions}

{scoring_reminder}
"""

    def _build_header(self, developer_name: str, developer_type: str) -> str:
        """Build prompt header"""
        return f"""You are {developer_name.upper()} - the {developer_type} developer in the Artemis competitive pipeline."""

    def _build_critical_instructions(
        self,
        prompt_file: str,
        adr_file: str,
        developer_name: str,
        developer_type: str
    ) -> str:
        """Build critical instructions section"""
        return f"""CRITICAL INSTRUCTIONS:

1. **Read your developer prompt**: {prompt_file}
   - Follow ALL instructions in your prompt
   - Apply the {developer_type} approach as specified
   - You MUST follow SOLID principles (mandatory)

2. **Read the ADR**: {adr_file}
   - This contains the architectural decisions and guidance
   - Follow the implementation strategy for {developer_name}"""

    def _build_task_section(
        self,
        task_title: str,
        task_description: str,
        developer_type: str,
        output_dir: Path
    ) -> str:
        """Build task section"""
        env_context = get_environment_context_short()
        return f"""3. **Implement the solution using TDD**:

   **TASK**: {task_title}

   **DESCRIPTION**: {task_description}

   **YOUR APPROACH**: {developer_type}

   **OUTPUT DIRECTORY**: {output_dir}

{env_context}"""

    def _build_tdd_workflow(self, output_dir: Path) -> str:
        """Build TDD workflow section"""
        return f"""   **MANDATORY TDD WORKFLOW**:

   Phase 1 - RED (Write Failing Tests):
   - Create test files FIRST in: {output_dir}/tests/
   - Write tests that FAIL (feature not implemented yet)
   - Run tests to verify they fail

   **CRITICAL TEST REQUIREMENTS**:
   - DO NOT import external dependencies that you haven't implemented (Kafka, Spark, InfluxDB, etc.)
   - If requirements mention external systems, use unittest.mock to mock them
   - Write EXECUTABLE tests that can run without installing external infrastructure
   - Focus on testing YOUR logic, not external integrations
   - Example: If requirements mention Kafka, use Mock objects instead of actual Kafka imports

   Example of CORRECT test approach:
   ```python
   import unittest
   from unittest.mock import Mock, patch

   class TestDataIngestion(unittest.TestCase):
       @patch('your_module.KafkaProducer')  # Mock external dependency
       def test_kafka_connection(self, mock_kafka):
           mock_kafka.return_value = Mock()
           # Test your logic, not Kafka itself
           result = your_function()
           self.assertIsNotNone(result)
   ```

   Example of INCORRECT test (DO NOT DO THIS):
   ```python
   from kafka import KafkaProducer  # ❌ NOT INSTALLED, WILL FAIL

   class TestDataIngestion(unittest.TestCase):
       def test_kafka_connection(self):
           producer = KafkaProducer(...)  # ❌ CANNOT RUN
   ```

   Phase 2 - GREEN (Make Tests Pass):
   - Implement MINIMUM code to make tests pass
   - Store implementation in: {output_dir}/
   - Use Mock objects for external dependencies mentioned in requirements
   - DO NOT implement actual Kafka/Spark/InfluxDB connections - use mock interfaces
   - Run tests to verify they pass

   Phase 3 - REFACTOR (Improve Quality):
   - Refactor code while keeping tests green
   - Add SOLID compliance
   - Add type hints and docstrings
   - Run tests to ensure still passing"""

    def _build_solid_compliance(self, developer_type: str) -> str:
        """Build SOLID compliance section"""
        patterns = (
            "Conservative patterns: Dependency Injection, SRP, Strategy"
            if developer_type == "conservative"
            else "Advanced patterns: Hexagonal Architecture, Composite, Decorator"
        )

        return f"""4. **SOLID Compliance (MANDATORY)**:
   - Apply ALL 5 SOLID principles
   - {patterns}
   - This is NON-NEGOTIABLE and affects arbitration scoring"""

    def _build_storage_instructions(self, output_dir: Path) -> str:
        """Build storage instructions section"""
        return f"""5. **Store your solution**:
   - Implementation files: {output_dir}/<feature>.py
   - Test files: {output_dir}/tests/unit/test_<feature>.py
   - Test files: {output_dir}/tests/integration/test_<feature>_integration.py
   - Test files: {output_dir}/tests/acceptance/test_<feature>_acceptance.py"""

    def _build_report_instructions(self, output_dir: Path) -> str:
        """Build report instructions section"""
        return f"""6. **Generate solution report**:
   - Create {output_dir}/solution_report.json with:
     - Approach explanation
     - SOLID principles applied
     - Test coverage metrics
     - TDD workflow timestamps"""

    def _build_scoring_reminder(self, developer_type: str) -> str:
        """Build scoring reminder section"""
        return f"""REMEMBER: You are competing against another developer. Your solution will be scored on:
- SOLID compliance (+15 for exceptional, -10 for violations)
- Test coverage (80% minimum for A, 90% for B)
- Code quality
- TDD compliance

Read your prompt file, read the ADR, and implement the best {developer_type} solution!"""
