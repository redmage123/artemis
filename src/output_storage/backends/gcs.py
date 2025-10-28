#!/usr/bin/env python3
"""
WHY: Provide Google Cloud Storage backend for cloud-based storage
RESPONSIBILITY: Implement storage operations using GCS API
PATTERNS: Strategy (storage backend), Adapter (google-cloud-storage SDK)

GCSStorageBackend provides:
- Google Cloud Storage integration
- Bucket and project configuration
- Optional prefix support
- GCS URI generation
"""

from typing import List
from output_storage.backends.base import StorageBackend


class GCSStorageBackend(StorageBackend):
    """
    Google Cloud Storage backend

    Stores all outputs in a GCS bucket.
    """

    def __init__(self, bucket: str, project: str, prefix: str = ""):
        """
        Initialize GCS storage backend

        Args:
            bucket: GCS bucket name
            project: GCP project ID
            prefix: Optional prefix for all blob names

        Raises:
            RuntimeError: If google-cloud-storage is not installed
        """
        self.bucket_name = bucket
        self.project = project
        self.prefix = prefix

        try:
            from google.cloud import storage
            self.storage_client = storage.Client(project=project)
            self.bucket = self.storage_client.bucket(bucket)
        except ImportError:
            raise RuntimeError("google-cloud-storage required for GCS. Install with: pip install google-cloud-storage")

    def write_file(self, relative_path: str, content: str) -> str:
        """
        Write file to GCS

        Args:
            relative_path: Path relative to prefix
            content: File content

        Returns:
            GCS URI (gs://bucket/blob)
        """
        blob_name = f"{self.prefix}/{relative_path}".lstrip("/")
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(content)
        return f"gs://{self.bucket_name}/{blob_name}"

    def read_file(self, relative_path: str) -> str:
        """
        Read file from GCS

        Args:
            relative_path: Path relative to prefix

        Returns:
            File content
        """
        blob_name = f"{self.prefix}/{relative_path}".lstrip("/")
        blob = self.bucket.blob(blob_name)
        return blob.download_as_text()

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List all files with given prefix

        Args:
            prefix: Prefix to filter files

        Returns:
            List of relative file paths
        """
        full_prefix = f"{self.prefix}/{prefix}".lstrip("/")
        blobs = self.storage_client.list_blobs(self.bucket_name, prefix=full_prefix)

        files = []
        for blob in blobs:
            name = blob.name

            # Strip base prefix if present
            if self.prefix:
                name = name[len(self.prefix):].lstrip("/")

            files.append(name)

        return sorted(files)

    def delete_file(self, relative_path: str) -> bool:
        """
        Delete file from GCS

        Args:
            relative_path: Path relative to prefix

        Returns:
            True (GCS delete always succeeds)
        """
        blob_name = f"{self.prefix}/{relative_path}".lstrip("/")
        blob = self.bucket.blob(blob_name)
        blob.delete()
        return True

    def get_full_path(self, relative_path: str) -> str:
        """
        Get GCS URI

        Args:
            relative_path: Path relative to prefix

        Returns:
            GCS URI (gs://bucket/blob)
        """
        blob_name = f"{self.prefix}/{relative_path}".lstrip("/")
        return f"gs://{self.bucket_name}/{blob_name}"
