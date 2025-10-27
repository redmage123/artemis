#!/usr/bin/env python3
"""
Module: bdd_test_generation_stage.py

Purpose: Transform Gherkin scenarios into executable pytest-bdd step definitions
         using LLM-powered code generation.

Why: Bridges the gap between business-readable specifications and executable tests.
     pytest-bdd requires Python step definitions to implement Given/When/Then steps.
     LLM generates these definitions automatically from Gherkin scenarios.

Patterns:
- Template Method Pattern: Implements PipelineStage execution contract
- Strategy Pattern: AI Query Service fallback to direct LLM calls
- Supervised Execution Pattern: Health monitoring via SupervisorAgent
- Parser Pattern: Extracts steps from Gherkin using regex

Integration:
- Runs after BDDScenarioGenerationStage (scenarios available)
- Provides pytest-bdd test files to DevelopmentStage
- Feeds into BDD Validation Stage (executes generated tests)
- Stores test files in developer workspace
- Stores test code in RAG for reference

SOLID Principles:
- S: Single Responsibility - Only generates pytest-bdd tests
- O: Open/Closed - Extensible to other BDD frameworks (behave, cucumber-py)
- L: Liskov Substitution - Implements PipelineStage contract
- I: Interface Segregation - Focused on test generation
- D: Dependency Inversion - Depends on abstractions (LLMClient, RAGAgent)
"""

from typing import Dict, Optional, List
from pathlib import Path
import re

from artemis_stage_interface import PipelineStage, LoggerInterface
from supervised_agent_mixin import SupervisedStageMixin
from kanban_manager import KanbanBoard
from rag_agent import RAGAgent
from llm_client import LLMClient
from artemis_exceptions import PipelineStageError, wrap_exception


