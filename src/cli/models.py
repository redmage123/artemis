"""
WHY: Define data models for CLI operations with type safety
RESPONSIBILITY: Provide typed data structures for commands and results
PATTERNS:
- Dataclass pattern for immutable configuration
- Type hints for all attributes
- Single Responsibility: One model per concept
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class CommandType(Enum):
    """Supported CLI command types"""
    INIT_PROMPTS = "init-prompts"
    TEST_CONFIG = "test-config"
    RUN = "run"
    CLEANUP = "cleanup"
    STATUS = "status"
    PROMPTS = "prompts"


class PromptAction(Enum):
    """Supported prompt management actions"""
    LIST = "list"
    SHOW = "show"
    SEARCH = "search"


@dataclass(frozen=True)
class CLIArguments:
    """
    Parsed command-line arguments

    Attributes:
        command: The command to execute
        verbose: Enable verbose output
        card_id: Card ID for run command
        full: Run full pipeline flag
        resume: Resume from checkpoint flag
        overrides: Hydra configuration overrides
        full_reset: Full reset flag for cleanup
        keep_checkpoints: Keep checkpoints flag
        action: Prompt action (list/show/search)
        name: Prompt name for show action
        query: Search query for search action
    """
    command: Optional[CommandType] = None
    verbose: bool = False

    # Run command arguments
    card_id: Optional[str] = None
    full: bool = False
    resume: bool = False
    overrides: List[str] = field(default_factory=list)

    # Cleanup command arguments
    full_reset: bool = False
    keep_checkpoints: bool = False

    # Prompts command arguments
    action: Optional[PromptAction] = None
    name: Optional[str] = None
    query: Optional[str] = None


@dataclass
class CommandResult:
    """
    Result of command execution

    Attributes:
        success: Whether command succeeded
        exit_code: Exit code (0 for success)
        message: Optional message to display
        data: Optional result data
    """
    success: bool
    exit_code: int
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

    @classmethod
    def success_result(cls, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> 'CommandResult':
        """Create a success result"""
        return cls(success=True, exit_code=0, message=message, data=data)

    @classmethod
    def failure_result(cls, exit_code: int = 1, message: Optional[str] = None) -> 'CommandResult':
        """Create a failure result"""
        return cls(success=False, exit_code=exit_code, message=message)


@dataclass(frozen=True)
class StoragePaths:
    """Storage paths configuration"""
    rag_db_path: str
    temp_dir: str
    checkpoint_dir: str
    state_dir: str
    adr_dir: str
    developer_output_dir: str
    message_dir: str


@dataclass(frozen=True)
class LLMConfig:
    """LLM configuration"""
    provider: str
    model: str


@dataclass
class SystemStatus:
    """
    System status information

    Attributes:
        storage_paths: Storage paths and their existence
        llm_config: LLM configuration
        kanban_stats: Kanban board statistics
        checkpoints: Recent checkpoint files
    """
    storage_paths: Dict[str, Dict[str, Any]]
    llm_config: LLMConfig
    kanban_stats: Dict[str, Any]
    checkpoints: List[str]
