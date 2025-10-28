#!/usr/bin/env python3
"""
HuggingFace Research Strategy

WHY: Implements research strategy for the HuggingFace Hub API, enabling discovery
of machine learning models, datasets, and related code examples. Focuses on AI/ML
use cases and pre-trained models.

RESPONSIBILITY: Handles all HuggingFace-specific research operations:
- Search HuggingFace Hub models via REST API
- Fetch model README files for documentation
- Convert HuggingFace API responses to ResearchExample objects
- Score results by popularity (downloads)

PATTERNS:
- Strategy Pattern: Concrete implementation of ResearchStrategy
- Guard Clause Pattern: Early returns for validation (max 1 level nesting)
- List Comprehension: Process results without explicit loops
"""

import urllib.parse
import urllib.request
from typing import List

from research_exceptions import ResearchSourceError
from research.base_strategy import ResearchStrategy
from research.models import ResearchExample


class HuggingFaceResearchStrategy(ResearchStrategy):
    """
    Research strategy for HuggingFace Hub.

    Searches HuggingFace Hub for AI/ML models and their documentation.
    Uses download counts as a proxy for relevance/quality.
    """

    def get_source_name(self) -> str:
        """
        Get the name of this research source.

        Returns:
            Human-readable name "HuggingFace"
        """
        return "HuggingFace"

    def search(self, query: str, technologies: List[str], max_results: int = 5) -> List[ResearchExample]:
        """
        Search HuggingFace Hub for models.

        Builds multiple queries by combining base query with each technology,
        searches HuggingFace for each, and returns the top results by popularity.

        Args:
            query: Base search query
            technologies: List of technologies to search for
            max_results: Maximum results to return

        Returns:
            List of ResearchExample objects sorted by relevance (download count)
        """
        # Guard clause: validate inputs
        if not query:
            return []

        # Build queries using base class method
        queries = self._build_queries(query, technologies)

        # Calculate results per query
        results_per_query = max(1, max_results // len(queries) + 1)

        # Search each query (list comprehension - no nested loops)
        all_results = [
            self._search_huggingface(q, results_per_query)
            for q in queries
        ]

        # Flatten results (list comprehension)
        examples = [example for results in all_results for example in results]

        # Sort by relevance (download-based score) and limit
        examples.sort(key=lambda x: x.relevance_score, reverse=True)
        return examples[:max_results]

    def _search_huggingface(self, query: str, limit: int) -> List[ResearchExample]:
        """
        Search HuggingFace API for models.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of ResearchExample objects from HuggingFace

        Raises:
            ResearchSourceError: If HuggingFace API request fails
        """
        try:
            # Build HuggingFace API URL
            encoded_query = urllib.parse.quote(query)
            url = f"https://huggingface.co/api/models?search={encoded_query}&limit={limit}"

            # Fetch data using base class method
            data = self._fetch_url(url)

            # Convert to ResearchExample objects (list comprehension)
            return [
                self._create_example_from_model(model)
                for model in data[:limit]
            ]

        except ResearchSourceError:
            # Re-raise ResearchSourceError as-is
            raise
        except Exception as e:
            raise ResearchSourceError(
                self.get_source_name(),
                f"HuggingFace search failed for query: {query}",
                cause=e
            )

    def _create_example_from_model(self, model: dict) -> ResearchExample:
        """
        Create ResearchExample from HuggingFace model data.

        Args:
            model: HuggingFace API response model dictionary

        Returns:
            ResearchExample object with HuggingFace data
        """
        model_id = model.get('modelId', '')

        # Fetch README content
        readme_content = self._fetch_readme(model_id)

        # Calculate relevance score from downloads (normalize to 0-1 range)
        downloads = model.get('downloads', 0)
        relevance_score = downloads / 1000.0

        return ResearchExample(
            title=model_id if model_id else 'Unknown',
            content=readme_content,
            source="HuggingFace",
            url=f"https://huggingface.co/{model_id}" if model_id else None,
            language="Python",  # Most HuggingFace models use Python
            tags=model.get('tags', []),
            relevance_score=relevance_score
        )

    def _fetch_readme(self, model_id: str) -> str:
        """
        Fetch model README content from HuggingFace.

        Args:
            model_id: HuggingFace model identifier (e.g., "bert-base-uncased")

        Returns:
            README content as string (limited to 5000 chars), or empty string on error
        """
        # Guard clause: return empty for invalid model ID
        if not model_id:
            return ""

        try:
            # Construct URL to raw README
            url = f"https://huggingface.co/{model_id}/raw/main/README.md"

            request = urllib.request.Request(url)
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                # Limit content size to prevent memory issues
                return response.read().decode('utf-8', errors='ignore')[:5000]

        except Exception:
            # Return empty string on any error (don't fail the whole search)
            return ""