class BDDTestGenerationStage(PipelineStage, SupervisedStageMixin):
    """
    Generate pytest-bdd step definitions from Gherkin scenarios.

    What it does: Uses LLM to convert Gherkin Given/When/Then steps into executable
                  Python pytest-bdd test code with proper fixtures and assertions.

    Why it exists: pytest-bdd requires Python step definitions to execute Gherkin scenarios.
                   Writing these manually is tedious and error-prone. LLM automates this
                   conversion while ensuring proper pytest-bdd syntax and patterns.

    Responsibilities:
    - Retrieve Gherkin scenarios from context or RAG
    - Extract unique Given/When/Then steps using regex parsing
    - Generate pytest-bdd step definitions using LLM (with AI Query Service optimization)
    - Extract Python code from LLM response (handles markdown code blocks)
    - Store test files in developer workspace
    - Store test code in RAG for reference
    - Track progress via supervised execution

    Design Pattern: Parser Pattern + Strategy Pattern
    - Parser: Regex extraction of Given/When/Then steps from Gherkin
    - Strategy: AI Query Service with fallback to direct LLM calls

    Integrates with supervisor for:
    - LLM call monitoring (tracks token usage and cost)
    - Test generation tracking (monitors code generation progress)
    - Step definition validation (detects malformed Python code)
    - Heartbeat monitoring (20 second interval for LLM-heavy stage)
    """

    def __init__(
        self,
        board: KanbanBoard,
        rag: RAGAgent,
        logger: LoggerInterface,
        llm_client: LLMClient,
        observable: Optional['PipelineObservable'] = None,
        supervisor: Optional['SupervisorAgent'] = None,
        ai_service: Optional['AIQueryService'] = None
    ):
        PipelineStage.__init__(self)
        SupervisedStageMixin.__init__(
            self,
            supervisor=supervisor,
            stage_name="BDDTestGenerationStage",
            heartbeat_interval=20
        )

        self.board = board
        self.rag = rag
        self.logger = logger
        self.llm_client = llm_client
        self.observable = observable
        self.supervisor = supervisor
        self.ai_service = ai_service

    def execute(self, card: Dict, context: Dict) -> Dict:
        """Execute with supervisor monitoring"""
        metadata = {
            "task_id": card.get('card_id'),
            "stage": "bdd_test_generation"
        }

        with self.supervised_execution(metadata):
            result = self._do_work(card, context)

        return result

    def _do_work(self, card: Dict, context: Dict) -> Dict:
        """Generate pytest-bdd test files from Gherkin scenarios"""
        self.logger.log("🧪 Starting BDD Test Generation Stage", "STAGE")

        card_id = card.get('card_id', 'unknown')
        title = card.get('title', 'Unknown Task')

        # Update progress
        self.update_progress({"step": "starting", "progress_percent": 10})

        # Get Gherkin scenarios from context or RAG
        scenarios_content = context.get('scenarios_content')
        if not scenarios_content:
            # Try to fetch from RAG
            scenarios_artifact = self.rag.query(
                query_text=f"bdd scenarios for {title}",
                filter_metadata={"card_id": card_id, "artifact_type": "bdd_scenarios"}
            )
            if scenarios_artifact:
                scenarios_content = scenarios_artifact[0].get('content', '')

        if not scenarios_content:
            self.logger.log("⚠️  No BDD scenarios found - skipping test generation", "WARNING")
            return {
                "stage": "bdd_test_generation",
                "status": "SKIPPED",
                "reason": "No BDD scenarios available"
            }

        self.logger.log(f"📝 Generating pytest-bdd tests for: {title}", "INFO")

        # Update progress
        self.update_progress({"step": "parsing_scenarios", "progress_percent": 30})

        # Extract steps from Gherkin scenarios
        steps = self._extract_steps_from_gherkin(scenarios_content)

        # Update progress
        self.update_progress({"step": "generating_tests", "progress_percent": 50})

        # Generate pytest-bdd test file using LLM
        test_content = self._generate_pytest_bdd_tests(
            card_id=card_id,
            title=title,
            scenarios_content=scenarios_content,
            steps=steps
        )

        # Update progress
        self.update_progress({"step": "storing_tests", "progress_percent": 80})

        # Store test files for each developer
        winner = context.get('winner', 'developer-a')
        test_path = self._store_test_file(winner, title, test_content)

        # Store in RAG
        self.rag.store_artifact(
            artifact_type="bdd_tests",
            card_id=card_id,
            task_title=title,
            content=test_content,
            metadata={
                "test_path": str(test_path),
                "step_count": len(steps),
                "framework": "pytest-bdd"
            }
        )

        # Update progress
        self.update_progress({"step": "complete", "progress_percent": 100})

        self.logger.log(f"✅ Generated {len(steps)} pytest-bdd step definitions", "SUCCESS")

        return {
            "stage": "bdd_test_generation",
            "test_path": str(test_path),
            "test_content": test_content,
            "step_count": len(steps),
            "framework": "pytest-bdd"
        }

    def _extract_steps_from_gherkin(self, content: str) -> List[str]:
        """
        Extract unique Given/When/Then steps from Gherkin scenarios.

        What it does: Uses regex to parse Gherkin text and extract all Given/When/Then/And/But
                      steps, returning unique normalized steps.

        Why: LLM needs to know which steps require Python implementations. Extracting unique
             steps prevents duplicate code generation and shows LLM the full step vocabulary.

        Parser Pattern Implementation:
        - Regex: ^\s*(Given|When|Then|And|But)\s+(.+)$
        - Multiline mode: Matches steps across entire document
        - Set deduplication: O(1) lookup for uniqueness

        Args:
            content: Gherkin scenario text

        Returns:
            List of (keyword, step_text) tuples
            Example: [("Given", "I am on the homepage"), ("When", "I click login")]

        Performance: O(n) single-pass regex matching
        """
        steps = set()

        # Match Given/When/Then/And/But lines
        step_pattern = re.compile(r'^\s*(Given|When|Then|And|But)\s+(.+)$', re.MULTILINE)

        for match in step_pattern.finditer(content):
            keyword, step_text = match.groups()
            # Normalize step text (remove quotes, parameters)
            normalized = step_text.strip()
            steps.add((keyword, normalized))

        return list(steps)

    def _generate_pytest_bdd_tests(
        self,
        card_id: str,
        title: str,
        scenarios_content: str,
        steps: List[tuple]
    ) -> str:
        """
        Generate pytest-bdd test file using LLM.

        What it does: Uses LLM to convert Gherkin scenarios into complete pytest-bdd
                      Python test file with imports, fixtures, and step definitions.

        Why: LLM excels at code generation from specifications. It generates:
             - Proper pytest-bdd imports (@scenarios, @given, @when, @then)
             - Fixtures for shared state (browser, API clients)
             - Step definitions with parsers for parameterized steps
             - Clear assertions in Then steps

        Strategy Pattern Implementation:
        - Primary: AI Query Service (token-optimized routing)
        - Fallback: Direct LLM call (if service unavailable)

        Args:
            card_id: Card ID for context tracking
            title: Feature title for test file reference
            scenarios_content: Full Gherkin scenario text
            steps: Extracted unique steps for LLM reference

        Returns:
            Complete Python test file content as string

        LLM Prompt Design:
        - Temperature: 0.3 (deterministic, consistent code)
        - Max tokens: 3000 (sufficient for 10-15 step definitions)
        - Prompt includes: Scenarios, guidelines, format requirements
        - Instructs LLM to use: @scenarios decorator, parsers.parse(), proper assertions

        Code Extraction: Handles both ```python and ``` markdown code blocks
        Why: LLMs often wrap code in markdown; extraction ensures clean Python code
        """

        prompt = f"""You are a BDD test automation expert. Generate pytest-bdd step definitions for the following Gherkin scenarios.

# Gherkin Scenarios

{scenarios_content}

# Task

Generate a complete pytest-bdd test file with:

1. **Import statements** for pytest-bdd (scenarios, given, when, then, parsers)
2. **Fixture setup** (if needed for browser, API clients, etc.)
3. **Step definitions** for all Given/When/Then steps
4. **Proper use of parsers** for parameterized steps
5. **Assertions** in Then steps to verify expected outcomes

# Guidelines

- Use `@scenarios('feature_file.feature')` to load all scenarios
- Use `parsers.parse()` for steps with parameters (e.g., "I enter {{value}}")
- Use `parsers.cfparse()` for complex parsing needs
- Steps should be reusable across scenarios
- Use fixtures for shared state and setup
- Make assertions clear and specific

# Output Format

Provide ONLY the complete Python code for the pytest-bdd test file. No explanations.

Generate the test file now:
"""

        # Use AI Query Service if available for token optimization
        if self.ai_service:
            result = self.ai_service.query(
                query=prompt,
                context={"card_id": card_id, "title": title},
                temperature=0.3,
                max_tokens=3000
            )
            if result.success:
                return result.response
            else:
                self.logger.log(f"AI Query Service failed: {result.error}, falling back to direct LLM", "WARNING")

        # Fallback to direct LLM call
        response = self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=3000
        )

        # Extract Python code from response
        code = response
        if "```python" in code:
            code_start = code.find("```python") + 9
            code_end = code.find("```", code_start)
            code = code[code_start:code_end].strip()
        elif "```" in code:
            code_start = code.find("```") + 3
            code_end = code.find("```", code_start)
            code = code[code_start:code_end].strip()

        return code

    def _store_test_file(self, developer: str, title: str, content: str) -> Path:
        """Store pytest-bdd test file in developer's directory"""
        test_dir = Path(f"/tmp/{developer}/tests/bdd")
        test_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        filename = title.lower().replace(' ', '_').replace('/', '_')
        test_path = test_dir / f"test_{filename}.py"

        with open(test_path, 'w') as f:
            f.write(content)

        self.logger.log(f"📝 Stored test file: {test_path}", "INFO")

        return test_path

    def get_stage_name(self) -> str:
        return "bdd_test_generation"
