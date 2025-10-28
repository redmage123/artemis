#!/usr/bin/env python3
"""
Checkpoint Restorer

WHY: Handles checkpoint restoration and LLM response caching, enabling pipeline
     resumption from saved state and avoiding redundant LLM calls.

RESPONSIBILITY:
    - Restore checkpoints from storage
    - Validate checkpoint resumability
    - Manage LLM response cache
    - Restore execution state

PATTERNS:
    - Memento Pattern: Restore previous state from saved checkpoint
    - Cache Pattern: Store and retrieve LLM responses
    - Guard Clauses: Validate restoration preconditions
"""

from datetime import datetime
from typing import Dict, Optional, Any

from .models import PipelineCheckpoint, CheckpointStatus
from .storage import CheckpointRepository, CheckpointValidator
from .creator import LLMCacheKeyGenerator


# ============================================================================
# CHECKPOINT RESTORER
# ============================================================================

class CheckpointRestorer:
    """
    Restores pipeline state from checkpoints

    Handles loading checkpoints, validating resumability,
    and updating checkpoint metadata for resumption.
    """

    def __init__(self, repository: CheckpointRepository):
        """
        Initialize checkpoint restorer

        Args:
            repository: Checkpoint storage repository
        """
        self.repository = repository
        self.validator = CheckpointValidator()

    def can_resume(self, card_id: str) -> bool:
        """
        Check if checkpoint can be resumed

        Guard clause approach - fail fast on invalid conditions

        Args:
            card_id: Card ID to check

        Returns:
            True if checkpoint exists and can be resumed
        """
        # Guard: Repository must exist
        if not self.repository:
            return False

        # Guard: Checkpoint must exist
        if not self.repository.exists(card_id):
            return False

        # Load and validate checkpoint
        checkpoint = self.repository.load(card_id)

        # Guard: Checkpoint must load successfully
        if not checkpoint:
            return False

        # Validate resumability
        return self.validator.can_resume_checkpoint(checkpoint)

    def resume(self, card_id: str) -> Optional[PipelineCheckpoint]:
        """
        Resume from checkpoint

        Updates checkpoint metadata and returns restored checkpoint

        Args:
            card_id: Card ID to resume

        Returns:
            Restored checkpoint or None if cannot resume
        """
        # Guard: Cannot resume if not resumable
        if not self.can_resume(card_id):
            return None

        # Load checkpoint
        checkpoint = self.repository.load(card_id)

        # Guard: Checkpoint must exist
        if not checkpoint:
            return None

        # Update checkpoint for resumption
        checkpoint.status = CheckpointStatus.RESUMED
        checkpoint.resume_count += 1
        checkpoint.last_resume_time = datetime.now()
        checkpoint.updated_at = datetime.now()

        # Save updated checkpoint
        self.repository.save(checkpoint)

        return checkpoint

    def load_checkpoint(self, card_id: str) -> Optional[PipelineCheckpoint]:
        """
        Load checkpoint without resumption updates

        Used for read-only checkpoint access

        Args:
            card_id: Card ID to load

        Returns:
            Checkpoint if exists, None otherwise
        """
        return self.repository.load(card_id)


# ============================================================================
# LLM CACHE MANAGER
# ============================================================================

class LLMCacheManager:
    """
    Manages LLM response caching for checkpoint restoration

    Stores and retrieves LLM responses to avoid redundant calls
    when resuming from checkpoint.
    """

    def __init__(self, enabled: bool = True):
        """
        Initialize LLM cache manager

        Args:
            enabled: Enable/disable caching
        """
        self.enabled = enabled
        self.cache: Dict[str, Any] = {}
        self.key_generator = LLMCacheKeyGenerator()

    def store_response(
        self,
        card_id: str,
        stage_name: str,
        prompt: str,
        response: Dict[str, Any]
    ) -> None:
        """
        Store LLM response in cache

        Args:
            card_id: Card ID
            stage_name: Stage name
            prompt: LLM prompt
            response: LLM response to cache
        """
        # Guard: Skip if caching disabled
        if not self.enabled:
            return

        cache_key = self.key_generator.generate_cache_key(
            card_id,
            stage_name,
            prompt
        )
        self.cache[cache_key] = response

    def get_cached_response(
        self,
        card_id: str,
        stage_name: str,
        prompt: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached LLM response if available

        Args:
            card_id: Card ID
            stage_name: Stage name
            prompt: LLM prompt

        Returns:
            Cached response or None
        """
        # Guard: Return None if caching disabled
        if not self.enabled:
            return None

        cache_key = self.key_generator.generate_cache_key(
            card_id,
            stage_name,
            prompt
        )
        return self.cache.get(cache_key)

    def restore_cache_from_checkpoint(
        self,
        checkpoint: PipelineCheckpoint
    ) -> None:
        """
        Restore LLM cache from checkpoint data

        Populates cache with LLM responses from completed stages

        Args:
            checkpoint: Checkpoint containing LLM responses
        """
        # Guard: Skip if caching disabled
        if not self.enabled:
            return

        # Guard: Checkpoint must exist
        if not checkpoint:
            return

        # Restore responses from all stage checkpoints
        for stage_name, stage_cp in checkpoint.stage_checkpoints.items():
            for response in stage_cp.llm_responses:
                prompt = response.get("prompt", "")

                # Guard: Skip if no prompt
                if not prompt:
                    continue

                self.store_response(
                    checkpoint.card_id,
                    stage_name,
                    prompt,
                    response
                )

    def clear_cache(self) -> None:
        """Clear all cached responses"""
        self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache metrics
        """
        return {
            "enabled": self.enabled,
            "cached_responses": len(self.cache),
            "cache_keys": list(self.cache.keys())
        }


# ============================================================================
# CHECKPOINT STATE RESTORER
# ============================================================================

class CheckpointStateRestorer:
    """
    Restores complete execution state from checkpoint

    Coordinates checkpoint loading, validation, and cache restoration
    to fully restore pipeline execution state.
    """

    def __init__(
        self,
        repository: CheckpointRepository,
        cache_manager: LLMCacheManager
    ):
        """
        Initialize state restorer

        Args:
            repository: Checkpoint storage repository
            cache_manager: LLM cache manager
        """
        self.restorer = CheckpointRestorer(repository)
        self.cache_manager = cache_manager

    def restore_full_state(
        self,
        card_id: str
    ) -> Optional[PipelineCheckpoint]:
        """
        Restore complete checkpoint state including LLM cache

        Args:
            card_id: Card ID to restore

        Returns:
            Restored checkpoint or None
        """
        # Guard: Cannot resume if not resumable
        if not self.restorer.can_resume(card_id):
            return None

        # Resume checkpoint
        checkpoint = self.restorer.resume(card_id)

        # Guard: Checkpoint must exist
        if not checkpoint:
            return None

        # Restore LLM cache
        self.cache_manager.restore_cache_from_checkpoint(checkpoint)

        return checkpoint

    def can_resume(self, card_id: str) -> bool:
        """
        Check if state can be restored

        Args:
            card_id: Card ID to check

        Returns:
            True if can be restored
        """
        return self.restorer.can_resume(card_id)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_state_restorer(
    repository: CheckpointRepository,
    enable_llm_cache: bool = True
) -> CheckpointStateRestorer:
    """
    Factory function to create checkpoint state restorer

    Args:
        repository: Checkpoint storage repository
        enable_llm_cache: Enable LLM caching

    Returns:
        CheckpointStateRestorer instance
    """
    cache_manager = LLMCacheManager(enabled=enable_llm_cache)
    return CheckpointStateRestorer(repository, cache_manager)
