#!/usr/bin/env python3
"""
Test script for Hydra logging and storage configuration.

WHY: Validates Hydra configuration for logging and storage components.
RESPONSIBILITY: Test and validate Hydra configuration system functionality.
PATTERNS: Strategy pattern for storage provider checking, early returns for validation.

This module tests:
- Logging configuration (directories, levels, rotation)
- Output storage configuration (local/remote)
- Remote storage provider configuration (S3, GCS, Azure)
- Logger and storage manager instantiation

Usage:
  python test_hydra_logging_storage.py card_id=test-001
  python test_hydra_logging_storage.py card_id=test-002 logging=dev
  python test_hydra_logging_storage.py card_id=test-003 output=s3
  python test_hydra_logging_storage.py card_id=test-004 logging=prod logging.log_level=DEBUG
"""

from typing import Dict, Any, Callable
from omegaconf import DictConfig, OmegaConf
import hydra
import os


# Constants - DRY principle for repeated values
CHECK_MARK = "✓ set"
CROSS_MARK = "✗ not set"
SEPARATOR_LONG = "=" * 70
SEPARATOR_SHORT = "-" * 70

# Strategy pattern: Remote storage provider handlers
# WHY: Avoid if/elif chain, easily extensible for new providers
REMOTE_PROVIDER_HANDLERS = {
    's3': '_print_s3_config',
    'gcs': '_print_gcs_config',
    'azure': '_print_azure_config'
}


def _get_env_status(var_name: str) -> str:
    """
    Get environment variable status indicator.

    WHY: DRY - avoid repeating env var check logic.

    Args:
        var_name: Environment variable name

    Returns:
        Status string with checkmark or cross mark
    """
    return CHECK_MARK if os.getenv(var_name) else CROSS_MARK


def _print_s3_config(cfg: DictConfig) -> None:
    """
    Print S3 storage configuration.

    WHY: Strategy pattern handler for S3 provider.
    """
    print(f"  Bucket: {cfg.output.remote.s3.bucket}")
    print(f"  Region: {cfg.output.remote.s3.region}")
    print(f"\n  Environment Variables:")
    print(f"    AWS_ACCESS_KEY_ID: {_get_env_status('AWS_ACCESS_KEY_ID')}")
    print(f"    AWS_SECRET_ACCESS_KEY: {_get_env_status('AWS_SECRET_ACCESS_KEY')}")


def _print_gcs_config(cfg: DictConfig) -> None:
    """
    Print GCS storage configuration.

    WHY: Strategy pattern handler for GCS provider.
    """
    print(f"  Bucket: {cfg.output.remote.gcs.bucket}")
    print(f"  Project: {cfg.output.remote.gcs.project}")
    print(f"\n  Environment Variables:")
    print(f"    GOOGLE_APPLICATION_CREDENTIALS: {_get_env_status('GOOGLE_APPLICATION_CREDENTIALS')}")


def _print_azure_config(cfg: DictConfig) -> None:
    """
    Print Azure storage configuration.

    WHY: Strategy pattern handler for Azure provider.
    """
    print(f"  Container: {cfg.output.remote.azure.container}")
    print(f"  Storage Account: {cfg.output.remote.azure.storage_account}")
    print(f"\n  Environment Variables:")
    print(f"    AZURE_STORAGE_CONNECTION_STRING: {_get_env_status('AZURE_STORAGE_CONNECTION_STRING')}")


def _print_logging_config(cfg: DictConfig) -> None:
    """
    Print logging configuration details.

    WHY: Extract complex logic to helper function for clarity.
    """
    print("\n📝 Logging Configuration:")
    print(f"  Log Directory: {cfg.logging.log_dir}")
    print(f"  Log Level: {cfg.logging.log_level}")
    print(f"  Max Size: {cfg.logging.max_size_mb} MB")
    print(f"  Backup Count: {cfg.logging.backup_count}")
    print(f"  Verbose: {cfg.logging.verbose}")

    # Check log directory status with early returns
    log_dir = cfg.logging.log_dir
    log_dir_exists = os.path.exists(log_dir)
    log_dir_writable = os.access(log_dir, os.W_OK) if log_dir_exists else False

    print(f"\n  Directory Status:")
    print(f"    Exists: {log_dir_exists}")
    print(f"    Writable: {log_dir_writable}")


def _print_local_storage_config(cfg: DictConfig) -> None:
    """
    Print local storage configuration.

    WHY: Extract local storage handling to avoid nested ifs.
    """
    from pathlib import Path

    # Early return if not local storage
    if cfg.output.storage_type != "local":
        return

    # Resolve local path
    agile_dir = Path(__file__).parent

    # Use early return pattern instead of nested if
    if Path(cfg.output.local_path).is_absolute():
        local_path = Path(cfg.output.local_path)
    else:
        local_path = (agile_dir / cfg.output.local_path).resolve()

    print(f"  Resolved Path: {local_path}")
    print(f"\n  Directory Status:")
    print(f"    Exists: {local_path.exists()}")

    # Only check writability if path exists
    if local_path.exists():
        print(f"    Writable: {os.access(local_path, os.W_OK)}")


