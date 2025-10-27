#!/usr/bin/env python3
"""
Validated Developer Mixin

Adds Layer 3 (Validation Pipeline) to StandaloneDeveloperAgent.

This mixin integrates continuous validation during code generation,
catching hallucinations before they propagate.

Usage:
    class ValidatedDeveloperAgent(StandaloneDeveloperAgent, ValidatedDeveloperMixin):
        pass

    # Validation is automatically applied to all code generation
"""

from pathlib import Path
from typing import Dict, Optional
from validation_pipeline import (
    ValidationPipeline,
    ValidationStage,
    StageValidationResult
)
from rag_enhanced_validation import RAGValidationFactory


class ValidatedDeveloperMixin:
    """
    Mixin that adds validation pipeline to developer agents.

    Integrates all 4 layers of validation:
    1. Preflight - Already in standalone_developer_agent
    2. Strategy Selection - Already uses requirements_driven_validator
    3. Validation Pipeline - THIS MIXIN
    4. Quality Gates - Already uses artifact_quality_validator

    Methods added:
    - _validated_llm_query: Query LLM with validation
    - _validate_generated_code: Validate code at specific stage
    - get_validation_stats: Get validation statistics
    """

    def __init_validation_pipeline__(self, strict_mode: bool = True, enable_rag_validation: bool = True):
        """
        Initialize validation pipeline (Layer 3 of 4-layer architecture).

        Why: This adds continuous validation during code generation to catch
             hallucinations before they propagate through the entire artifact.

        Args:
            strict_mode: If True, fail on any validation error.
                        If False, only fail on critical errors.
            enable_rag_validation: If True, enable RAG-enhanced validation.
        """
        if not hasattr(self, 'validation_pipeline'):
            llm_client = getattr(self, 'llm_client', None)
            logger = getattr(self, 'logger', None)

            self.validation_pipeline = ValidationPipeline(
                llm_client=llm_client,
                logger=logger,
                strict_mode=strict_mode
            )

            self.validation_enabled = True  # Can be toggled via enable_validation()
            self.validation_stats = {
                'total_validations': 0,
                'failed_validations': 0,
                'regenerations': 0,
                'rag_validations': 0,
                'rag_failures': 0,
                'rag_warnings': 0
            }

            # Initialize RAG validator (Layer 3.5)
            self.rag_validation_enabled = enable_rag_validation
            if enable_rag_validation:
                rag_agent = getattr(self, 'rag', None)
                if rag_agent:
                    # Get framework from context
                    framework = self._get_framework_from_context()

                    self.rag_validator = RAGValidationFactory.create_validator(
                        rag_agent=rag_agent,
                        framework=framework
                    )

                    if logger:
                        logger.log(f"✅ RAG Validation enabled (framework: {framework or 'generic'})", "INFO")
                else:
                    self.rag_validation_enabled = False
                    if logger:
                        logger.log("⚠️  RAG Validation disabled (no RAG agent)", "WARNING")

            # Store observable reference for event notifications
            self.observable = getattr(self, 'observable', None)

            if logger:
                logger.log("✅ Validation Pipeline initialized (Layer 3)", "INFO")

    def _validated_llm_query(self,
                            prompt: str,
                            stage: ValidationStage,
                            max_retries: int = 2,
                            context: Optional[Dict] = None) -> str:
        """
        Query LLM with validation pipeline.

        This replaces direct llm_client.query() calls with validated queries
        that check for hallucinations and regenerate if needed.

        Args:
            prompt: The prompt to send to LLM
            stage: Which validation stage this is
            max_retries: Maximum regeneration attempts
            context: Additional validation context

        Returns:
            Validated code from LLM

        Raises:
            Exception if validation fails after max_retries
        """
        if not self.validation_enabled:
            # Validation disabled - fall back to direct query
            return self.llm_client.query(prompt)

        llm_client = getattr(self, 'llm_client')
        logger = getattr(self, 'logger', None)

        for attempt in range(max_retries + 1):
            # OBSERVER: Notify validation started
            self._notify_validation_event('validation_started', {
                'stage': stage.value,
                'attempt': attempt
            })

            # Generate code
            if logger and attempt > 0:
                logger.log(f"🔄 Regeneration attempt {attempt}/{max_retries}", "INFO")

            response = llm_client.query(prompt)

            # Extract code from response (handle markdown fences)
            code = self._extract_code_from_response(response)

            # Validate
            result = self.validation_pipeline.validate_stage(code, stage, context)

            self.validation_stats['total_validations'] += 1

            if result.passed:
                # OBSERVER: Notify validation passed
                self._notify_validation_event('validation_passed', {
                    'stage': stage.value,
                    'attempt': attempt,
                    'score': result.score if hasattr(result, 'score') else 1.0
                })

                # RAG Validation (Layer 3.5) - Only for BODY and FULL_CODE stages
                if self.rag_validation_enabled and stage in [ValidationStage.BODY, ValidationStage.FULL_CODE]:
                    rag_result = self._validate_with_rag(code, stage, context, logger)

                    # Track RAG validation stats
                    self.validation_stats['rag_validations'] += 1

                    if not rag_result.passed:
                        # RAG validation failed
                        self.validation_stats['rag_failures'] += 1

                        # OBSERVER: Notify RAG validation failed
                        self._notify_rag_validation_event(rag_result, passed=False)

                        if logger:
                            logger.log(
                                f"⚠️  RAG validation warnings: {', '.join(rag_result.warnings[:2])}",
                                "WARNING"
                            )

                        # Only fail if confidence is very low (< 0.3)
                        if rag_result.confidence < 0.3 and attempt < max_retries:
                            # Add RAG feedback to prompt for regeneration
                            rag_feedback = "\\n".join(rag_result.recommendations[:3])
                            prompt += f"\\n\\nRAG Validation Feedback:\\n{rag_feedback}"

                            if logger:
                                logger.log("🔄 Regenerating with RAG feedback", "INFO")

                            continue  # Retry with RAG feedback
                        else:
                            # Low confidence but max retries - add warning
                            self.validation_stats['rag_warnings'] += 1
                    else:
                        # OBSERVER: Notify RAG validation passed
                        self._notify_rag_validation_event(rag_result, passed=True)

                        if logger and rag_result.confidence < 0.7:
                            logger.log(
                                f"⚠️  Code validated but with low RAG confidence: {rag_result.confidence:.2f}",
                                "WARNING"
                            )

                # Validation passed
                if logger and attempt > 0:
                    logger.log(f"✅ Validation passed after {attempt} regenerations", "INFO")

                if attempt > 0:
                    self.validation_stats['regenerations'] += 1

                return code

            # OBSERVER: Notify validation failed
            self._notify_validation_event('validation_failed', {
                'stage': stage.value,
                'attempt': attempt,
                'feedback': result.feedback[:3]  # First 3 feedback items
            })

            # Validation failed
            self.validation_stats['failed_validations'] += 1

            if logger:
                logger.log(f"❌ Validation failed: {', '.join(result.feedback[:2])}", "WARNING")

            if attempt < max_retries:
                # Regenerate with feedback
                feedback_prompt = self.validation_pipeline.get_regeneration_prompt(result)
                prompt += f"\n\n{feedback_prompt}"
            else:
                # OBSERVER: Notify max retries exceeded
                self._notify_validation_event('validation_max_retries', {
                    'stage': stage.value,
                    'feedback': result.feedback
                })

                # Max retries exceeded
                if logger:
                    logger.log(f"❌ Max retries exceeded for {stage.value}", "ERROR")
                raise Exception(
                    f"Validation failed after {max_retries} attempts: {result.feedback}"
                )

        # Should never reach here
        return code

    def _validate_generated_code(self,
                                code: str,
                                stage: ValidationStage,
                                context: Optional[Dict] = None) -> StageValidationResult:
        """
        Validate generated code at a specific stage.

        Args:
            code: Code to validate
            stage: Which stage to validate
            context: Additional context

        Returns:
            Validation result
        """
        if not hasattr(self, 'validation_pipeline'):
            self.__init_validation_pipeline__()

        return self.validation_pipeline.validate_stage(code, stage, context)

    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from LLM response (remove markdown fences)"""
        import re

        # If response is a dict/object with content field
        if hasattr(response, 'content'):
            response = response.content
        elif isinstance(response, dict) and 'content' in response:
            response = response['content']

        # Convert to string if not already
        response = str(response)

        # Remove markdown code blocks
        # Match ```python\n...\n``` or ```\n...\n```
        code_block_pattern = r'```(?:python|javascript|typescript|java|go|rust|cpp|c)?\n(.*?)\n```'
        matches = re.findall(code_block_pattern, response, re.DOTALL)

        if matches:
            # Return first code block
            return matches[0].strip()

        # No code blocks found - return as-is
        return response.strip()

    def get_validation_stats(self) -> Dict:
        """Get validation statistics"""
        if not hasattr(self, 'validation_pipeline'):
            return {'validation_pipeline': 'not_initialized'}

        pipeline_stats = self.validation_pipeline.get_validation_summary()

        return {
            **self.validation_stats,
            **pipeline_stats,
            'validation_enabled': self.validation_enabled
        }

    def enable_validation(self, enabled: bool = True):
        """Enable or disable validation pipeline"""
        self.validation_enabled = enabled
        logger = getattr(self, 'logger', None)
        if logger:
            status = "enabled" if enabled else "disabled"
            logger.log(f"Validation pipeline {status}", "INFO")

    def get_validation_report(self) -> str:
        """Get human-readable validation report"""
        stats = self.get_validation_stats()

        if stats.get('validation_pipeline') == 'not_initialized':
            return "Validation pipeline not initialized"

        report = f"""
