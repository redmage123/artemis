#!/usr/bin/env python3
"""
WHY: Specialized scanning of Java source files for Spring annotations
RESPONSIBILITY: Detect and extract Spring Framework annotations from Java code
PATTERNS: Strategy Pattern (different scanners), Guard Clauses, Single Responsibility

This module provides annotation scanning capabilities for Spring Boot projects:
- Find classes with specific annotations (@RestController, @Service, etc.)
- Extract REST endpoint mappings and HTTP methods
- Parse annotation parameters and metadata
"""

from pathlib import Path
from typing import List, Optional, Callable
import re
import logging

from .models import RestEndpoint


class AnnotationScanner:
    """
    Scanner for Spring Framework annotations in Java source code.

    Provides methods to find annotated classes and extract
    annotation metadata using regex patterns.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize annotation scanner.

        Args:
            logger: Optional logger for diagnostic messages
        """
        self.logger = logger or logging.getLogger(__name__)

    def find_main_application_class(self, src_main: Path) -> Optional[str]:
        """
        Find the main Spring Boot application class.

        Args:
            src_main: Path to src/main/java directory

        Returns:
            Fully qualified class name or None if not found
        """
        if not src_main.exists():
            return None

        for java_file in src_main.glob("**/*.java"):
            content = java_file.read_text()

            if "@SpringBootApplication" not in content:
                continue

            # Extract class name
            match = re.search(r'public\s+class\s+(\w+)', content)
            if not match:
                continue

            package = self._extract_package_from_file(java_file)
            return f"{package}.{match.group(1)}"

        return None

    def find_annotated_classes(self, src_main: Path, *annotations: str) -> List[str]:
        """
        Find classes with specific annotations.

        Args:
            src_main: Path to src/main/java directory
            annotations: Spring annotations to search for (e.g., '@Service')

        Returns:
            List of fully qualified class names
        """
        if not src_main.exists():
            return []

        classes = []
        for java_file in src_main.glob("**/*.java"):
            content = java_file.read_text()

            # Check if any annotation is present
            if not any(ann in content for ann in annotations):
                continue

            # Extract class name
            match = re.search(r'public\s+(?:class|interface)\s+(\w+)', content)
            if not match:
                continue

            package = self._extract_package_from_file(java_file)
            classes.append(f"{package}.{match.group(1)}")

        return classes

    def check_annotation_usage(self, src_main: Path, annotation: str) -> bool:
        """
        Check if annotation is used anywhere in source code.

        Args:
            src_main: Path to src/main/java directory
            annotation: Annotation to search for (e.g., '@Async')

        Returns:
            True if annotation is found
        """
        if not src_main.exists():
            return False

        for java_file in src_main.glob("**/*.java"):
            content = java_file.read_text()
            if annotation in content:
                return True

        return False

    def _extract_package_from_file(self, java_file: Path) -> str:
        """
        Extract package declaration from Java file.

        Args:
            java_file: Path to Java source file

        Returns:
            Package name or empty string
        """
        content = java_file.read_text()
        match = re.search(r'package\s+([\w.]+);', content)
        return match.group(1) if match else ""