def _print_remote_storage_config(cfg: DictConfig) -> None:
    """
    Print remote storage configuration using strategy pattern.

    WHY: Strategy pattern avoids if/elif chain for providers.
    PATTERNS: Strategy pattern with dictionary mapping.
    """
    # Early return if not remote storage
    if cfg.output.storage_type != "remote":
        return

    provider = cfg.output.remote.provider
    print(f"\n☁️  Remote Storage ({provider.upper()}):")

    # Strategy pattern: Get handler for provider
    handler_name = REMOTE_PROVIDER_HANDLERS.get(provider)

    # Early return if unknown provider
    if not handler_name:
        print(f"  ⚠️  Unknown provider: {provider}")
        return

    # Execute handler using globals() to call function by name
    # WHY: Cleaner than if/elif chain, easily extensible
    handler = globals()[handler_name]
    handler(cfg)


def _print_other_config(cfg: DictConfig) -> None:
    """
    Print other configuration sections.

    WHY: Extract to helper for clarity, uses hasattr guard pattern.
    """
    print("\n🔧 Other Configuration:")

    if hasattr(cfg, 'llm'):
        llm_info = cfg.llm.provider if hasattr(cfg.llm, 'provider') else 'configured'
        print(f"  LLM Provider: {llm_info}")

    if hasattr(cfg, 'storage'):
        storage_info = cfg.storage.rag_db_type if hasattr(cfg.storage, 'rag_db_type') else 'configured'
        print(f"  Storage Backend: {storage_info}")

    if hasattr(cfg, 'pipeline'):
        print(f"  Pipeline Strategy: configured")

    if hasattr(cfg, 'security'):
        print(f"  Security Level: configured")


def _test_logger_creation(cfg: DictConfig) -> None:
    """
    Test logger creation with configuration.

    WHY: Extract logger testing to separate function for clarity.
    """
    print("\n🧪 Testing Logger Creation:")

    try:
        from artemis_logger import ArtemisLogger
        logger = ArtemisLogger(
            component="test",
            log_dir=cfg.logging.log_dir,
            log_level=cfg.logging.log_level,
            max_bytes=cfg.logging.max_size_mb * 1024 * 1024,
            backup_count=cfg.logging.backup_count
        )
        logger.info("Test log message from Hydra config test")
        print(f"  ✅ Logger created successfully")
        print(f"  Log file: {logger.get_log_path()}")
    except Exception as e:
        print(f"  ❌ Logger creation failed: {e}")


def _test_storage_manager_creation(cfg: DictConfig) -> None:
    """
    Test storage manager creation with configuration.

    WHY: Extract storage manager testing to separate function for clarity.
    """
    print("\n🧪 Testing Storage Manager Creation:")

    try:
        # Set environment variables from config for testing
        os.environ["ARTEMIS_OUTPUT_STORAGE"] = cfg.output.storage_type
        os.environ["ARTEMIS_OUTPUT_PATH"] = cfg.output.local_path

        # Only set remote provider if using remote storage
        if cfg.output.storage_type == "remote":
            os.environ["ARTEMIS_REMOTE_STORAGE_PROVIDER"] = cfg.output.remote.provider

        from output_storage import OutputStorageManager
        storage = OutputStorageManager()
        info = storage.get_storage_info()

        print(f"  ✅ Storage manager created successfully")
        print(f"  Type: {info['type']}")
        print(f"  Backend: {info['backend']}")

        # Use early return pattern instead of nested if
        if info['type'] == 'local':
            print(f"  Base Path: {info['base_path']}")
        elif info['type'] == 'remote':
            print(f"  Provider: {info['provider']}")
    except Exception as e:
        print(f"  ❌ Storage manager creation failed: {e}")


@hydra.main(config_path="conf", config_name="config", version_base=None)
def test_config(cfg: DictConfig) -> None:
    """
    Test Hydra configuration for logging and storage.

    WHY: Validates that Hydra configuration loads correctly and can be used
    to instantiate logging and storage components.
    PATTERNS: Delegates to helper functions for clean, testable code.

    Args:
        cfg: Hydra configuration object
    """
    # Print header
    print(SEPARATOR_LONG)
    print("Hydra Configuration Test - Logging & Storage")
    print(SEPARATOR_LONG)

    # Card ID
    print(f"\n📋 Card ID: {cfg.card_id}")

    # Logging configuration
    _print_logging_config(cfg)

    # Output storage configuration
    print("\n💾 Output Storage Configuration:")
    print(f"  Storage Type: {cfg.output.storage_type}")
    print(f"  Local Path: {cfg.output.local_path}")

    # Local storage details (early return pattern used inside)
    _print_local_storage_config(cfg)

    print(f"\n  Remote Provider: {cfg.output.remote.provider}")

    # Remote storage details (strategy pattern used inside)
    _print_remote_storage_config(cfg)

    # Other configurations
    _print_other_config(cfg)

    # Test logger creation
    _test_logger_creation(cfg)

    # Test storage manager creation
    _test_storage_manager_creation(cfg)

    # Summary
    print(f"\n{SEPARATOR_LONG}")
    print("✅ Configuration Test Complete!")
    print(SEPARATOR_LONG)

    # Show full config in YAML format
    print("\n📄 Full Configuration (YAML):")
    print(SEPARATOR_SHORT)
    print(OmegaConf.to_yaml(cfg))


if __name__ == "__main__":
    test_config()
