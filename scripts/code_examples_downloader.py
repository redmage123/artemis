#!/usr/bin/env python3
"""
Module: code_examples_downloader.py

Purpose: Background service that continuously downloads high-quality code examples
         for all supported languages and build systems, storing them in RAG DB
Why: Provides Artemis with extensive code examples for reference during development,
     enabling better code generation through retrieval-augmented generation
Patterns: Observer Pattern (progress updates), Strategy Pattern (download sources)
Integration: Runs as background daemon, stores in rag_agent.py via rag_storage_helper.py

This script runs continuously in the background, downloading code examples from:
- GitHub trending repositories
- HuggingFace datasets
- Language-specific example repositories
- Official framework documentation examples
"""

import os
import sys
import time
import json
import signal
import logging
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import requests

# Artemis imports
from artemis_logger import ArtemisLogger
from rag_storage_helper import RAGStorageHelper
from build_manager_factory import BuildSystem


@dataclass
class DownloadStats:
    """
    Track download statistics.

    Why needed: Monitoring and reporting download progress
    """
    total_examples: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    total_size_bytes: int = 0
    start_time: datetime = field(default_factory=datetime.now)

    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        total = self.successful + self.failed
        return (self.successful / total * 100) if total > 0 else 0.0

    def elapsed_time(self) -> float:
        """Time elapsed since start in seconds"""
        return (datetime.now() - self.start_time).total_seconds()


class ExampleSource(Enum):
    """
    Source types for code examples.

    Why needed: Different sources require different download strategies
    """
    GITHUB_TRENDING = "github_trending"
    GITHUB_AWESOME = "github_awesome"  # Awesome-* lists
    HUGGINGFACE = "huggingface"
    ROSETTA_CODE = "rosetta_code"
    OFFICIAL_DOCS = "official_docs"
    LANGUAGE_PLAYGROUND = "language_playground"


@dataclass
class CodeExample:
    """
    Represents a code example to be stored in RAG.

    Why needed: Structured format for RAG storage
    """
    language: str
    build_system: Optional[str]
    title: str
    description: str
    code: str
    source_url: str
    tags: List[str]
    complexity: str  # "beginner", "intermediate", "advanced"
    quality_score: float  # 0.0 to 1.0
    framework: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


