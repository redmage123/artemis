#!/usr/bin/env python3
"""
GitHub Research Strategy

WHY: Implements research strategy for the GitHub API, enabling discovery of code
examples from public repositories. Leverages GitHub's code search API for finding
relevant examples based on technologies and queries.

RESPONSIBILITY: Handles all GitHub-specific research operations:
- Search GitHub code repositories via REST API
- Fetch raw file contents from repositories
- Convert GitHub API responses to ResearchExample objects
- Score and rank results by relevance

PATTERNS:
- Strategy Pattern: Concrete implementation of ResearchStrategy
- Guard Clause Pattern: Early returns for validation (max 1 level nesting)
- List Comprehension: Flatten nested results without explicit loops
"""

import urllib.parse
import urllib.request
from typing import List

from research_exceptions import ResearchSourceError
from research.base_strategy import ResearchStrategy
from research.models import ResearchExample


class GitHubResearchStrategy(ResearchStrategy):
    """
    Research strategy for GitHub API.

    Searches GitHub repositories for code examples using the GitHub Code Search API.
    Fetches raw file content and ranks results by GitHub's relevance score.
    """

    def get_source_name(self) -> str:
        """
        Get the name of this research source.

        Returns:
            Human-readable name "GitHub"
        """
        return "GitHub"

    def search(self, query: str, technologies: List[str], max_results: int = 5) -> List[ResearchExample]:
        """
        Search GitHub for code examples.

        Builds multiple queries by combining base query with each technology,
        searches GitHub for each, and returns the top results by relevance.

        Args:
            query: Base search query
            technologies: List of technologies to search for
            max_results: Maximum results to return

        Returns:
            List of ResearchExample objects sorted by relevance score
        """
        # Guard clause: validate inputs
        if not query:
            return []

        # Build queries using base class method (no nested loops)
        queries = self._build_queries(query, technologies)

        # Calculate results per query
        results_per_query = max(1, max_results // len(queries) + 1)

        # Search each query and collect results (list comprehension - no nested loops)
        all_results = [
            self._search_github_code(q, results_per_query)
            for q in queries
        ]

        # Flatten results (list comprehension - no nested loops)
        examples = [example for results in all_results for example in results]

        # Sort by relevance and limit
        examples.sort(key=lambda x: x.relevance_score, reverse=True)
        return examples[:max_results]

    def _search_github_code(self, query: str, limit: int) -> List[ResearchExample]:
        """
        Search GitHub code API.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of ResearchExample objects from GitHub

        Raises:
            ResearchSourceError: If GitHub API request fails
        """
        try:
            # Build GitHub API URL
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.github.com/search/code?q={encoded_query}&per_page={limit}"

            # Set required headers for GitHub API
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Artemis-Research-Agent"
            }

            # Fetch data using base class method
            data = self._fetch_url(url, headers)

            # Convert to ResearchExample objects (list comprehension)
            return [
                self._create_example_from_item(item)
                for item in data.get('items', [])
            ]

        except ResearchSourceError:
            # Re-raise ResearchSourceError as-is
            raise
        except Exception as e:
            raise ResearchSourceError(
                self.get_source_name(),
                f"GitHub search failed for query: {query}",
                cause=e
            )

    def _create_example_from_item(self, item: dict) -> ResearchExample:
        """
        Create ResearchExample from GitHub API item.

        Args:
            item: GitHub API response item dictionary

        Returns:
            ResearchExample object with GitHub data
        """
        # Extract repository name for tags
        repo_name = item.get('repository', {}).get('name', '')

        # Fetch file content
        file_url = item.get('url', '')
        content = self._fetch_file_content(file_url)

        return ResearchExample(
            title=item.get('name', 'Unknown'),
            content=content,
            source="GitHub",
            url=item.get('html_url'),
            language=item.get('language', 'Unknown'),
            tags=[repo_name] if repo_name else [],
            relevance_score=item.get('score', 0.0)
        )

    def _fetch_file_content(self, url: str) -> str:
        """
        Fetch file content from GitHub API.

        Args:
            url: GitHub API URL for the file

        Returns:
            File content as string (limited to 5000 chars), or empty string on error
        """
        # Guard clause: return empty for invalid URL
        if not url:
            return ""

        try:
            # Request raw content
            headers = {
                "Accept": "application/vnd.github.v3.raw",
                "User-Agent": "Artemis-Research-Agent"
            }

            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                # Limit content size to prevent memory issues
                return response.read().decode('utf-8', errors='ignore')[:5000]

        except Exception:
            # Return empty string on any error (don't fail the whole search)
            return ""
