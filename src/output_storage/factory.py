#!/usr/bin/env python3
"""
WHY: Create storage backends based on configuration using Factory pattern
RESPONSIBILITY: Instantiate appropriate storage backend from environment variables
PATTERNS: Factory (backend creation), Strategy (backend selection), Dispatch Table

Backend factory provides:
- Local storage creation (default)
- S3 storage creation (requires boto3)
- GCS storage creation (requires google-cloud-storage)
- Configuration from environment variables
"""

import os
from typing import Callable, Dict
from output_storage.backends.base import StorageBackend
from output_storage.backends.local import LocalStorageBackend
from output_storage.backends.s3 import S3StorageBackend
from output_storage.backends.gcs import GCSStorageBackend


class StorageBackendFactory:
    """
    Factory for creating storage backends

    Uses dispatch table for O(1) backend selection.
    """

    def create_backend(self) -> StorageBackend:
        """
        Create storage backend based on environment configuration

        Returns:
            Configured StorageBackend instance

        Raises:
            ValueError: If storage type or provider is invalid
        """
        storage_type = os.getenv("ARTEMIS_OUTPUT_STORAGE", "local")

        # Guard clause - handle local storage (most common case)
        if storage_type == "local":
            return self._create_local_backend()

        # Guard clause - handle remote storage
        if storage_type == "remote":
            return self._create_remote_backend()

        # Invalid storage type
        raise ValueError(f"Invalid storage type: {storage_type}")

    def _create_local_backend(self) -> LocalStorageBackend:
        """
        Create local storage backend

        Returns:
            Configured LocalStorageBackend instance
        """
        # Default to repo root/output
        default_path = "../../output"
        base_path = os.getenv("ARTEMIS_OUTPUT_PATH", default_path)

        # Convert relative path to absolute
        if not os.path.isabs(base_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.join(script_dir, base_path)

        return LocalStorageBackend(base_path)

    def _create_remote_backend(self) -> StorageBackend:
        """
        Create remote storage backend using dispatch table

        Returns:
            Configured remote StorageBackend instance

        Raises:
            ValueError: If provider is unsupported
        """
        provider = os.getenv("ARTEMIS_REMOTE_STORAGE_PROVIDER", "s3")

        # Dispatch table: provider -> factory method
        backend_creators: Dict[str, Callable[[], StorageBackend]] = {
            "s3": self._create_s3_backend,
            "gcs": self._create_gcs_backend,
        }

        # Guard clause - check if provider is supported
        creator = backend_creators.get(provider)
        if not creator:
            raise ValueError(f"Unsupported remote storage provider: {provider}")

        # Create backend using dispatch table - O(1) lookup
        return creator()

    def _create_s3_backend(self) -> S3StorageBackend:
        """
        Create S3 storage backend

        Returns:
            Configured S3StorageBackend instance
        """
        return S3StorageBackend(
            bucket=os.getenv("ARTEMIS_S3_BUCKET"),
            region=os.getenv("ARTEMIS_S3_REGION", "us-east-1")
        )

    def _create_gcs_backend(self) -> GCSStorageBackend:
        """
        Create GCS storage backend

        Returns:
            Configured GCSStorageBackend instance
        """
        return GCSStorageBackend(
            bucket=os.getenv("ARTEMIS_GCS_BUCKET"),
            project=os.getenv("ARTEMIS_GCS_PROJECT")
        )