class RestEndpointScanner:
    """
    Specialized scanner for REST API endpoints.

    Extracts REST controller mappings, HTTP methods,
    path variables, and request parameters.
    """

    # Dispatch table for REST mapping annotations
    MAPPING_PATTERNS = {
        'GET': r'@GetMapping\(["\']([^"\']+)["\']\)',
        'POST': r'@PostMapping\(["\']([^"\']+)["\']\)',
        'PUT': r'@PutMapping\(["\']([^"\']+)["\']\)',
        'DELETE': r'@DeleteMapping\(["\']([^"\']+)["\']\)',
        'PATCH': r'@PatchMapping\(["\']([^"\']+)["\']\)',
    }

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize REST endpoint scanner.

        Args:
            logger: Optional logger for diagnostic messages
        """
        self.logger = logger or logging.getLogger(__name__)

    def scan_rest_endpoints(self, src_main: Path) -> List[RestEndpoint]:
        """
        Scan for REST API endpoints in controllers.

        Args:
            src_main: Path to src/main/java directory

        Returns:
            List of discovered REST endpoints
        """
        if not src_main.exists():
            return []

        endpoints = []
        for java_file in src_main.glob("**/*.java"):
            content = java_file.read_text()

            if not self._is_rest_controller(content):
                continue

            controller_endpoints = self._extract_endpoints_from_controller(content)
            endpoints.extend(controller_endpoints)

        return endpoints

    def _is_rest_controller(self, content: str) -> bool:
        """
        Check if file contains a REST controller.

        Args:
            content: Java file content

        Returns:
            True if file is a REST controller
        """
        return "@RestController" in content or "@Controller" in content

    def _extract_endpoints_from_controller(self, content: str) -> List[RestEndpoint]:
        """
        Extract all endpoints from a controller class.

        Args:
            content: Controller Java file content

        Returns:
            List of REST endpoints
        """
        # Extract class name
        class_match = re.search(r'public\s+class\s+(\w+)', content)
        if not class_match:
            return []

        controller_class = class_match.group(1)

        # Extract base path from @RequestMapping on class
        class_path = self._extract_class_base_path(content)

        # Find all endpoint methods
        endpoints = []
        endpoints.extend(self._scan_mapping_annotations(content, controller_class, class_path))
        endpoints.extend(self._scan_request_mapping(content, controller_class, class_path))

        return endpoints

    def _extract_class_base_path(self, content: str) -> str:
        """
        Extract base path from class-level @RequestMapping.

        Args:
            content: Controller Java file content

        Returns:
            Base path or empty string
        """
        class_mapping = re.search(r'@RequestMapping\(["\']([^"\']+)["\']\)', content)
        return class_mapping.group(1) if class_mapping else ""

    def _scan_mapping_annotations(
        self,
        content: str,
        controller_class: str,
        class_path: str
    ) -> List[RestEndpoint]:
        """
        Scan for @GetMapping, @PostMapping, etc.

        Args:
            content: Controller Java file content
            controller_class: Name of controller class
            class_path: Base path from class-level mapping

        Returns:
            List of REST endpoints
        """
        endpoints = []

        for http_method, pattern in self.MAPPING_PATTERNS.items():
            for match in re.finditer(pattern, content):
                endpoint = self._create_endpoint(
                    match,
                    [http_method],
                    controller_class,
                    class_path,
                    content
                )
                if endpoint:
                    endpoints.append(endpoint)

        return endpoints

    def _scan_request_mapping(
        self,
        content: str,
        controller_class: str,
        class_path: str
    ) -> List[RestEndpoint]:
        """
        Scan for @RequestMapping with method specification.

        Args:
            content: Controller Java file content
            controller_class: Name of controller class
            class_path: Base path from class-level mapping

        Returns:
            List of REST endpoints
        """
        endpoints = []
        pattern = r'@RequestMapping\([^)]*value\s*=\s*["\']([^"\']+)["\'][^)]*method\s*=\s*RequestMethod\.(\w+)'

        for match in re.finditer(pattern, content):
            http_method = match.group(2)
            endpoint = self._create_endpoint(
                match,
                [http_method],
                controller_class,
                class_path,
                content
            )
            if endpoint:
                endpoints.append(endpoint)

        return endpoints

    def _create_endpoint(
        self,
        match: re.Match,
        methods: List[str],
        controller_class: str,
        class_path: str,
        content: str
    ) -> Optional[RestEndpoint]:
        """
        Create RestEndpoint from regex match.

        Args:
            match: Regex match object
            methods: HTTP methods for endpoint
            controller_class: Name of controller class
            class_path: Base path from class-level mapping
            content: Controller Java file content

        Returns:
            RestEndpoint or None if extraction fails
        """
        path = match.group(1)
        full_path = f"{class_path}{path}".replace("//", "/")

        # Extract method name
        method_start = match.end()
        method_def = content[method_start:method_start + 200]
        method_name_match = re.search(r'public\s+\w+\s+(\w+)\s*\(', method_def)
        method_name = method_name_match.group(1) if method_name_match else "unknown"

        # Extract path variables
        path_vars = re.findall(r'\{(\w+)\}', full_path)

        return RestEndpoint(
            path=full_path,
            methods=methods,
            controller_class=controller_class,
            method_name=method_name,
            path_variables=path_vars
        )
