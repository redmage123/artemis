#!/usr/bin/env python3
"""
Hydra Config Loader - Load profile-specific configs

WHY: Enable adaptive pipeline to load different config profiles
based on task complexity and platform capabilities.

RESPONSIBILITY: Load and compose Hydra configs dynamically.

PATTERNS: Factory Pattern, Singleton Pattern.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from omegaconf import OmegaConf, DictConfig
from artemis_logger import get_logger

logger = get_logger(__name__)


class HydraConfigLoader:
    """
    Load and compose Hydra configuration files.

    WHY: Enables dynamic profile loading without restarting application.
    """

    def __init__(self, config_dir: str = "conf"):
        """
        Initialize loader.

        Args:
            config_dir: Directory containing Hydra configs (relative to src/)
        """
        self.config_dir = Path(__file__).parent / config_dir

    def load_pipeline_profile(self, profile: str) -> DictConfig:
        """
        Load a pipeline profile configuration.

        Args:
            profile: Profile name (minimal, balanced, aggressive, conservative)

        Returns:
            DictConfig with pipeline configuration
        """
        profile_path = self.config_dir / "pipeline" / f"{profile}.yaml"

        if not profile_path.exists():
            logger.log(f"⚠️  Profile {profile} not found, using balanced", "WARNING")
            profile_path = self.config_dir / "pipeline" / "balanced.yaml"

        logger.log(f"📂 Loading pipeline profile: {profile}", "INFO")
        cfg = OmegaConf.load(profile_path)

        return cfg

    def compose_config(
        self,
        base_config: Optional[DictConfig] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> DictConfig:
        """
        Compose configuration with overrides.

        Args:
            base_config: Base configuration to override
            overrides: Dict of values to override

        Returns:
            Composed DictConfig
        """
        if base_config is None:
            base_config = OmegaConf.create({})

        if overrides:
            override_cfg = OmegaConf.create(overrides)
            cfg = OmegaConf.merge(base_config, override_cfg)
        else:
            cfg = base_config

        return cfg

    def get_profile_for_execution_profile(self, execution_profile: str) -> str:
        """
        Map execution profile to pipeline profile.

        Args:
            execution_profile: Execution profile (MINIMAL, BALANCED, AGGRESSIVE, CONSERVATIVE)

        Returns:
            Pipeline profile name
        """
        mapping = {
            "MINIMAL": "minimal",
            "BALANCED": "balanced",
            "AGGRESSIVE": "aggressive",
            "CONSERVATIVE": "conservative"
        }

        return mapping.get(execution_profile.upper(), "balanced")

    def load_profile_params(self, profile: str) -> Dict[str, Any]:
        """
        Load profile parameters as plain dict.

        Args:
            profile: Profile name

        Returns:
            Dict with profile parameters
        """
        cfg = self.load_pipeline_profile(profile)
        return OmegaConf.to_container(cfg, resolve=True)


# Singleton instance
_loader_instance = None


def get_config_loader() -> HydraConfigLoader:
    """Get singleton config loader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = HydraConfigLoader()
    return _loader_instance


def load_profile(profile: str) -> Dict[str, Any]:
    """
    Convenience function to load a profile.

    Usage:
        params = load_profile("balanced")
        max_retries = params["retry"]["max_retries"]
    """
    loader = get_config_loader()
    return loader.load_profile_params(profile)
