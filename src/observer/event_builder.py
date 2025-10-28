#!/usr/bin/env python3
"""
Module: observer/event_builder.py

WHY: Builder for creating pipeline events with convenient methods.
     Provides type-safe, easy-to-use factory methods for common events.

RESPONSIBILITY:
    - Provide convenient methods for creating common events
    - Ensure consistent event creation across codebase
    - Support both standard events and specialized validation events
    - Encapsulate event construction logic

PATTERNS:
    - Builder pattern for object creation
    - Static factory methods for different event types
    - Fluent interface for event data
    - Specialized builders for validation and RAG events

DESIGN DECISIONS:
    - Static methods for stateless factory
    - Separate methods for each event type for type safety
    - **data pattern allows flexible additional data
    - Validation events return dict (legacy compatibility)
    - RAG validation events include confidence and recommendations
"""

from typing import Dict, Any
from datetime import datetime

from .event_model import PipelineEvent
from .event_types import EventType


class EventBuilder:
    """
    Builder for creating pipeline events.

    Provides convenient methods for creating common events.
    """

    @staticmethod
    def pipeline_started(card_id: str, **data) -> PipelineEvent:
        """Create pipeline started event"""
        return PipelineEvent(
            event_type=EventType.PIPELINE_STARTED,
            card_id=card_id,
            data=data
        )

    @staticmethod
    def pipeline_completed(card_id: str, **data) -> PipelineEvent:
        """Create pipeline completed event"""
        return PipelineEvent(
            event_type=EventType.PIPELINE_COMPLETED,
            card_id=card_id,
            data=data
        )

    @staticmethod
    def pipeline_failed(card_id: str, error: Exception, **data) -> PipelineEvent:
        """Create pipeline failed event"""
        return PipelineEvent(
            event_type=EventType.PIPELINE_FAILED,
            card_id=card_id,
            error=error,
            data=data
        )

    @staticmethod
    def stage_started(card_id: str, stage_name: str, **data) -> PipelineEvent:
        """Create stage started event"""
        return PipelineEvent(
            event_type=EventType.STAGE_STARTED,
            card_id=card_id,
            stage_name=stage_name,
            data=data
        )

    @staticmethod
    def stage_completed(card_id: str, stage_name: str, **data) -> PipelineEvent:
        """Create stage completed event"""
        return PipelineEvent(
            event_type=EventType.STAGE_COMPLETED,
            card_id=card_id,
            stage_name=stage_name,
            data=data
        )

    @staticmethod
    def stage_failed(card_id: str, stage_name: str, error: Exception, **data) -> PipelineEvent:
        """Create stage failed event"""
        return PipelineEvent(
            event_type=EventType.STAGE_FAILED,
            card_id=card_id,
            stage_name=stage_name,
            error=error,
            data=data
        )

    @staticmethod
    def developer_started(card_id: str, developer_name: str, **data) -> PipelineEvent:
        """Create developer started event"""
        return PipelineEvent(
            event_type=EventType.DEVELOPER_STARTED,
            card_id=card_id,
            developer_name=developer_name,
            data=data
        )

    @staticmethod
    def developer_completed(card_id: str, developer_name: str, **data) -> PipelineEvent:
        """Create developer completed event"""
        return PipelineEvent(
            event_type=EventType.DEVELOPER_COMPLETED,
            card_id=card_id,
            developer_name=developer_name,
            data=data
        )

    @staticmethod
    def validation_event(developer_name: str, event_type: str, validation_data: dict) -> dict:
        """
        Create a validation event for Layer 3 (Validation Pipeline).

        Args:
            developer_name: Name of developer performing validation
            event_type: Type of validation event:
                - 'validation_started': Validation check initiated
                - 'validation_passed': Validation check passed
                - 'validation_failed': Validation check failed
                - 'validation_max_retries': Max retries exceeded
            validation_data: Event data including:
                - stage: ValidationStage value
                - attempt: Attempt number
                - feedback: List of validation feedback (if failed)
                - score: Validation score (if passed)

        Returns:
            Event dict for observer pattern

        Why: Validation events enable real-time monitoring of code quality
             during generation, not just at the end. This allows:
             - UI dashboards to show live validation status
             - Supervisor to learn from validation patterns
             - Metrics collection for retrospective analysis
        """
        return {
            "type": "validation",
            "subtype": event_type,
            "developer": developer_name,
            "timestamp": datetime.now().isoformat(),
            "data": validation_data
        }

    @staticmethod
    def rag_validation_event(developer_name: str, rag_result, passed: bool) -> dict:
        """
        Create a RAG validation event for Layer 3.5 (RAG-Enhanced Validation).

        WHY: RAG validation events enable monitoring of hallucination prevention:
             - Track how often generated code matches proven patterns
             - Identify frameworks/languages with lower confidence scores
             - Collect metrics on RAG validation effectiveness
             - Enable supervisor to learn from RAG feedback patterns

        Args:
            developer_name: Name of developer performing validation
            rag_result: RAGValidationResult from rag_enhanced_validation
            passed: Whether RAG validation passed

        Returns:
            Event dict for observer pattern with RAG-specific data
        """
        return {
            "type": "rag_validation",
            "subtype": "passed" if passed else "failed",
            "developer": developer_name,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "confidence": rag_result.confidence,
                "similar_examples_count": len(rag_result.similar_examples),
                "similarity_results_count": len(rag_result.similarity_results),
                "warnings": rag_result.warnings,
                "recommendations": rag_result.recommendations,
                "best_match_source": (
                    max(rag_result.similar_examples, key=lambda e: e.relevance_score).source
                    if rag_result.similar_examples else None
                ),
                "best_match_score": (
                    max(rag_result.similar_examples, key=lambda e: e.relevance_score).relevance_score
                    if rag_result.similar_examples else 0.0
                )
            }
        }
