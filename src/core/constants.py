from artemis_logger import get_logger
logger = get_logger('constants')
'\nModule: core/constants.py\n\nArtemis Configuration Constants\n\nCentralized constants for paths, timeouts, limits, and other configuration values.\nThis eliminates hard-coded values and magic numbers throughout the codebase.\n\nWHY: Single source of truth for all configuration values.\nRESPONSIBILITY: Define all system-wide constants and configuration helpers.\nPATTERNS: Configuration module, Constants pattern, Helper functions for path resolution.\n\nDependencies: None (core module - no Artemis dependencies)\n'
import os
from pathlib import Path
REPO_ROOT = Path(os.environ.get('ARTEMIS_REPO_ROOT', Path(__file__).parent.parent.parent.absolute()))
AGENTS_DIR = REPO_ROOT / '.agents'
AGILE_DIR = AGENTS_DIR / 'agile'
KANBAN_BOARD_PATH = AGILE_DIR / 'kanban_board.json'
DEVELOPER_A_PROMPT_PATH = AGENTS_DIR / 'developer_a_prompt.md'
DEVELOPER_B_PROMPT_PATH = AGENTS_DIR / 'developer_b_prompt.md'
PYTEST_PATH = os.environ.get('ARTEMIS_PYTEST_PATH', 'pytest')
DEFAULT_DATA_DIR = REPO_ROOT / '.artemis_data'
DEFAULT_OUTPUT_DIR = DEFAULT_DATA_DIR / 'temp'
DEFAULT_DEVELOPER_A_DIR = DEFAULT_DATA_DIR / 'developer_output' / 'developer-a'
DEFAULT_DEVELOPER_B_DIR = DEFAULT_DATA_DIR / 'developer_output' / 'developer-b'
DEFAULT_RAG_DB_PATH = DEFAULT_DATA_DIR / 'rag_db'
DEFAULT_CHECKPOINT_DIR = DEFAULT_DATA_DIR / 'checkpoints'
DEFAULT_RETRY_INTERVAL_SECONDS = 5
MAX_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2
LLM_REQUEST_TIMEOUT_SECONDS = 300
LLM_STREAM_TIMEOUT_SECONDS = 600
DEVELOPER_AGENT_TIMEOUT_SECONDS = 3600
CODE_REVIEW_TIMEOUT_SECONDS = 1800
STAGE_TIMEOUT_SECONDS = 3600
FULL_PIPELINE_TIMEOUT_SECONDS = 14400
MAX_LLM_PROMPT_LENGTH = 8000
MAX_LLM_RESPONSE_LENGTH = 4000
MAX_CONTEXT_TOKENS = 100000
DEFAULT_LLM_PROVIDER = 'openai'
DEFAULT_LLM_MODEL = 'gpt-5'
DEFAULT_LLM_TEMPERATURE = 0.7
DEFAULT_LLM_MAX_TOKENS = 4000
DEFAULT_COST_LIMIT_USD = 100.0
COST_WARNING_THRESHOLD_USD = 75.0
DEFAULT_REQUESTS_PER_MINUTE = 10
DEFAULT_REQUESTS_PER_HOUR = 500
STAGE_PROJECT_ANALYSIS = 'project_analysis'
STAGE_ARCHITECTURE = 'architecture'
STAGE_DEPENDENCIES = 'dependencies'
STAGE_DEVELOPMENT = 'development'
STAGE_CODE_REVIEW = 'code_review'
STAGE_VALIDATION = 'validation'
STAGE_INTEGRATION = 'integration'
STAGE_TESTING = 'testing'
DEFAULT_PIPELINE_STAGES = [STAGE_PROJECT_ANALYSIS, STAGE_ARCHITECTURE, STAGE_DEPENDENCIES, STAGE_DEVELOPMENT, STAGE_CODE_REVIEW, STAGE_VALIDATION, STAGE_INTEGRATION, STAGE_TESTING]
MAX_PARALLEL_DEVELOPERS = 2
DEFAULT_ENABLE_SUPERVISION = True
DEFAULT_ENABLE_CHECKPOINTS = True
CODE_REVIEW_PASSING_SCORE = 70
CODE_REVIEW_WARNING_SCORE = 50
MAX_CODE_REVIEW_RETRIES = 3
REVIEW_CATEGORY_SECURITY = 'security'
REVIEW_CATEGORY_QUALITY = 'quality'
REVIEW_CATEGORY_PERFORMANCE = 'performance'
REVIEW_CATEGORY_MAINTAINABILITY = 'maintainability'
KANBAN_COLUMN_BACKLOG = 'backlog'
KANBAN_COLUMN_IN_PROGRESS = 'in_progress'
KANBAN_COLUMN_REVIEW = 'review'
KANBAN_COLUMN_DONE = 'done'
KANBAN_WIP_LIMIT_IN_PROGRESS = 3
KANBAN_WIP_LIMIT_REVIEW = 2
PRIORITY_HIGH = 'high'
PRIORITY_MEDIUM = 'medium'
PRIORITY_LOW = 'low'
DEFAULT_RAG_COLLECTION_NAME = 'artemis_artifacts'
RAG_SIMILARITY_TOP_K = 5
RAG_SIMILARITY_THRESHOLD = 0.7
ARTIFACT_TYPE_PROJECT_ANALYSIS = 'project_analysis'
ARTIFACT_TYPE_ARCHITECTURE = 'architecture'
ARTIFACT_TYPE_CODE = 'code'
ARTIFACT_TYPE_TEST = 'test'
ARTIFACT_TYPE_REVIEW = 'code_review'
ARTIFACT_TYPE_ADR = 'architecture_decision_record'
SUPERVISOR_CONFIDENCE_THRESHOLD = 0.8
SUPERVISOR_MAX_INTERVENTIONS = 5
STATE_IDLE = 'idle'
STATE_PLANNING = 'planning'
STATE_EXECUTING = 'executing'
STATE_REVIEWING = 'reviewing'
STATE_FAILED = 'failed'
STATE_COMPLETED = 'completed'
PYTHON_FILE_PATTERN = '**/*.py'
JAVASCRIPT_FILE_PATTERN = '**/*.js'
TYPESCRIPT_FILE_PATTERN = '**/*.ts'
TEST_FILE_PATTERN = '**/test_*.py'
EXCLUDE_PATTERNS = ['**/__pycache__/**', '**/venv/**', '**/.venv/**', '**/node_modules/**', '**/.git/**', '**/*.pyc']
LOG_LEVEL_DEBUG = 'DEBUG'
LOG_LEVEL_INFO = 'INFO'
LOG_LEVEL_WARNING = 'WARNING'
LOG_LEVEL_ERROR = 'ERROR'
DEFAULT_LOG_LEVEL = LOG_LEVEL_INFO
LOG_FORMAT_SIMPLE = '%(levelname)s: %(message)s'
LOG_FORMAT_DETAILED = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FORMAT_JSON = 'json'
DEFAULT_MEMGRAPH_HOST = 'localhost'
DEFAULT_MEMGRAPH_PORT = 7687
DEFAULT_MEMGRAPH_LAB_PORT = 7444
DEFAULT_REDIS_HOST = 'localhost'
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_DB = 0
MIN_STORY_POINTS = 1
MAX_STORY_POINTS = 21
MAX_CYCLOMATIC_COMPLEXITY = 10
MAX_FUNCTION_LENGTH_LINES = 50
MAX_FILE_LENGTH_LINES = 300
MAX_METHOD_PARAMETERS = 5
MIN_TEST_COVERAGE_PERCENT = 80
MIN_TESTS_PER_FEATURE = 3

