#!/usr/bin/env python3
"""
Base Research Strategy

WHY: Defines the abstract interface for all research strategies, ensuring consistency
and enabling the Strategy Pattern for different research sources.

RESPONSIBILITY: Provides abstract base class and common functionality:
- Abstract search interface that all strategies must implement
- Common HTTP fetching with timeout and error handling
- Query building utilities
- Exception handling with proper error context

PATTERNS:
- Strategy Pattern: Abstract base class for interchangeable research algorithms
- Template Method Pattern: Common implementation with extension points
- Guard Clause Pattern: Early returns for error conditions (max 1 level nesting)
"""

import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from research_exceptions import ResearchSourceError, ResearchTimeoutError
from research.models import ResearchExample


class ResearchStrategy(ABC):
    """
    Abstract base class for research strategies (Strategy Pattern).

    Each concrete strategy implements a different research source (GitHub, HuggingFace, etc.)
    This base class provides common functionality like HTTP fetching and query building.
    """

    def __init__(self, timeout_seconds: int = 30):
        """
        Initialize research strategy.

        Args:
            timeout_seconds: Timeout for HTTP requests in seconds
        """
        self.timeout_seconds = timeout_seconds

    @abstractmethod
    def search(self, query: str, technologies: List[str], max_results: int = 5) -> List[ResearchExample]:
        """
        Search for code examples.

        Args:
            query: Search query describing what to find
            technologies: List of technologies/frameworks to search for
            max_results: Maximum number of results to return

        Returns:
            List of ResearchExample objects sorted by relevance

        Raises:
            ResearchSourceError: If search fails
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get the name of this research source.

        Returns:
            Human-readable name (e.g., "GitHub", "HuggingFace", "Local")
        """
        pass

    def _build_queries(self, query: str, technologies: List[str]) -> List[str]:
        """
        Build search queries from base query and technologies.

        Uses comprehension instead of nested loop for O(n) complexity.

        Args:
            query: Base query string
            technologies: List of technology names

        Returns:
            List of search query strings combining query with each technology
        """
        # Guard clause: return single query if no technologies
        if not technologies:
            return [query]

        # Use list comprehension to build queries (no nested loops)
        return [f"{query} {tech}" for tech in technologies]

    def _fetch_url(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Fetch URL with timeout and error handling.

        Provides consistent error handling and wrapping for all HTTP requests.

        Args:
            url: URL to fetch
            headers: Optional HTTP headers dictionary

        Returns:
            Parsed JSON response as dictionary

        Raises:
            ResearchSourceError: If fetch fails or JSON is invalid
            ResearchTimeoutError: If request times out
        """
        # Guard clause: validate URL
        if not url:
            raise ResearchSourceError(
                self.get_source_name(),
                "URL cannot be empty"
            )

        try:
            request = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode('utf-8'))

        except urllib.error.URLError as e:
            raise ResearchSourceError(
                self.get_source_name(),
                f"Failed to fetch {url}",
                cause=e
            )
        except json.JSONDecodeError as e:
            raise ResearchSourceError(
                self.get_source_name(),
                f"Invalid JSON response from {url}",
                cause=e
            )
        except TimeoutError as e:
            raise ResearchTimeoutError(
                f"fetch {url}",
                self.timeout_seconds,
                cause=e
            )