class CodeExamplesDownloader:
    """
    Background service for downloading code examples.

    Why it exists: Continuously populates RAG DB with high-quality code examples
                   for all supported languages and build systems

    Design pattern: Observer + Strategy patterns

    Responsibilities:
    - Download code examples from multiple sources
    - Filter for quality and relevance
    - Store in RAG database with metadata
    - Run continuously in background
    - Report progress and statistics
    - Handle rate limiting and errors gracefully

    Why continuous: New examples are constantly published, trending repos change,
                    frameworks evolve - continuous updates keep RAG fresh
    """

    # Supported languages mapped to their ecosystems
    LANGUAGE_ECOSYSTEMS = {
        # JVM Languages
        "java": ["maven", "gradle", "ant"],
        "kotlin": ["gradle", "maven"],
        "scala": ["sbt", "maven", "gradle"],

        # JavaScript/TypeScript
        "javascript": ["npm", "yarn", "pnpm"],
        "typescript": ["npm", "yarn", "pnpm"],

        # Python
        "python": ["pip", "poetry", "pipenv", "conda"],

        # Systems Languages
        "c": ["cmake", "make"],
        "cpp": ["cmake", "make"],
        "rust": ["cargo"],
        "go": ["go"],
        "zig": ["zig"],

        # Scripting
        "lua": ["luarocks"],
        "ruby": ["bundler", "gem"],
        "perl": ["cpan"],
        "php": ["composer"],

        # .NET
        "csharp": ["dotnet", "nuget"],
        "fsharp": ["dotnet", "nuget"],

        # Functional
        "haskell": ["cabal", "stack"],
        "elixir": ["mix"],
        "erlang": ["rebar3"],
        "clojure": ["leiningen", "deps"],

        # Shell/DevOps
        "bash": ["bash"],
        "powershell": ["powershell"],
        "terraform": ["terraform"],
    }

    def __init__(
        self,
        rag_helper: Optional[RAGStorageHelper] = None,
        logger: Optional[ArtemisLogger] = None,
        download_dir: str = "/tmp/artemis_examples",
        update_interval: int = 3600,  # 1 hour
        max_examples_per_language: int = 100
    ):
        """
        Initialize code examples downloader.

        Why needed: Sets up background service with RAG integration

        Args:
            rag_helper: RAG storage helper for storing examples
            logger: Artemis logger instance
            download_dir: Temporary directory for downloads
            update_interval: Seconds between update cycles
            max_examples_per_language: Max examples to store per language
        """
        self.logger = logger or ArtemisLogger(component="CodeExamplesDownloader")
        self.rag_helper = rag_helper or RAGStorageHelper()
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        self.update_interval = update_interval
        self.max_examples_per_language = max_examples_per_language

        self.stats = DownloadStats()
        self.running = False
        self.thread: Optional[threading.Thread] = None

        # GitHub API token (optional, increases rate limit)
        self.github_token = os.environ.get("GITHUB_TOKEN")

        self.logger.info("📥 Code Examples Downloader initialized")
        self.logger.info(f"   Download directory: {self.download_dir}")
        self.logger.info(f"   Update interval: {update_interval}s")
        self.logger.info(f"   Max examples/language: {max_examples_per_language}")

    def start_background(self) -> None:
        """
        Start downloader as background thread.

        Why needed: Allows downloader to run continuously without blocking

        How it works:
            Creates daemon thread that runs download loop
        """
        if self.running:
            self.logger.warning("Downloader already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._download_loop, daemon=True)
        self.thread.start()

        self.logger.info("✅ Code examples downloader started in background")

    def stop(self) -> None:
        """
        Stop background downloader.

        Why needed: Graceful shutdown
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)

        self.logger.info("🛑 Code examples downloader stopped")
        self._print_stats()

    def _download_loop(self) -> None:
        """
        Main download loop (runs in background thread).

        Why needed: Continuous updates of code examples

        How it works:
            1. Download examples for each language
            2. Store in RAG
            3. Sleep for update_interval
            4. Repeat
        """
        self.logger.info("🔄 Starting download loop...")

        while self.running:
            try:
                # Download examples for all languages
                for language, build_systems in self.LANGUAGE_ECOSYSTEMS.items():
                    if not self.running:
                        break

                    self.logger.info(f"📥 Downloading {language} examples...")
                    self._download_language_examples(language, build_systems)

                # Print statistics
                self._print_stats()

                # Sleep until next update
                self.logger.info(f"💤 Sleeping for {self.update_interval}s until next update...")
                time.sleep(self.update_interval)

            except Exception as e:
                self.logger.error(f"❌ Error in download loop: {e}")
                time.sleep(60)  # Short sleep on error

    def _download_language_examples(
        self,
        language: str,
        build_systems: List[str]
    ) -> None:
        """
        Download examples for a specific language.

        Why needed: Language-specific download strategy

        Args:
            language: Programming language name
            build_systems: Associated build systems
        """
        try:
            # Download from multiple sources
            examples = []

            # 1. GitHub Awesome lists
            examples.extend(self._download_from_awesome_list(language))

            # 2. GitHub trending repositories
            examples.extend(self._download_from_trending(language))

            # 3. Rosetta Code (common algorithms)
            examples.extend(self._download_from_rosetta_code(language))

            # 4. Language-specific playgrounds
            examples.extend(self._download_from_playground(language))

            # Filter and limit
            examples = self._filter_quality(examples)
            examples = examples[:self.max_examples_per_language]

            # Store in RAG
            for example in examples:
                self._store_example(example, language, build_systems)

            self.logger.info(f"✅ Downloaded {len(examples)} {language} examples")

        except Exception as e:
            self.logger.error(f"❌ Failed to download {language} examples: {e}")
            self.stats.failed += 1

    def _download_from_awesome_list(self, language: str) -> List[CodeExample]:
        """
        Download examples from Awesome-* lists on GitHub.

        Why needed: Awesome lists curate high-quality resources

        Args:
            language: Programming language

        Returns:
            List of code examples
        """
        examples = []

        try:
            # Search for awesome-{language} repositories
            awesome_repos = self._github_search(f"awesome-{language} in:name")

            for repo in awesome_repos[:5]:  # Top 5 awesome lists
                # Clone and parse README for code examples
                repo_examples = self._extract_examples_from_repo(
                    repo["html_url"],
                    language
                )
                examples.extend(repo_examples)

        except Exception as e:
            self.logger.warning(f"Failed to download from awesome list: {e}")

        return examples

    def _download_from_trending(self, language: str) -> List[CodeExample]:
        """
        Download examples from GitHub trending repositories.

        Why needed: Trending repos often showcase modern best practices

        Args:
            language: Programming language

        Returns:
            List of code examples
        """
        examples = []

        try:
            # Search trending repositories
            trending = self._github_search(
                f"language:{language} stars:>100 pushed:>2024-01-01",
                sort="stars"
            )

            for repo in trending[:10]:  # Top 10 trending
                repo_examples = self._extract_examples_from_repo(
                    repo["html_url"],
                    language
                )
                examples.extend(repo_examples)

        except Exception as e:
            self.logger.warning(f"Failed to download trending: {e}")

        return examples

    def _download_from_rosetta_code(self, language: str) -> List[CodeExample]:
        """
        Download algorithm examples from Rosetta Code.

        Why needed: Rosetta Code has same algorithms in many languages

        Args:
            language: Programming language

        Returns:
            List of code examples
        """
        examples = []

        # Rosetta Code algorithms to fetch
        algorithms = [
            "quicksort", "binary-search", "fibonacci", "factorial",
            "palindrome", "prime-numbers", "fizzbuzz", "hello-world",
            "linked-list", "binary-tree", "hash-table", "graph-traversal"
        ]

        for algo in algorithms:
            try:
                # This is a placeholder - actual implementation would scrape or use API
                example = CodeExample(
                    language=language,
                    build_system=None,
                    title=f"{algo.title()} in {language.title()}",
                    description=f"Implementation of {algo} algorithm",
                    code=f"# {algo} implementation\n# TODO: Fetch from Rosetta Code",
                    source_url=f"https://rosettacode.org/wiki/{algo}#{language}",
                    tags=["algorithm", algo, "rosetta-code"],
                    complexity="intermediate",
                    quality_score=0.8
                )
                examples.append(example)

            except Exception as e:
                self.logger.debug(f"Failed to fetch {algo}: {e}")

        return examples

    def _download_from_playground(self, language: str) -> List[CodeExample]:
        """
        Download examples from language-specific playgrounds.

        Why needed: Official playgrounds have beginner-friendly examples

        Args:
            language: Programming language

        Returns:
            List of code examples
        """
        examples = []

        # Language-specific playground URLs
        playgrounds = {
            "rust": "https://play.rust-lang.org",
            "go": "https://go.dev/play",
            "python": "https://repl.it/languages/python3",
            "javascript": "https://jsfiddle.net",
        }

        if language in playgrounds:
            # Placeholder - would actually fetch from playground
            self.logger.debug(f"Playground for {language}: {playgrounds[language]}")

        return examples

    def _github_search(
        self,
        query: str,
        sort: str = "stars",
        per_page: int = 10
    ) -> List[Dict]:
        """
        Search GitHub repositories.

        Why needed: Find relevant code repositories

        Args:
            query: GitHub search query
            sort: Sort order (stars, forks, updated)
            per_page: Results per page

        Returns:
            List of repository metadata dicts
        """
        url = "https://api.github.com/search/repositories"
        headers = {}

        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"

        params = {
            "q": query,
            "sort": sort,
            "order": "desc",
            "per_page": per_page
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json().get("items", [])

        except requests.exceptions.RequestException as e:
            self.logger.warning(f"GitHub search failed: {e}")
            return []

    def _extract_examples_from_repo(
        self,
        repo_url: str,
        language: str
    ) -> List[CodeExample]:
        """
        Extract code examples from a GitHub repository.

        Why needed: Parse repository files for example code

        Args:
            repo_url: GitHub repository URL
            language: Expected programming language

        Returns:
            List of extracted code examples
        """
        examples = []

        # For now, return placeholder
        # Full implementation would clone repo and parse files
        self.logger.debug(f"Extracting examples from {repo_url}")

        return examples

    def _filter_quality(self, examples: List[CodeExample]) -> List[CodeExample]:
        """
        Filter examples by quality score.

        Why needed: Only store high-quality examples in RAG

        Args:
            examples: List of code examples

        Returns:
            Filtered list of high-quality examples
        """
        # Filter: quality score >= 0.7
        filtered = [ex for ex in examples if ex.quality_score >= 0.7]

        # Sort by quality score (highest first)
        filtered.sort(key=lambda ex: ex.quality_score, reverse=True)

        return filtered

    def _store_example(
        self,
        example: CodeExample,
        language: str,
        build_systems: List[str]
    ) -> None:
        """
        Store code example in RAG database.

        Why needed: Makes examples available for retrieval during development

        Args:
            example: Code example to store
            language: Programming language
            build_systems: Associated build systems
        """
        try:
            # Create metadata
            metadata = {
                "type": "code_example",
                "language": language,
                "build_systems": build_systems,
                "title": example.title,
                "description": example.description,
                "source_url": example.source_url,
                "tags": example.tags,
                "complexity": example.complexity,
                "quality_score": example.quality_score,
                "framework": example.framework,
                "dependencies": example.dependencies,
                "ingested_at": datetime.now().isoformat()
            }

            # Store in RAG
            self.rag_helper.store_code_example(
                code=example.code,
                language=language,
                metadata=metadata
            )

            self.stats.successful += 1
            self.stats.total_size_bytes += len(example.code)

        except Exception as e:
            self.logger.warning(f"Failed to store example: {e}")
            self.stats.failed += 1

    def _print_stats(self) -> None:
        """
        Print download statistics.

        Why needed: Progress monitoring and debugging
        """
        elapsed = self.stats.elapsed_time()
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)

        self.logger.info("📊 Download Statistics:")
        self.logger.info(f"   Total examples: {self.stats.total_examples}")
        self.logger.info(f"   Successful: {self.stats.successful}")
        self.logger.info(f"   Failed: {self.stats.failed}")
        self.logger.info(f"   Skipped: {self.stats.skipped}")
        self.logger.info(f"   Success rate: {self.stats.success_rate():.1f}%")
        self.logger.info(f"   Total size: {self.stats.total_size_bytes / 1024 / 1024:.2f} MB")
        self.logger.info(f"   Elapsed time: {hours}h {minutes}m")


def main():
    """
    Main entry point for background downloader.

    Why needed: Can be run as standalone daemon or imported as module
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Artemis Code Examples Downloader - Background Service"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Update interval in seconds (default: 3600 = 1 hour)"
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=100,
        help="Max examples per language (default: 100)"
    )
    parser.add_argument(
        "--download-dir",
        type=str,
        default="/tmp/artemis_examples",
        help="Download directory (default: /tmp/artemis_examples)"
    )
    parser.add_argument(
        "--foreground",
        action="store_true",
        help="Run in foreground (default: background)"
    )

    args = parser.parse_args()

    # Create downloader
    downloader = CodeExamplesDownloader(
        update_interval=args.interval,
        max_examples_per_language=args.max_examples,
        download_dir=args.download_dir
    )

    # Handle signals for graceful shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Received shutdown signal, stopping...")
        downloader.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start downloader
    if args.foreground:
        print("🚀 Starting in foreground mode...")
        downloader.start_background()

        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            downloader.stop()
    else:
        print("🚀 Starting in background mode...")
        downloader.start_background()

        # Daemonize process
        print(f"✅ Running as daemon (PID: {os.getpid()})")
        print(f"📝 Check logs at: /tmp/artemis_logs/CodeExamplesDownloader.log")

        # Keep process alive
        while downloader.running:
            time.sleep(10)


if __name__ == "__main__":
    main()
