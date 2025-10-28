#!/usr/bin/env python3
"""
Persistence Store Factory

WHY: Centralizes persistence store creation, enabling easy addition of
     new storage backends without modifying client code.

RESPONSIBILITY: Creates appropriate persistence store based on type.
                Uses Strategy Pattern to support multiple backends.

PATTERNS:
- Factory Pattern: Encapsulates object creation logic
- Strategy Pattern: Dictionary mapping for store types (dispatch table)
- Single Responsibility: Focused solely on store instantiation
"""

import os
from typing import Dict, Any, Callable

from artemis_exceptions import ConfigurationError

from .interface import PersistenceStoreInterface
from .sqlite_store import SQLitePersistenceStore
from .json_store import JSONFilePersistenceStore


class PersistenceStoreFactory:
    """
    Factory for creating persistence stores.

    WHY: Centralizes persistence store creation, enabling easy addition of
         new storage backends without modifying client code.

    RESPONSIBILITY: Creates appropriate persistence store based on type.
                    Uses Strategy Pattern to support multiple backends.

    PATTERNS: Factory Pattern - encapsulates object creation logic.
              Strategy Pattern - dictionary mapping for store types.
    """

    # Strategy Pattern: Dictionary mapping for store creation (avoids if/elif chains)
    _STORE_CREATORS: Dict[str, Callable[[Dict[str, Any]], PersistenceStoreInterface]] = {
        'sqlite': lambda kwargs: SQLitePersistenceStore(
            db_path=kwargs.get("db_path", "../../.artemis_data/artemis_persistence.db")
        ),
        'json': lambda kwargs: JSONFilePersistenceStore(
            storage_dir=kwargs.get("storage_dir", "../../.artemis_data/persistence")
        ),
    }

    @staticmethod
    def create(store_type: str = "sqlite", **kwargs) -> PersistenceStoreInterface:
        """
        Create persistence store.

        WHY: Factory pattern centralizes store creation logic.
        PERFORMANCE: O(1) dictionary lookup instead of if/elif chain.

        Args:
            store_type: "sqlite", "postgres", or "json"
            **kwargs: Store-specific arguments

        Returns:
            PersistenceStoreInterface implementation

        Raises:
            ConfigurationError: If store type is unknown or not implemented
        """
        # PostgreSQL not yet implemented - early check
        if store_type == "postgres":
            raise ConfigurationError(
                "PostgreSQL persistence store not yet implemented",
                context={'store_type': store_type, 'available': list(PersistenceStoreFactory._STORE_CREATORS.keys())}
            )

        # Strategy Pattern: Look up creator in dictionary
        creator = PersistenceStoreFactory._STORE_CREATORS.get(store_type)

        # Early return guard clause - unknown store type
        if not creator:
            raise ConfigurationError(
                f"Unknown store type: {store_type}",
                context={'store_type': store_type, 'available': list(PersistenceStoreFactory._STORE_CREATORS.keys())}
            )

        # Creator found - invoke it
        return creator(kwargs)

    @staticmethod
    def create_from_env() -> PersistenceStoreInterface:
        """
        Create persistence store from environment variables.

        WHY: Enables configuration through environment variables for
             different deployment environments (dev, staging, prod).
        PERFORMANCE: O(1) environment variable lookup and store creation.

        Returns:
            PersistenceStoreInterface implementation based on env config

        Environment Variables:
            ARTEMIS_PERSISTENCE_TYPE: Store type ("sqlite" or "json", default: "sqlite")
            ARTEMIS_PERSISTENCE_DB: SQLite database path
            ARTEMIS_PERSISTENCE_DIR: JSON storage directory
        """
        store_type = os.getenv("ARTEMIS_PERSISTENCE_TYPE", "sqlite")

        # Strategy Pattern: Dictionary mapping for environment-based configuration
        env_config_map: Dict[str, Dict[str, str]] = {
            'sqlite': {
                'db_path': os.getenv("ARTEMIS_PERSISTENCE_DB", "../../.artemis_data/artemis_persistence.db")
            },
            'json': {
                'storage_dir': os.getenv("ARTEMIS_PERSISTENCE_DIR", "../../.artemis_data/persistence")
            }
        }

        # Get configuration for store type
        config = env_config_map.get(store_type)

        # Early return guard clause - unknown store type, default to SQLite
        if not config:
            return SQLitePersistenceStore()

        # Known store type - create with environment config
        return PersistenceStoreFactory.create(store_type, **config)