Validation Pipeline Report
{'='*50}

Overall Statistics:
  Total Validations: {stats['total_validations']}
  Passed: {stats['passed']}
  Failed: {stats['failed']}
  Pass Rate: {stats['pass_rate']:.1%}
  Regenerations: {stats.get('regenerations', 0)}

By Stage:
"""
        for stage, counts in stats.get('by_stage', {}).items():
            report += f"  {stage}: {counts['passed']} passed, {counts['failed']} failed\n"

        return report

    def _notify_validation_event(self, event_type: str, data: dict):
        """
        Notify observers of validation events (Observer Pattern).

        Why: This enables real-time monitoring of validation during code generation:
             - UI dashboards can show live validation status
             - Supervisor can learn from validation patterns
             - Metrics collectors can track hallucination trends

        Args:
            event_type: Type of validation event (validation_started, validation_passed, etc.)
            data: Event data including stage, attempt, feedback, score
        """
        observable = getattr(self, 'observable', None)
        developer_name = getattr(self, 'developer_name', 'unknown')

        if observable:
            try:
                # Use EventBuilder from pipeline_observer
                from pipeline_observer import EventBuilder

                event = EventBuilder.validation_event(
                    developer_name=developer_name,
                    event_type=event_type,
                    validation_data=data
                )

                observable.notify(event)
            except Exception as e:
                # Don't fail if observer notification fails
                logger = getattr(self, 'logger', None)
                if logger:
                    logger.log(f"⚠️  Observer notification failed: {e}", "DEBUG")

    def _validate_with_rag(self, code: str, stage: ValidationStage, context: Optional[Dict], logger) -> 'RAGValidationResult':
        """
        Validate code using RAG-enhanced validation (Layer 3.5).

        WHY: Checks generated code against proven patterns from RAG database.
             This catches hallucinations that pass standard validation but
             don't match real-world code patterns.

        WHAT: Queries RAG for similar code, computes similarity using multiple
              strategies, returns validation result with confidence score.

        Args:
            code: Generated code to validate
            stage: Validation stage (BODY or FULL_CODE)
            context: Additional context (language, framework, requirements)
            logger: Logger for debugging

        Returns:
            RAGValidationResult with pass/fail and recommendations
        """
        try:
            # Build RAG context from validation context
            rag_context = {
                'language': context.get('language', 'python') if context else 'python',
                'framework': context.get('framework') if context else None,
                'requirements': context.get('task_description') if context else None
            }

            # Validate using RAG validator
            result = self.rag_validator.validate_code(
                generated_code=code,
                context=rag_context,
                top_k=5  # Query top 5 similar examples
            )

            return result

        except Exception as e:
            # RAG validation failure shouldn't block code generation
            # Return passed result with warning
            if logger:
                logger.log(f"⚠️  RAG validation error: {e}", "DEBUG")

            # Create failed result to trigger regeneration
            from rag_enhanced_validation import RAGValidationResult
            return RAGValidationResult(
                passed=True,  # Don't block on RAG errors
                confidence=0.5,  # Medium confidence
                similar_examples=[],
                similarity_results=[],
                warnings=[f"RAG validation encountered error: {str(e)}"],
                recommendations=[]
            )

    def _notify_rag_validation_event(self, rag_result: 'RAGValidationResult', passed: bool):
        """
        Notify observers of RAG validation events (Observer Pattern).

        WHY: Enables real-time monitoring of RAG validation:
             - UI dashboards show RAG validation status
             - Supervisor learns from RAG validation patterns
             - Metrics collectors track hallucination prevention

        Args:
            rag_result: RAG validation result
            passed: Whether validation passed
        """
        observable = getattr(self, 'observable', None)
        developer_name = getattr(self, 'developer_name', 'unknown')

        if observable:
            try:
                # Use EventBuilder from pipeline_observer
                from pipeline_observer import EventBuilder

                event = EventBuilder.rag_validation_event(
                    developer_name=developer_name,
                    rag_result=rag_result,
                    passed=passed
                )

                observable.notify(event)
            except Exception as e:
                # Don't fail if observer notification fails
                logger = getattr(self, 'logger', None)
                if logger:
                    logger.log(f"⚠️  RAG observer notification failed: {e}", "DEBUG")

    def _get_framework_from_context(self) -> Optional[str]:
        """
        Extract framework from context/metadata.

        WHY: Framework detection enables framework-specific RAG validation
             thresholds (Django vs Flask have different patterns).

        WHAT: Looks in multiple places for framework info:
              1. self.context (if exists)
              2. self.metadata (if exists)
              3. self.config (if exists)
              4. Returns None if not found

        Returns:
            Framework name (django, flask, rails, react, etc.) or None
        """
        # Framework detection strategy (avoid nested ifs - use early returns)
        context = getattr(self, 'context', None)
        if context and isinstance(context, dict):
            framework = context.get('framework')
            if framework:
                return framework.lower()

        metadata = getattr(self, 'metadata', None)
        if metadata and isinstance(metadata, dict):
            framework = metadata.get('framework')
            if framework:
                return framework.lower()

        config = getattr(self, 'config', None)
        if config and hasattr(config, 'framework'):
            return config.framework.lower()

        # No framework found
        return None


# ═══════════════════════════════════════════════════════════════════
# Enhanced TDD Workflow Methods
# ═══════════════════════════════════════════════════════════════════

class ValidatedTDDMixin(ValidatedDeveloperMixin):
    """
    Extended mixin with validated TDD workflow methods.

    Adds methods specifically for TDD workflow with validation:
    - _validated_red_phase: Generate tests with validation
    - _validated_green_phase: Generate implementation with validation
    - _validated_refactor_phase: Refactor with validation
    """

    def _validated_red_phase(self, task_title: str, task_description: str,
                            adr_content: str, context: Dict) -> Dict:
        """
        RED phase with validation: Write failing tests

        Returns:
            Dict with test_code, test_files, validation_result
        """
        logger = getattr(self, 'logger', None)

        if logger:
            logger.log("🔴 RED: Generating tests (with validation)...", "INFO")

        # Build prompt for test generation
        prompt = self._build_red_phase_prompt(task_title, task_description, adr_content, context)

        # Generate tests with validation
        test_code = self._validated_llm_query(
            prompt=prompt,
            stage=ValidationStage.TESTS,
            max_retries=2,
            context={
                'task_title': task_title,
                'task_description': task_description
            }
        )

        # Parse and write test files
        test_files = self._write_test_files(test_code, context.get('output_dir'))

        return {
            'test_code': test_code,
            'test_files': test_files,
            'phase': 'RED',
            'validated': True
        }

    def _validated_green_phase(self, task_title: str, task_description: str,
                               adr_content: str, test_code: str, context: Dict) -> Dict:
        """
        GREEN phase with validation: Implement minimum code to pass tests

        Returns:
            Dict with implementation_code, implementation_files, validation_result
        """
        logger = getattr(self, 'logger', None)

        if logger:
            logger.log("🟢 GREEN: Generating implementation (with validation)...", "INFO")

        # Build prompt for implementation
        prompt = self._build_green_phase_prompt(
            task_title, task_description, adr_content, test_code, context
        )

        # Validate incrementally: imports → signature → body
        full_code = ""

        # Stage 1: Imports
        imports_prompt = f"{prompt}\n\nFirst, generate only the import statements needed."
        imports = self._validated_llm_query(
            prompt=imports_prompt,
            stage=ValidationStage.IMPORTS,
            max_retries=2
        )
        full_code += imports + "\n\n"

        # Stage 2: Signature
        sig_prompt = f"{prompt}\n\n{full_code}\n\nNow generate function/class signatures with type hints and docstrings."
        signature = self._validated_llm_query(
            prompt=sig_prompt,
            stage=ValidationStage.SIGNATURE,
            max_retries=2
        )
        full_code += signature + "\n\n"

        # Stage 3: Body
        body_prompt = f"{prompt}\n\n{full_code}\n\nNow complete the implementation. No TODOs or placeholders."
        body = self._validated_llm_query(
            prompt=body_prompt,
            stage=ValidationStage.BODY,
            max_retries=2,
            context={'expected_methods': self._extract_test_methods(test_code)}
        )
        full_code += body

        # Final validation
        final_result = self._validate_generated_code(
            code=full_code,
            stage=ValidationStage.FULL_CODE
        )

        if not final_result.passed and logger:
            logger.log(f"⚠️  Final validation warnings: {final_result.feedback}", "WARNING")

        # Write implementation files
        impl_files = self._write_implementation_files(full_code, context.get('output_dir'))

        return {
            'implementation_code': full_code,
            'implementation_files': impl_files,
            'phase': 'GREEN',
            'validated': True,
            'validation_result': final_result
        }

    def _validated_refactor_phase(self, implementation_code: str, context: Dict) -> Dict:
        """
        REFACTOR phase with validation: Improve code quality

        Returns:
            Dict with refactored_code, refactored_files, validation_result
        """
        logger = getattr(self, 'logger', None)

        if logger:
            logger.log("🔵 REFACTOR: Improving code (with validation)...", "INFO")

        # Build refactoring prompt
        prompt = f"""Refactor this code to improve quality:

