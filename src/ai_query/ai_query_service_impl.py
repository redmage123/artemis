#!/usr/bin/env python3
"""
AI Query Service Implementation

WHY: Centralized service for orchestrating KG → RAG → LLM query pipeline.

RESPONSIBILITY:
- Execute complete AI query pipeline (KG → RAG → LLM)
- Enhance prompts with KG/RAG context
- Track token savings and costs
- Cache KG queries for performance
- Provide metrics and dashboards

PATTERNS:
- Guard clauses for early returns (no nested ifs)
- Strategy pattern for KG queries
- Extracted helper methods for clarity
- Exception wrapping for consistent error handling
"""

from typing import Dict, List, Optional, Any
import time
import json
import hashlib

from artemis_exceptions import (
    ArtemisException,
    KnowledgeGraphError,
    LLMError,
    wrap_exception
)
from debug_mixin import DebugMixin
from ai_query.query_type import QueryType
from ai_query.kg_context import KGContext
from ai_query.rag_context import RAGContext
from ai_query.llm_response import LLMResponse
from ai_query.ai_query_result import AIQueryResult
from ai_query.kg_query_strategy import KGQueryStrategy
from ai_query.requirements_kg_strategy import RequirementsKGStrategy
from ai_query.architecture_kg_strategy import ArchitectureKGStrategy
from ai_query.code_review_kg_strategy import CodeReviewKGStrategy
from ai_query.code_generation_kg_strategy import CodeGenerationKGStrategy
from ai_query.project_analysis_kg_strategy import ProjectAnalysisKGStrategy
from ai_query.error_recovery_kg_strategy import ErrorRecoveryKGStrategy
from ai_query.sprint_planning_kg_strategy import SprintPlanningKGStrategy
from ai_query.retrospective_kg_strategy import RetrospectiveKGStrategy
from ai_query.token_savings_tracker import TokenSavingsTracker
from ai_query.token_savings_metrics import TokenSavingsMetrics


