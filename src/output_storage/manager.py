#!/usr/bin/env python3
"""
WHY: Manage all Artemis pipeline outputs with unified API regardless of backend
RESPONSIBILITY: Provide high-level API for ADR, developer, test, and report storage
PATTERNS: Facade (simplified API), Strategy (backend selection), Template Method

OutputStorageManager provides:
- write_adr() - Write ADR files
- write_developer_output() - Write developer implementation files
- write_test_results() - Write test results
- write_pipeline_report() - Write pipeline reports
- read_file() - Read any file
- list_card_outputs() - List all outputs for a card
- get_storage_info() - Get backend configuration details
"""

from typing import Dict, List
from datetime import datetime
from output_storage.backends.base import StorageBackend
from output_storage.factory import StorageBackendFactory


class OutputStorageManager:
    """
    Manages all Artemis pipeline outputs

    Configuration via environment variables:
    - ARTEMIS_OUTPUT_STORAGE: "local" or "remote" (default: local)
    - ARTEMIS_OUTPUT_PATH: Local storage base path (default: repo_root/output)
    - ARTEMIS_REMOTE_STORAGE_PROVIDER: "s3", "gcs", or "azure"
    - Provider-specific configs (see .env.example)
    """

    def __init__(self):
        """
        Initialize output storage manager

        Creates appropriate backend based on configuration.
        """
        factory = StorageBackendFactory()
        self.backend = factory.create_backend()

    def write_adr(self, card_id: str, adr_number: str, content: str) -> str:
        """
        Write ADR file

        Args:
            card_id: Kanban card ID
            adr_number: ADR number (e.g., "001")
            content: ADR content (Markdown)

        Returns:
            Full path or URI of written file
        """
        path = f"adrs/{card_id}/ADR-{adr_number}.md"
        return self.backend.write_file(path, content)

    def write_developer_output(
        self,
        card_id: str,
        developer: str,
        filename: str,
        content: str
    ) -> str:
        """
        Write developer output file

        Args:
            card_id: Kanban card ID
            developer: Developer name (developer-a, developer-b)
            filename: Output filename
            content: File content

        Returns:
            Full path or URI of written file
        """
        path = f"developers/{card_id}/{developer}/{filename}"
        return self.backend.write_file(path, content)

    def write_test_results(
        self,
        card_id: str,
        test_type: str,
        content: str
    ) -> str:
        """
        Write test results

        Args:
            card_id: Kanban card ID
            test_type: Type of test (unit, integration, e2e)
            content: Test results (JSON)

        Returns:
            Full path or URI of written file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"tests/{card_id}/{test_type}_{timestamp}.json"
        return self.backend.write_file(path, content)

    def write_pipeline_report(self, card_id: str, content: str) -> str:
        """
        Write pipeline execution report

        Args:
            card_id: Kanban card ID
            content: Pipeline report (JSON)

        Returns:
            Full path or URI of written file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"reports/{card_id}/pipeline_{timestamp}.json"
        return self.backend.write_file(path, content)

    def read_file(self, relative_path: str) -> str:
        """
        Read any file

        Args:
            relative_path: Path relative to storage root

        Returns:
            File content
        """
        return self.backend.read_file(relative_path)

    def list_card_outputs(self, card_id: str) -> Dict[str, List[str]]:
        """
        List all outputs for a card

        Args:
            card_id: Kanban card ID

        Returns:
            Dictionary with categorized file lists
        """
        return {
            "adrs": self.backend.list_files(f"adrs/{card_id}"),
            "developers": self.backend.list_files(f"developers/{card_id}"),
            "tests": self.backend.list_files(f"tests/{card_id}"),
            "reports": self.backend.list_files(f"reports/{card_id}")
        }

    def get_storage_info(self) -> Dict:
        """
        Get information about storage configuration

        Returns:
            Dictionary with backend type and configuration details
        """
        backend_type = self.backend.__class__.__name__

        # Dispatch table: backend type -> info getter
        info_getters = {
            "LocalStorageBackend": self._get_local_info,
            "S3StorageBackend": self._get_s3_info,
            "GCSStorageBackend": self._get_gcs_info,
        }

        # Guard clause - check if info getter exists
        getter = info_getters.get(backend_type)
        if getter:
            return getter(backend_type)

        # Default case for unknown backends
        return {"type": "unknown", "backend": backend_type}

    def _get_local_info(self, backend_type: str) -> Dict:
        """Get local storage backend info"""
        return {
            "type": "local",
            "backend": backend_type,
            "base_path": str(self.backend.base_path)
        }

    def _get_s3_info(self, backend_type: str) -> Dict:
        """Get S3 storage backend info"""
        return {
            "type": "remote",
            "backend": backend_type,
            "provider": "s3",
            "bucket": self.backend.bucket,
            "region": self.backend.region
        }

    def _get_gcs_info(self, backend_type: str) -> Dict:
        """Get GCS storage backend info"""
        return {
            "type": "remote",
            "backend": backend_type,
            "provider": "gcs",
            "bucket": self.backend.bucket_name,
            "project": self.backend.project
        }