{implementation_code}

Requirements:
- Maintain all functionality
- Improve readability
- Add type hints if missing
- Improve docstrings
- Follow best practices
- NO PLACEHOLDERS OR TODOs

Return the refactored code.
"""

        # Refactor with validation
        refactored_code = self._validated_llm_query(
            prompt=prompt,
            stage=ValidationStage.FULL_CODE,
            max_retries=2
        )

        return {
            'refactored_code': refactored_code,
            'phase': 'REFACTOR',
            'validated': True
        }

    def _extract_test_methods(self, test_code: str) -> list:
        """Extract method names from test code"""
        import re
        # Find all function calls in assertions
        method_calls = re.findall(r'(\w+)\s*\(', test_code)
        return list(set(method_calls))

    def _build_red_phase_prompt(self, title, desc, adr, context) -> str:
        """Build prompt for RED phase (override in subclass if needed)"""
        return f"Generate pytest tests for: {title}\n\n{desc}\n\nADR:\n{adr}"

    def _build_green_phase_prompt(self, title, desc, adr, tests, context) -> str:
        """Build prompt for GREEN phase (override in subclass if needed)"""
        return f"Implement code to pass these tests:\n\n{tests}\n\nTask: {title}\n{desc}"

    def _write_test_files(self, code, output_dir) -> list:
        """Write test files (override in subclass)"""
        # This should be implemented by the actual developer agent
        raise NotImplementedError("Subclass must implement _write_test_files")

    def _write_implementation_files(self, code, output_dir) -> list:
        """Write implementation files (override in subclass)"""
        # This should be implemented by the actual developer agent
        raise NotImplementedError("Subclass must implement _write_implementation_files")


# ═══════════════════════════════════════════════════════════════════
# Helper: Create Validated Developer Agent
# ═══════════════════════════════════════════════════════════════════

def create_validated_developer_agent(
    developer_name: str,
    developer_type: str,
    llm_provider: str = "openai",
    llm_model: Optional[str] = None,
    logger = None,
    rag_agent = None,
    ai_service = None,
    enable_validation: bool = True,
    enable_rag_validation: bool = True
):
    """
    Factory function to create a validated developer agent.

    This creates a developer agent with all 4 validation layers enabled.

    Args:
        developer_name: Name of developer
        developer_type: Type (conservative/aggressive)
        llm_provider: LLM provider (openai/anthropic)
        llm_model: Specific model
        logger: Logger instance
        rag_agent: RAG agent
        ai_service: AI Query Service
        enable_validation: Enable validation pipeline (Layer 3, default True)
        enable_rag_validation: Enable RAG-enhanced validation (Layer 3.5, default True)

    Returns:
        StandaloneDeveloperAgent with validation enabled
    """
    from standalone_developer_agent import StandaloneDeveloperAgent

    # Create base developer agent
    agent = StandaloneDeveloperAgent(
        developer_name=developer_name,
        developer_type=developer_type,
        llm_provider=llm_provider,
        llm_model=llm_model,
        logger=logger,
        rag_agent=rag_agent,
        ai_service=ai_service
    )

    # Add validation mixin functionality dynamically
    # Copy methods from ValidatedDeveloperMixin to agent instance
    for attr_name in dir(ValidatedDeveloperMixin):
        if not attr_name.startswith('_') or attr_name.startswith('_validated') or attr_name.startswith('__init'):
            attr = getattr(ValidatedDeveloperMixin, attr_name)
            if callable(attr):
                # Bind method to agent instance
                setattr(agent, attr_name, attr.__get__(agent, type(agent)))

    # Initialize validation pipeline (Layer 3 + Layer 3.5)
    agent.__init_validation_pipeline__(
        strict_mode=True,
        enable_rag_validation=enable_rag_validation
    )
    agent.enable_validation(enable_validation)

    if logger:
        logger.log(f"✅ Created validated developer: {developer_name}", "INFO")

    return agent
