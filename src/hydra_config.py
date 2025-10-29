#!/usr/bin/env python3
"""
Hydra Structured Configurations for Artemis

Type-safe configuration dataclasses that work with Hydra.
Provides IDE autocomplete, validation, and better error messages.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from hydra.core.config_store import ConfigStore


@dataclass
class LLMConfig:
    """
    LLM Provider Configuration

    Controls which LLM provider and model to use for code generation.

    Why this exists: Centralizes all LLM-related configuration in one place,
    making it easy to switch providers or models without code changes.

    Attributes:
        provider: LLM provider name (openai, anthropic, or mock)
        model: Specific model to use (e.g., gpt-4o, claude-3-opus). If None, uses provider default
        api_key: API key for authentication. If None, reads from environment variables
        max_tokens_per_request: Maximum tokens to request per API call (prevents runaway costs)
        temperature: Sampling temperature (0.0-1.0). Lower = more deterministic, higher = more creative
        top_k: Number of top tokens to consider (RAG retrieval)
        cost_limit_usd: Optional daily cost limit to prevent overspending
    """
    provider: str = "openai"  # openai, anthropic, or mock
    model: Optional[str] = None  # Specific model (e.g., gpt-4o, claude-3-opus)
    api_key: Optional[str] = None  # API key (read from env typically)
    max_tokens_per_request: int = 2000
    temperature: float = 0.3
    top_k: int = 5  # RAG retrieval top-k
    cost_limit_usd: Optional[float] = None  # Daily cost limit


@dataclass
class StorageConfig:
    """
    Storage Configuration

    Controls where Artemis stores RAG database, checkpoints, and temporary files.
    Paths are relative to .agents/agile directory unless overridden by env vars.

    Why this exists: Provides flexible storage configuration for different deployment
    environments (local dev, CI/CD, production) without code changes.

    Attributes:
        rag_db_type: Type of database for RAG (sqlite for local dev, postgres for production)
        rag_db_path: File path for SQLite database (relative to .agents/agile)
        chromadb_host: PostgreSQL host for ChromaDB vector storage (production only)
        chromadb_port: PostgreSQL port for ChromaDB vector storage
        temp_dir: Directory for temporary files (cleared periodically)
        checkpoint_dir: Directory for pipeline checkpoints (enables resume on failure)
        state_dir: Directory for persistent state (kanban board, metrics)
    """
    rag_db_type: str = "sqlite"  # sqlite or postgres
    rag_db_path: Optional[str] = "db"  # Path for SQLite (relative to .agents/agile)
    chromadb_host: Optional[str] = None  # Host for PostgreSQL-backed ChromaDB
    chromadb_port: Optional[int] = None  # Port for PostgreSQL-backed ChromaDB
    temp_dir: str = "../../.artemis_data/temp"
    checkpoint_dir: str = "../../.artemis_data/checkpoints"
    state_dir: str = "../../.artemis_data/state"


@dataclass
class TimeoutConfig:
    """Timeout Configuration - All values in seconds"""
    build: int = 600  # Build operations
    test: int = 300  # Test execution
    redis_socket: int = 5  # Redis socket operations
    redis_connect: int = 5  # Redis connection
    dependency_check: int = 300  # Dependency validation
    unreal_engine: int = 1800  # Unreal Engine builds
    default: int = 120  # Default timeout


@dataclass
class RetryConfig:
    """Retry Configuration"""
    max_retries: int = 2  # Maximum retry attempts
    initial_delay: float = 2.0  # Initial delay in seconds
    max_delay: float = 60.0  # Maximum delay in seconds
    backoff_multiplier: float = 2.0  # Exponential backoff multiplier


@dataclass
class ParallelismConfig:
    """Parallelism Configuration"""
    max_workers: int = 4  # Worker threads
    max_parallel_developers: int = 2  # Parallel developer agents
    max_parallel_stages: int = 2  # Parallel stages
    max_parallel_tests: int = 4  # Parallel test execution
    thread_pool_size: int = 8  # Thread pool size
    prefetch_count: int = 1  # Message prefetch count


@dataclass
class BatchConfig:
    """Batch Processing Configuration"""
    default_size: int = 100  # Default batch size
    rag_query_size: int = 50  # RAG query batch size
    small_memory_size: int = 25  # Batch size for low memory systems


@dataclass
class ComplexityConfig:
    """Complexity Thresholds"""
    low_threshold: int = 50  # Simple task threshold
    medium_threshold: int = 200  # Medium task threshold
    high_threshold: int = 500  # Complex task threshold
    max_cyclomatic: int = 10  # Maximum cyclomatic complexity


@dataclass
class ValidationConfig:
    """Validation Configuration"""
    pass_threshold: float = 0.8  # Minimum pass score (0.0-1.0)
    confidence_threshold: float = 0.7  # Minimum confidence score
    min_similarity: float = 0.3  # Minimum RAG similarity
    enable_type_checking: bool = True
    enable_linting: bool = True
    enable_complexity_check: bool = True


@dataclass
class MemoryConfig:
    """Memory Allocation Configuration - All values in MB/GB"""
    per_agent_gb: float = 1.0  # Memory per agent in GB
    sandbox_max_mb: int = 512  # Sandbox memory limit in MB
    logger_max_mb: int = 100  # Log file size limit in MB


@dataclass
class CacheConfig:
    """Cache Configuration"""
    lru_maxsize: int = 256  # LRU cache size
    plan_cache_size: int = 100  # Plan cache size
    query_cache_size: int = 1000  # Query cache size
    ttl_seconds: int = 3600  # Cache TTL


@dataclass
class FeatureFlagsConfig:
    """Feature Flags"""
    enable_llm_analysis: bool = True
    enable_rag_validation: bool = True
    enable_self_critique: bool = True
    enable_dynamic_pipeline: bool = True
    enable_two_pass: bool = False
    enable_thermodynamic: bool = True
    enable_property_tests: bool = True


@dataclass
class SkipFlagsConfig:
    """Stage Skip Flags"""
    skip_sprint_planning: bool = False
    skip_project_analysis: bool = False
    skip_arbitration: bool = False


@dataclass
class RateLimitConfig:
    """Rate Limiting Configuration"""
    default_limit: int = 100
    window_seconds: int = 60
    failure_threshold: int = 5
    success_threshold: int = 2


@dataclass
class PipelineConfig:
    """
    Pipeline Execution Configuration

    Controls how the Artemis pipeline executes stages.
    """
    # Original fields
    max_parallel_developers: int = 2  # Number of parallel developer agents
    enable_code_review: bool = True  # Enable code review stage
    auto_approve_project_analysis: bool = False  # Auto-approve project analysis
    enable_supervision: bool = True  # Enable supervisor agent
    max_retries: int = 2  # Max retries for failed code reviews
    stages: List[str] = field(default_factory=lambda: [
        "project_analysis",
        "architecture",
        "dependencies",
        "development",
        "code_review",
        "validation",
        "integration",
        "testing"
    ])

    # Comprehensive hyperparameters
    timeouts: TimeoutConfig = field(default_factory=TimeoutConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    parallelism: ParallelismConfig = field(default_factory=ParallelismConfig)
    batch: BatchConfig = field(default_factory=BatchConfig)
    complexity: ComplexityConfig = field(default_factory=ComplexityConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    features: FeatureFlagsConfig = field(default_factory=FeatureFlagsConfig)
    skip_flags: SkipFlagsConfig = field(default_factory=SkipFlagsConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)


@dataclass
class SecurityConfig:
    """
    Security and Compliance Configuration

    Controls security checks and compliance enforcement.
    """
    enforce_gdpr: bool = True  # Enforce GDPR compliance
    enforce_wcag: bool = True  # Enforce WCAG accessibility
    require_security_review: bool = True  # Require security review
    min_code_review_score: int = 80  # Minimum acceptable code review score


@dataclass
class LoggingConfig:
    """
    Logging Configuration

    Controls logging verbosity and output.
    """
    verbose: bool = True  # Enable verbose logging
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR


@dataclass
class ArtemisConfig:
    """
    Complete Artemis Configuration

    Top-level configuration containing all sub-configurations.
    This is the root config object used throughout Artemis.
    """
    # Card ID (required - must be provided via CLI)
    card_id: str = "???"  # ??? means required by Hydra

    # Sub-configurations
    llm: LLMConfig = field(default_factory=LLMConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


def register_configs():
    """
    Register all configs with Hydra ConfigStore

    This allows Hydra to provide type-safe config composition.

    Why this exists: Enables Hydra's powerful configuration composition features,
    allowing users to override specific config groups via CLI or config files.

    What it does:
    - Registers main ArtemisConfig as default config schema
    - Registers each config group (llm, storage, pipeline, etc.) separately
    - Enables CLI overrides like: python app.py llm.provider=anthropic
    - Provides IDE autocomplete and type checking for config values

    When called: Automatically on module import (see bottom of file)
    """
    cs = ConfigStore.instance()

    # Register main config
    cs.store(name="artemis_config", node=ArtemisConfig)

    # Register config groups
    cs.store(group="llm", name="base_llm", node=LLMConfig)
    cs.store(group="storage", name="base_storage", node=StorageConfig)
    cs.store(group="pipeline", name="base_pipeline", node=PipelineConfig)
    cs.store(group="security", name="base_security", node=SecurityConfig)
    cs.store(group="logging", name="base_logging", node=LoggingConfig)


# Register configs when module is imported
register_configs()
