#!/usr/bin/env python3
"""
WHY: Provide AWS S3 storage backend for cloud-based storage
RESPONSIBILITY: Implement storage operations using AWS S3 API
PATTERNS: Strategy (storage backend), Adapter (boto3 SDK)

S3StorageBackend provides:
- AWS S3 integration via boto3
- Bucket and region configuration
- Optional prefix support
- S3 URI generation
"""

from typing import List
from output_storage.backends.base import StorageBackend


class S3StorageBackend(StorageBackend):
    """
    AWS S3 storage backend

    Stores all outputs in an S3 bucket.
    """

    def __init__(self, bucket: str, region: str = "us-east-1", prefix: str = ""):
        """
        Initialize S3 storage backend

        Args:
            bucket: S3 bucket name
            region: AWS region (default: us-east-1)
            prefix: Optional prefix for all keys

        Raises:
            RuntimeError: If boto3 is not installed
        """
        self.bucket = bucket
        self.region = region
        self.prefix = prefix

        try:
            import boto3
            self.s3 = boto3.client('s3', region_name=region)
        except ImportError:
            raise RuntimeError("boto3 required for S3 storage. Install with: pip install boto3")

    def write_file(self, relative_path: str, content: str) -> str:
        """
        Write file to S3

        Args:
            relative_path: Path relative to prefix
            content: File content

        Returns:
            S3 URI (s3://bucket/key)
        """
        key = f"{self.prefix}/{relative_path}".lstrip("/")
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content.encode('utf-8')
        )
        return f"s3://{self.bucket}/{key}"

    def read_file(self, relative_path: str) -> str:
        """
        Read file from S3

        Args:
            relative_path: Path relative to prefix

        Returns:
            File content
        """
        key = f"{self.prefix}/{relative_path}".lstrip("/")
        response = self.s3.get_object(Bucket=self.bucket, Key=key)
        return response['Body'].read().decode('utf-8')

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List all files with given prefix

        Args:
            prefix: Prefix to filter files

        Returns:
            List of relative file paths
        """
        full_prefix = f"{self.prefix}/{prefix}".lstrip("/")
        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=full_prefix)

        files = []
        for obj in response.get('Contents', []):
            key = obj['Key']

            # Strip base prefix if present
            if self.prefix:
                key = key[len(self.prefix):].lstrip("/")

            files.append(key)

        return sorted(files)

    def delete_file(self, relative_path: str) -> bool:
        """
        Delete file from S3

        Args:
            relative_path: Path relative to prefix

        Returns:
            True (S3 delete always succeeds)
        """
        key = f"{self.prefix}/{relative_path}".lstrip("/")
        self.s3.delete_object(Bucket=self.bucket, Key=key)
        return True

    def get_full_path(self, relative_path: str) -> str:
        """
        Get S3 URI

        Args:
            relative_path: Path relative to prefix

        Returns:
            S3 URI (s3://bucket/key)
        """
        key = f"{self.prefix}/{relative_path}".lstrip("/")
        return f"s3://{self.bucket}/{key}"