def get_developer_prompt_path(agent_name: str) -> Path:
    """
    Get the prompt file path for a developer agent.

    WHAT: Maps developer agent names to their corresponding prompt file paths.
    WHY: Centralizes the mapping logic so agent names can vary while file locations stay consistent.
         This allows flexible agent naming (dev-a, developer-a, a all map to same file).

    Args:
        agent_name: Name of the developer agent (e.g., "developer-a")

    Returns:
        Path to the prompt file

    Raises:
        ValueError: If agent_name is not recognized
    """
    if agent_name.lower() in ['developer-a', 'dev-a', 'a']:
        return DEVELOPER_A_PROMPT_PATH
    elif agent_name.lower() in ['developer-b', 'dev-b', 'b']:
        return DEVELOPER_B_PROMPT_PATH
    else:
        return DEVELOPER_A_PROMPT_PATH

def get_developer_output_dir(agent_name: str) -> Path:
    """
    Get the output directory for a developer agent.

    WHAT: Maps developer agent names to their dedicated output directories.
    WHY: Separates outputs from different developers to prevent conflicts and enable
         side-by-side comparison of their work during arbitration.

    Args:
        agent_name: Name of the developer agent

    Returns:
        Path to the output directory
    """
    if agent_name.lower() in ['developer-a', 'dev-a', 'a']:
        return DEFAULT_DEVELOPER_A_DIR
    elif agent_name.lower() in ['developer-b', 'dev-b', 'b']:
        return DEFAULT_DEVELOPER_B_DIR
    else:
        return DEFAULT_OUTPUT_DIR / agent_name.lower()

