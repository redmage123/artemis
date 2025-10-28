#!/usr/bin/env python3
"""
WHY: Parse Spring Boot configuration files (properties, YAML)
RESPONSIBILITY: Load and parse application.properties and application.yml files
PATTERNS: Strategy Pattern (properties vs YAML), Guard Clauses, Single Responsibility

This module handles Spring Boot configuration parsing:
- application.properties parsing
- application.yml parsing with YAML flattening
- Active profile detection
- Actuator endpoint configuration
- Database configuration extraction
"""

from pathlib import Path
from typing import Dict, List, Optional
import yaml
import re
import logging

from .models import DatabaseConfig


class ConfigParser:
    """
    Parser for Spring Boot configuration files.

    Handles both .properties and .yml/.yaml formats.
    """

    def __init__(self, resources_dir: Path, logger: Optional[logging.Logger] = None):
        """
        Initialize configuration parser.

        Args:
            resources_dir: Path to src/main/resources directory
            logger: Optional logger for diagnostic messages
        """
        self.resources_dir = resources_dir
        self.logger = logger or logging.getLogger(__name__)

    def load_properties(self) -> Dict[str, str]:
        """
        Load all application properties from .properties and .yml files.

        Returns:
            Dictionary of flattened properties
        """
        properties = {}

        # Load from application.properties
        properties.update(self._load_properties_file())

        # Load from application.yml (overwrites .properties if conflicts)
        properties.update(self._load_yaml_file())

        return properties

    def get_active_profiles(self) -> List[str]:
        """
        Get active Spring profiles from configuration.

        Returns:
            List of active profile names
        """
        profiles_prop = "spring.profiles.active"

        for config_file in [
            self.resources_dir / "application.properties",
            self.resources_dir / "application.yml"
        ]:
            if not config_file.exists():
                continue

            content = config_file.read_text()
            match = re.search(rf'{profiles_prop}[:\s=]+([^\n]+)', content)
            if match:
                return [p.strip() for p in match.group(1).split(",")]

        return []

    def _load_properties_file(self) -> Dict[str, str]:
        """
        Load application.properties file.

        Returns:
            Dictionary of key-value properties
        """
        props_file = self.resources_dir / "application.properties"
        if not props_file.exists():
            return {}

        properties = {}
        content = props_file.read_text()

        for line in content.splitlines():
            line = line.strip()

            # Guard clauses for invalid lines
            if not line:
                continue
            if line.startswith("#"):
                continue
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            properties[key.strip()] = value.strip()

        return properties

    def _load_yaml_file(self) -> Dict[str, str]:
        """
        Load application.yml file and flatten to dot notation.

        Returns:
            Dictionary of flattened properties
        """
        yml_file = self.resources_dir / "application.yml"
        if not yml_file.exists():
            return {}

        try:
            with open(yml_file, 'r') as f:
                yml_data = yaml.safe_load(f)

            if not yml_data:
                return {}

            return self._flatten_yaml(yml_data)

        except Exception as e:
            self.logger.warning(f"Failed to parse application.yml: {e}")
            return {}

    def _flatten_yaml(self, data: dict, prefix: str = "") -> Dict[str, str]:
        """
        Flatten nested YAML structure to dot notation.

        Args:
            data: Nested dictionary from YAML
            prefix: Current key prefix

        Returns:
            Flattened dictionary with dot notation keys
        """
        result = {}

        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                result.update(self._flatten_yaml(value, full_key))
            else:
                result[full_key] = str(value)

        return result


class DatabaseConfigExtractor:
    """
    Extractor for database configuration from properties.

    Parses Spring datasource properties into DatabaseConfig model.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize database config extractor.

        Args:
            logger: Optional logger for diagnostic messages
        """
        self.logger = logger or logging.getLogger(__name__)

    def extract_database_config(
        self,
        properties: Dict[str, str],
        database_type_detector: Optional[callable] = None
    ) -> DatabaseConfig:
        """
        Extract database configuration from properties.

        Args:
            properties: Application properties dictionary
            database_type_detector: Optional function to detect DB type from URL

        Returns:
            DatabaseConfig with extracted values
        """
        config = DatabaseConfig()

        config.url = properties.get("spring.datasource.url")
        config.driver_class = properties.get("spring.datasource.driver-class-name")
        config.username = properties.get("spring.datasource.username")

        # Detect database type if detector provided
        if database_type_detector and config.url:
            config.datasource_type = database_type_detector(config.url)

        return config


class ActuatorConfigExtractor:
    """
    Extractor for Spring Boot Actuator configuration.

    Parses actuator endpoint exposure settings.
    """

    # Default actuator endpoints when none specified
    DEFAULT_ENDPOINTS = ["health", "info"]

    # All available actuator endpoints
    ALL_ENDPOINTS = [
        "health",
        "info",
        "metrics",
        "env",
        "beans",
        "mappings",
        "loggers"
    ]

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize actuator config extractor.

        Args:
            logger: Optional logger for diagnostic messages
        """
        self.logger = logger or logging.getLogger(__name__)

    def get_exposed_endpoints(self, properties: Dict[str, str]) -> List[str]:
        """
        Get list of exposed actuator endpoints.

        Args:
            properties: Application properties dictionary

        Returns:
            List of exposed endpoint names
        """
        expose_prop = properties.get("management.endpoints.web.exposure.include", "")

        # All endpoints exposed
        if expose_prop == "*":
            return self.ALL_ENDPOINTS.copy()

        # Specific endpoints listed
        if expose_prop:
            return [e.strip() for e in expose_prop.split(",")]

        # Default endpoints
        return self.DEFAULT_ENDPOINTS.copy()


class SecurityConfigExtractor:
    """
    Extractor for Spring Security configuration from properties.

    Identifies security-related configuration in application properties.
    """

    def __init__(self, src_main: Path, logger: Optional[logging.Logger] = None):
        """
        Initialize security config extractor.

        Args:
            src_main: Path to src/main/java directory
            logger: Optional logger for diagnostic messages
        """
        self.src_main = src_main
        self.logger = logger or logging.getLogger(__name__)

    def detect_security_features(self) -> Dict[str, bool]:
        """
        Detect security features from security configuration files.

        Returns:
            Dictionary of detected security features
        """
        features = {
            'basic_auth': False,
            'form_login': False,
            'cors_enabled': False,
            'csrf_enabled': True,  # Default in Spring Security
        }

        if not self.src_main.exists():
            return features

        # Scan security configuration files
        for java_file in self.src_main.glob("**/*Security*.java"):
            content = java_file.read_text()

            if "httpBasic()" in content:
                features['basic_auth'] = True
            if "formLogin()" in content:
                features['form_login'] = True
            if ".cors()" in content:
                features['cors_enabled'] = True
            if "csrf().disable()" in content:
                features['csrf_enabled'] = False

        return features