class AIQueryService(DebugMixin):
    """
    Centralized AI Query Service - KG → RAG → LLM Pipeline

    Single service that all agents use to query the AI subsystem.
    Eliminates code duplication and ensures consistent KG-First approach.
    """

    def __init__(
        self,
        llm_client: Any,
        kg: Optional[Any] = None,
        rag: Optional[Any] = None,
        logger: Optional[Any] = None,
        enable_kg: bool = True,
        enable_rag: bool = True,
        verbose: bool = False
    ):
        """
        Initialize AI Query Service

        Args:
            llm_client: LLM client instance (required)
            kg: Knowledge Graph instance (optional)
            rag: RAG agent instance (optional)
            logger: Logger for events (optional)
            enable_kg: Enable KG-First queries (default: True)
            enable_rag: Enable RAG enhancement (default: True)
            verbose: Enable verbose logging (default: False)
        """
        DebugMixin.__init__(self, component_name="ai_query")
        self.llm_client = llm_client
        self.kg = kg
        self.rag = rag
        self.logger = logger
        self.enable_kg = enable_kg
        self.enable_rag = enable_rag
        self.verbose = verbose

        # Strategy registry
        self.strategies: Dict[QueryType, KGQueryStrategy] = {
            QueryType.REQUIREMENTS_PARSING: RequirementsKGStrategy(),
            QueryType.ARCHITECTURE_DESIGN: ArchitectureKGStrategy(),
            QueryType.CODE_REVIEW: CodeReviewKGStrategy(),
            QueryType.CODE_GENERATION: CodeGenerationKGStrategy(),
            QueryType.PROJECT_ANALYSIS: ProjectAnalysisKGStrategy(),
            QueryType.ERROR_RECOVERY: ErrorRecoveryKGStrategy(),
            QueryType.SPRINT_PLANNING: SprintPlanningKGStrategy(),
            QueryType.RETROSPECTIVE: RetrospectiveKGStrategy()
        }

        # Token savings tracker for metrics
        self.savings_tracker = TokenSavingsTracker()

        # KG query cache for performance optimization
        self.kg_cache: Dict[str, KGContext] = {}
        self.cache_enabled = True
        self.cache_max_age_seconds = 300  # 5 minutes

        if self.verbose and self.logger:
            self.logger.log("AI Query Service initialized with KG→RAG→LLM pipeline", "INFO")

    def query(
        self,
        query_type: QueryType,
        prompt: str,
        kg_query_params: Optional[Dict[str, Any]] = None,
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> AIQueryResult:
        """
        Execute complete AI query pipeline: KG → RAG → LLM

        Args:
            query_type: Type of query being performed
            prompt: Base LLM prompt (will be enhanced with KG/RAG context)
            kg_query_params: Parameters for KG query (query-specific)
            temperature: LLM temperature (default: 0.3)
            max_tokens: Max LLM tokens (default: 4000)

        Returns:
            AIQueryResult with complete pipeline results

        Raises:
            ArtemisException: If any stage fails critically
        """
        self.debug_trace("query",
                        query_type=query_type.value,
                        prompt_length=len(prompt),
                        temperature=temperature,
                        max_tokens=max_tokens,
                        kg_enabled=self.enable_kg,
                        rag_enabled=self.enable_rag)

        try:
            start_time = time.time()

            # Step 1: Query Knowledge Graph (KG-First)
            with self.debug_section("KG Query", query_type=query_type.value):
                kg_context = self._query_knowledge_graph(query_type, kg_query_params or {})
                if kg_context:
                    self.debug_log("KG patterns found",
                                  pattern_count=kg_context.pattern_count,
                                  estimated_token_savings=kg_context.estimated_token_savings)

            # Step 2: Query RAG for additional recommendations
            with self.debug_section("RAG Query", query_type=query_type.value):
                rag_context = self._query_rag(query_type, prompt)
                if rag_context and rag_context.recommendation_count > 0:
                    self.debug_log("RAG recommendations found",
                                  recommendation_count=rag_context.recommendation_count)

            # Step 3: Enhance prompt with KG + RAG context
            enhanced_prompt = self._enhance_prompt(prompt, kg_context, rag_context)
            self.debug_log("Prompt enhanced",
                          original_length=len(prompt),
                          enhanced_length=len(enhanced_prompt))

            # Step 4: Call LLM with enhanced prompt
            with self.debug_section("LLM Call", query_type=query_type.value):
                llm_response = self._call_llm(enhanced_prompt, temperature, max_tokens,
                                             kg_context.estimated_token_savings if kg_context else 0)
                self.debug_log("LLM response received",
                              tokens_used=llm_response.tokens_used,
                              tokens_saved=llm_response.tokens_saved,
                              cost_usd=f"${llm_response.cost_usd:.6f}")

            # Calculate total duration
            total_duration_ms = (time.time() - start_time) * 1000

            # Record metrics for tracking
            self.savings_tracker.record_query(
                query_type=query_type,
                tokens_used=llm_response.tokens_used,
                tokens_saved=llm_response.tokens_saved,
                cost_usd=llm_response.cost_usd,
                kg_patterns_found=kg_context.pattern_count if kg_context else 0
            )

            self.debug_log("Query pipeline completed",
                          total_duration_ms=f"{total_duration_ms:.2f}",
                          kg_patterns=kg_context.pattern_count if kg_context else 0,
                          tokens_saved=llm_response.tokens_saved)

            # Log success
            if self.verbose and self.logger:
                self.logger.log(
                    f"✅ AI Query completed: {query_type.value} "
                    f"(KG: {kg_context.pattern_count if kg_context else 0} patterns, "
                    f"Tokens saved: ~{llm_response.tokens_saved})",
                    "INFO"
                )

            return AIQueryResult(
                query_type=query_type,
                kg_context=kg_context,
                rag_context=rag_context,
                llm_response=llm_response,
                total_duration_ms=total_duration_ms,
                success=True,
                error=None
            )
        except ArtemisException as ae:
            # Re-raise Artemis exceptions as-is
            self.debug_log("AI Query failed with ArtemisException", error=str(ae))
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            self.debug_log("AI Query failed with unexpected exception", error=str(e))
            raise wrap_exception(e, ArtemisException,
                               f"AI Query pipeline failed: {str(e)}")

    def _query_knowledge_graph(
        self,
        query_type: QueryType,
        query_params: Dict[str, Any]
    ) -> Optional[KGContext]:
        """
        Query Knowledge Graph for patterns (Step 1) with caching

        Args:
            query_type: Type of query
            query_params: Query-specific parameters

        Returns:
            KGContext with patterns found, or None if KG unavailable
        """
        try:
            # Guard clause: KG not available
            if not self.enable_kg or not self.kg:
                return None

            # Guard clause: No strategy for this query type
            strategy = self.strategies.get(query_type)
            if not strategy:
                self._log_no_kg_strategy(query_type)
                return None

            # Check cache first (if enabled)
            cache_key = self._generate_cache_key(query_type, query_params)
            cached_result = self._check_kg_cache(cache_key, query_type)
            if cached_result is not None:
                return cached_result

            # Execute KG query
            kg_context = strategy.query_kg(self.kg, query_params)

            # Store in cache
            self._store_in_kg_cache(cache_key, kg_context)

            # Log success
            self._log_kg_patterns_found(query_type, kg_context)

            return kg_context
        except KnowledgeGraphError:
            # Already wrapped, re-raise
            raise
        except Exception as e:
            # Log error but don't fail the entire pipeline
            if self.logger:
                self.logger.log(f"KG query failed (continuing without KG): {str(e)}", "WARNING")
            return None

    def _log_no_kg_strategy(self, query_type: QueryType) -> None:
        """
        Log when no KG strategy is available.

        WHY: Extracted to avoid nested if in _query_knowledge_graph (Early Return Pattern).

        Args:
            query_type: Query type that has no strategy
        """
        if self.verbose and self.logger:
            self.logger.log(f"No KG strategy for {query_type.value} - skipping KG", "DEBUG")

    def _generate_cache_key(self, query_type: QueryType, query_params: Dict[str, Any]) -> Optional[str]:
        """
        Generate cache key for KG query.

        WHY: Extracted to simplify cache logic (DRY principle).

        Args:
            query_type: Type of query
            query_params: Query parameters

        Returns:
            Cache key string, or None if caching disabled
        """
        # Guard clause: Caching disabled
        if not self.cache_enabled:
            return None

        cache_data = f"{query_type.value}:{json.dumps(query_params, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _check_kg_cache(self, cache_key: Optional[str], query_type: QueryType) -> Optional[KGContext]:
        """
        Check KG cache for cached results.

        WHY: Extracted to avoid nested if statements (Early Return Pattern).

        Args:
            cache_key: Cache key to check
            query_type: Query type (for logging)

        Returns:
            Cached KGContext if found, None otherwise
        """
        # Guard clause: Caching disabled or no cache key
        if not cache_key:
            return None

        # Guard clause: Cache miss
        if cache_key not in self.kg_cache:
            return None

        # Cache hit - log and return
        cached_result = self.kg_cache[cache_key]
        if self.verbose and self.logger:
            self.logger.log(f"💾 KG cache hit for {query_type.value}", "DEBUG")
        return cached_result

    def _store_in_kg_cache(self, cache_key: Optional[str], kg_context: Optional[KGContext]) -> None:
        """
        Store KG query result in cache.

        WHY: Extracted to avoid nested if statements (Early Return Pattern).

        Args:
            cache_key: Cache key for storage
            kg_context: KG context to cache
        """
        # Guard clause: Caching disabled or invalid inputs
        if not self.cache_enabled:
            return
        if not cache_key:
            return
        if not kg_context:
            return

        # Store in cache
        self.kg_cache[cache_key] = kg_context

        # Enforce cache size limit
        self._enforce_cache_size_limit()

    def _enforce_cache_size_limit(self) -> None:
        """
        Enforce cache size limit by removing oldest entries.

        WHY: Extracted to avoid nested if statements (Early Return Pattern).
        PERFORMANCE: Simple FIFO eviction, O(1) removal.
        """
        # Guard clause: Cache within limits
        if len(self.kg_cache) <= 100:
            return

        # Remove oldest entry (simple FIFO)
        oldest_key = next(iter(self.kg_cache))
        del self.kg_cache[oldest_key]

    def _log_kg_patterns_found(self, query_type: QueryType, kg_context: Optional[KGContext]) -> None:
        """
        Log KG patterns found.

        WHY: Extracted to avoid nested if in _query_knowledge_graph (Early Return Pattern).

        Args:
            query_type: Query type
            kg_context: KG context with patterns
        """
        # Guard clause: Verbose logging disabled
        if not self.verbose or not self.logger:
            return

        # Guard clause: No context or no patterns
        if not kg_context or kg_context.pattern_count == 0:
            return

        self.logger.log(
            f"📊 KG found {kg_context.pattern_count} patterns for {query_type.value} "
            f"(~{kg_context.estimated_token_savings} tokens saved)",
            "INFO"
        )

    def _query_rag(
        self,
        query_type: QueryType,
        prompt: str
    ) -> Optional[RAGContext]:
        """
        Query RAG for recommendations (Step 2)

        Args:
            query_type: Type of query
            prompt: Base prompt (used to find relevant RAG content)

        Returns:
            RAGContext with recommendations, or None if RAG unavailable
        """
        try:
            # Guard clause: RAG not available
            if not self.enable_rag or not self.rag:
                return None

            # Guard clause: RAG doesn't have get_recommendations method
            if not hasattr(self.rag, 'get_recommendations'):
                return None

            # Query RAG for recommendations
            recommendations = self.rag.get_recommendations(prompt[:500])  # First 500 chars

            # Guard clause: No recommendations found
            if not recommendations:
                return None

            if self.verbose and self.logger:
                self.logger.log(
                    f"📚 RAG found {len(recommendations)} recommendations",
                    "INFO"
                )

            return RAGContext(
                recommendations=recommendations,
                recommendation_count=len(recommendations),
                rag_available=True
            )
        except Exception as e:
            # Log error but don't fail the entire pipeline
            if self.logger:
                self.logger.log(f"RAG query failed (continuing without RAG): {str(e)}", "WARNING")
            return RAGContext(
                recommendations=[],
                recommendation_count=0,
                rag_available=False,
                error=str(e)
            )

    def _enhance_prompt(
        self,
        base_prompt: str,
        kg_context: Optional[KGContext],
        rag_context: Optional[RAGContext]
    ) -> str:
        """
        Enhance prompt with KG + RAG context (Step 3)

        Args:
            base_prompt: Original prompt
            kg_context: KG patterns (if available)
            rag_context: RAG recommendations (if available)

        Returns:
            Enhanced prompt with KG and RAG context
        """
        try:
            enhanced_parts = [base_prompt]

            # Add KG context
            if kg_context and kg_context.pattern_count > 0:
                enhanced_parts.append("\n\n" + "="*80)
                enhanced_parts.append("\n**Knowledge Graph Context (use as reference):**\n")
                enhanced_parts.append(f"Found {kg_context.pattern_count} similar patterns:\n")

                for i, pattern in enumerate(kg_context.patterns_found[:5], 1):
                    pattern_summary = json.dumps(pattern, indent=2)
                    enhanced_parts.append(f"\n**Pattern {i}:**\n```json\n{pattern_summary}\n```")

                enhanced_parts.append("\n**NOTE**: Use these patterns as guidance, adapt to your specific task.")
                enhanced_parts.append("\n" + "="*80 + "\n")

            # Add RAG context
            if rag_context and rag_context.recommendation_count > 0:
                enhanced_parts.append("\n\n" + "="*80)
                enhanced_parts.append("\n**Historical Recommendations (RAG):**\n")
                for i, rec in enumerate(rag_context.recommendations[:3], 1):
                    enhanced_parts.append(f"{i}. {rec}\n")
                enhanced_parts.append("="*80 + "\n")

            return "".join(enhanced_parts)
        except Exception as e:
            # If enhancement fails, return base prompt
            if self.logger:
                self.logger.log(f"Prompt enhancement failed: {str(e)}", "WARNING")
            return base_prompt

    def _call_llm(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        estimated_tokens_saved: int
    ) -> LLMResponse:
        """
        Call LLM with enhanced prompt (Step 4)

        Args:
            prompt: Enhanced prompt
            temperature: LLM temperature
            max_tokens: Max tokens
            estimated_tokens_saved: Estimated savings from KG-First

        Returns:
            LLMResponse with result

        Raises:
            LLMError: If LLM call fails
        """
        try:
            # Call LLM
            response = self.llm_client.generate_text(
                system_message="You are a helpful AI assistant.",
                user_message=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract content if response is LLMResponse object
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Calculate tokens and cost (approximate)
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(response_text.split()) * 1.3
            total_tokens = int(input_tokens + output_tokens)

            # Rough cost calculation (GPT-4 pricing: $10/1M input, $30/1M output)
            cost_usd = (input_tokens / 1_000_000 * 10) + (output_tokens / 1_000_000 * 30)

            return LLMResponse(
                content=response_text,
                tokens_used=total_tokens,
                tokens_saved=estimated_tokens_saved,
                cost_usd=cost_usd,
                model=getattr(self.llm_client, 'model', 'unknown'),
                temperature=temperature,
                error=None
            )
        except Exception as e:
            raise wrap_exception(e, LLMError,
                               f"LLM call failed: {str(e)}")

    def get_metrics(self, query_type: Optional[QueryType] = None) -> TokenSavingsMetrics:
        """
        Get token savings metrics

        Args:
            query_type: Optional query type to filter by

        Returns:
            TokenSavingsMetrics for the specified query type or overall
        """
        return self.savings_tracker.get_metrics(query_type)

    def print_metrics_dashboard(self):
        """Print comprehensive metrics dashboard"""
        self.savings_tracker.print_dashboard()

    def clear_cache(self):
        """Clear the KG query cache"""
        self.kg_cache.clear()
        if self.verbose and self.logger:
            self.logger.log("🧹 KG query cache cleared", "INFO")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dict with cache size and hit rate
        """
        return {
            'cache_size': len(self.kg_cache),
            'cache_enabled': self.cache_enabled,
            'cache_max_age_seconds': self.cache_max_age_seconds
        }