def ensure_directory_exists(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    WHAT: Creates directory and all parent directories if they don't exist.
    WHY: Prevents file write failures by ensuring the directory structure exists first.
         Returns path to enable method chaining for cleaner code.

    Args:
        path: Path to the directory

    Returns:
        The path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path

def validate_config():
    """
    Validate that all required paths and configurations are accessible.

    WHAT: Checks that critical directories exist and configuration values are valid.
    WHY: Fail fast with clear errors during startup rather than cryptic failures later.
         Validates numeric constants are in sensible ranges to prevent misconfiguration.

    Raises:
        FileNotFoundError: If required files are missing
        ValueError: If configuration is invalid
    """
    if not REPO_ROOT.exists():
        raise FileNotFoundError(f'Repository root not found: {REPO_ROOT}')
    if not AGILE_DIR.exists():
        raise FileNotFoundError(f'Agile directory not found: {AGILE_DIR}')
    if MAX_RETRY_ATTEMPTS < 1:
        raise ValueError(f'MAX_RETRY_ATTEMPTS must be >= 1, got {MAX_RETRY_ATTEMPTS}')
    if CODE_REVIEW_PASSING_SCORE < 0 or CODE_REVIEW_PASSING_SCORE > 100:
        raise ValueError(f'CODE_REVIEW_PASSING_SCORE must be 0-100, got {CODE_REVIEW_PASSING_SCORE}')
    return True
if __name__ == '__main__':
    
    logger.log('=' * 70, 'INFO')
    
    logger.log('ARTEMIS CONFIGURATION CONSTANTS', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    
    logger.log(f'\nRepository Root: {REPO_ROOT}', 'INFO')
    
    logger.log(f'Agents Directory: {AGENTS_DIR}', 'INFO')
    
    logger.log(f'Agile Directory: {AGILE_DIR}', 'INFO')
    
    logger.log(f'\nKanban Board: {KANBAN_BOARD_PATH}', 'INFO')
    
    logger.log(f'Developer A Prompt: {DEVELOPER_A_PROMPT_PATH}', 'INFO')
    
    logger.log(f'Developer B Prompt: {DEVELOPER_B_PROMPT_PATH}', 'INFO')
    
    logger.log(f'\nPytest Path: {PYTEST_PATH}', 'INFO')
    
    logger.log(f'RAG Database: {DEFAULT_RAG_DB_PATH}', 'INFO')
    
    logger.log(f'Checkpoint Dir: {DEFAULT_CHECKPOINT_DIR}', 'INFO')
    
    logger.log(f'\nMax Retry Attempts: {MAX_RETRY_ATTEMPTS}', 'INFO')
    
    logger.log(f'Retry Interval: {DEFAULT_RETRY_INTERVAL_SECONDS}s', 'INFO')
    
    logger.log(f'Code Review Passing Score: {CODE_REVIEW_PASSING_SCORE}', 'INFO')
    
    logger.log(f'Max Parallel Developers: {MAX_PARALLEL_DEVELOPERS}', 'INFO')
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('VALIDATION', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    try:
        validate_config()
        
        logger.log('✅ Configuration is valid', 'INFO')
    except Exception as e:
        
        logger.log(f'❌ Configuration error: {e}', 'INFO')
        exit(1)
__all__ = ['REPO_ROOT', 'AGENTS_DIR', 'AGILE_DIR', 'KANBAN_BOARD_PATH', 'DEVELOPER_A_PROMPT_PATH', 'DEVELOPER_B_PROMPT_PATH', 'PYTEST_PATH', 'DEFAULT_DATA_DIR', 'DEFAULT_OUTPUT_DIR', 'DEFAULT_DEVELOPER_A_DIR', 'DEFAULT_DEVELOPER_B_DIR', 'DEFAULT_RAG_DB_PATH', 'DEFAULT_CHECKPOINT_DIR', 'DEFAULT_RETRY_INTERVAL_SECONDS', 'MAX_RETRY_ATTEMPTS', 'RETRY_BACKOFF_FACTOR', 'LLM_REQUEST_TIMEOUT_SECONDS', 'LLM_STREAM_TIMEOUT_SECONDS', 'DEVELOPER_AGENT_TIMEOUT_SECONDS', 'CODE_REVIEW_TIMEOUT_SECONDS', 'STAGE_TIMEOUT_SECONDS', 'FULL_PIPELINE_TIMEOUT_SECONDS', 'MAX_LLM_PROMPT_LENGTH', 'MAX_LLM_RESPONSE_LENGTH', 'MAX_CONTEXT_TOKENS', 'DEFAULT_LLM_PROVIDER', 'DEFAULT_LLM_MODEL', 'DEFAULT_LLM_TEMPERATURE', 'DEFAULT_LLM_MAX_TOKENS', 'DEFAULT_COST_LIMIT_USD', 'COST_WARNING_THRESHOLD_USD', 'DEFAULT_REQUESTS_PER_MINUTE', 'DEFAULT_REQUESTS_PER_HOUR', 'STAGE_PROJECT_ANALYSIS', 'STAGE_ARCHITECTURE', 'STAGE_DEPENDENCIES', 'STAGE_DEVELOPMENT', 'STAGE_CODE_REVIEW', 'STAGE_VALIDATION', 'STAGE_INTEGRATION', 'STAGE_TESTING', 'DEFAULT_PIPELINE_STAGES', 'MAX_PARALLEL_DEVELOPERS', 'DEFAULT_ENABLE_SUPERVISION', 'DEFAULT_ENABLE_CHECKPOINTS', 'CODE_REVIEW_PASSING_SCORE', 'CODE_REVIEW_WARNING_SCORE', 'MAX_CODE_REVIEW_RETRIES', 'REVIEW_CATEGORY_SECURITY', 'REVIEW_CATEGORY_QUALITY', 'REVIEW_CATEGORY_PERFORMANCE', 'REVIEW_CATEGORY_MAINTAINABILITY', 'KANBAN_COLUMN_BACKLOG', 'KANBAN_COLUMN_IN_PROGRESS', 'KANBAN_COLUMN_REVIEW', 'KANBAN_COLUMN_DONE', 'KANBAN_WIP_LIMIT_IN_PROGRESS', 'KANBAN_WIP_LIMIT_REVIEW', 'PRIORITY_HIGH', 'PRIORITY_MEDIUM', 'PRIORITY_LOW', 'DEFAULT_RAG_COLLECTION_NAME', 'RAG_SIMILARITY_TOP_K', 'RAG_SIMILARITY_THRESHOLD', 'ARTIFACT_TYPE_PROJECT_ANALYSIS', 'ARTIFACT_TYPE_ARCHITECTURE', 'ARTIFACT_TYPE_CODE', 'ARTIFACT_TYPE_TEST', 'ARTIFACT_TYPE_REVIEW', 'ARTIFACT_TYPE_ADR', 'SUPERVISOR_CONFIDENCE_THRESHOLD', 'SUPERVISOR_MAX_INTERVENTIONS', 'STATE_IDLE', 'STATE_PLANNING', 'STATE_EXECUTING', 'STATE_REVIEWING', 'STATE_FAILED', 'STATE_COMPLETED', 'PYTHON_FILE_PATTERN', 'JAVASCRIPT_FILE_PATTERN', 'TYPESCRIPT_FILE_PATTERN', 'TEST_FILE_PATTERN', 'EXCLUDE_PATTERNS', 'LOG_LEVEL_DEBUG', 'LOG_LEVEL_INFO', 'LOG_LEVEL_WARNING', 'LOG_LEVEL_ERROR', 'DEFAULT_LOG_LEVEL', 'LOG_FORMAT_SIMPLE', 'LOG_FORMAT_DETAILED', 'LOG_FORMAT_JSON', 'DEFAULT_MEMGRAPH_HOST', 'DEFAULT_MEMGRAPH_PORT', 'DEFAULT_MEMGRAPH_LAB_PORT', 'DEFAULT_REDIS_HOST', 'DEFAULT_REDIS_PORT', 'DEFAULT_REDIS_DB', 'MIN_STORY_POINTS', 'MAX_STORY_POINTS', 'MAX_CYCLOMATIC_COMPLEXITY', 'MAX_FUNCTION_LENGTH_LINES', 'MAX_FILE_LENGTH_LINES', 'MAX_METHOD_PARAMETERS', 'MIN_TEST_COVERAGE_PERCENT', 'MIN_TESTS_PER_FEATURE', 'get_developer_prompt_path', 'get_developer_output_dir', 'ensure_directory_exists', 'validate_config']