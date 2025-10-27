#!/usr/bin/env python3
"""
Upload Local Repository Code Examples to RAG Database

Scans local repositories for high-quality code examples and uploads them to RAG.
Uses intelligent sampling to avoid overwhelming the database with too many examples.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
from rag_agent import RAGAgent


class LocalRepoUploader:
    """Upload code examples from local repositories to RAG"""

    def __init__(self, rag_db_path: str = '../.artemis_data/rag_db'):
        self.rag = RAGAgent(db_path=rag_db_path, verbose=True)
        self.uploaded_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def calculate_code_quality(self, file_path: Path) -> float:
        """
        Calculate quality score for code file based on various metrics

        Returns: 0.0-1.0 score (higher is better)
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Size metrics
            lines = content.split('\n')
            line_count = len(lines)
            char_count = len(content)

            # Basic quality heuristics
            quality = 0.5  # Base score

            # Prefer medium-sized files (not too small, not too large)
            if 20 <= line_count <= 300:
                quality += 0.2
            elif 10 <= line_count <= 500:
                quality += 0.1

            # Has documentation (comments, docstrings)
            if '"""' in content or "'''" in content or '//' in content or '/*' in content:
                quality += 0.15

            # Has imports (suggests real code, not just snippets)
            if 'import ' in content or 'require(' in content or 'package ' in content:
                quality += 0.1

            # Has functions/classes (structured code)
            if 'def ' in content or 'class ' in content or 'function ' in content:
                quality += 0.1

            # Not too many empty lines (suggests quality formatting)
            empty_lines = sum(1 for line in lines if line.strip() == '')
            if empty_lines / line_count < 0.3:
                quality += 0.05

            return min(1.0, quality)

        except Exception:
            return 0.0

    def detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.ipynb': 'jupyter_notebook',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala'
        }
        return ext_map.get(file_path.suffix.lower(), 'unknown')

    def extract_description(self, file_path: Path, content: str) -> str:
        """Extract description from file (docstrings, comments, README, etc.)"""
        lines = content.split('\n')[:10]  # First 10 lines

        # Try to find description in comments
        for line in lines:
            line = line.strip()
            if line.startswith('"""') or line.startswith("'''"):
                return line.strip('"\'').strip()
            elif line.startswith('//') or line.startswith('#'):
                desc = line.lstrip('/#').strip()
                if len(desc) > 20:
                    return desc

        # Fallback: use file name
        return f"Code example from {file_path.stem}"

    def upload_code_file(self, file_path: Path, repo_name: str) -> bool:
        """Upload a single code file to RAG"""
        try:
            # Read content
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Skip if too small or too large
            if len(content) < 50 or len(content) > 100_000:
                self.skipped_count += 1
                return False

            # Calculate quality
            quality_score = self.calculate_code_quality(file_path)

            # Skip low-quality files
            if quality_score < 0.5:
                self.skipped_count += 1
                return False

            # Detect language
            language = self.detect_language(file_path)

            # Extract description
            description = self.extract_description(file_path, content)

            # Create unique ID
            file_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
            card_id = f"local-repo-{repo_name}-{file_hash}"

            # Prepare metadata
            metadata = {
                'source': 'local_repository',
                'repo_name': repo_name,
                'file_path': str(file_path),
                'language': language,
                'quality_score': quality_score,
                'file_size_bytes': len(content),
                'line_count': len(content.split('\n')),
                'features': [f'{repo_name}_example', language, 'local_code']
            }

            # Store in RAG
            artifact_id = self.rag.store_artifact(
                artifact_type="code_example",
                card_id=card_id,
                task_title=f"{repo_name}: {file_path.name}",
                content=f"# {description}\n\n```{language}\n{content}\n```",
                metadata=metadata
            )

            if artifact_id:
                self.uploaded_count += 1
                return True
            else:
                self.error_count += 1
                return False

        except Exception as e:
            print(f"   ❌ Error uploading {file_path.name}: {e}")
            self.error_count += 1
            return False

    def upload_repository(
        self,
        repo_path: str,
        repo_name: str,
        file_extensions: List[str],
        max_files: int = 50
    ) -> int:
        """
        Upload code examples from a repository

        Args:
            repo_path: Path to repository
            repo_name: Name of repository
            file_extensions: List of file extensions to include (e.g., ['.py', '.js'])
            max_files: Maximum number of files to upload

        Returns:
            Number of files uploaded
        """
        print(f"\n{'='*70}")
        print(f"📁 Repository: {repo_name}")
        print(f"{'='*70}")

        repo_path_obj = Path(repo_path)

        if not repo_path_obj.exists():
            print(f"   ❌ Path does not exist: {repo_path}")
            return 0

        # Find all matching files
        all_files = []
        for ext in file_extensions:
            all_files.extend(repo_path_obj.rglob(f'*{ext}'))

        print(f"   Found {len(all_files)} {', '.join(file_extensions)} files")

        # Score and sort by quality
        files_with_scores = []
        for file_path in all_files[:500]:  # Limit initial scan
            quality = self.calculate_code_quality(file_path)
            files_with_scores.append((file_path, quality))

        # Sort by quality (best first)
        files_with_scores.sort(key=lambda x: x[1], reverse=True)

        # Upload top files
        uploaded_this_repo = 0
        for file_path, quality in files_with_scores[:max_files]:
            print(f"   📄 {file_path.name} (quality: {quality:.2f})")
            if self.upload_code_file(file_path, repo_name):
                uploaded_this_repo += 1

        print(f"   ✅ Uploaded {uploaded_this_repo} files from {repo_name}")
        return uploaded_this_repo


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("LOCAL REPOSITORY CODE EXAMPLES → RAG DATABASE")
    print("="*70)

    uploader = LocalRepoUploader()

    # Define repositories to upload
    repositories = [
        {
            'path': '/home/bbrelin/src/repos/langchain-tutorials',
            'name': 'langchain-tutorials',
            'extensions': ['.py', '.ipynb'],
            'max_files': 30  # Upload all
        },
        {
            'path': '/home/bbrelin/src/repos/fabric-samples',
            'name': 'fabric-samples',
            'extensions': ['.js', '.go', '.java'],
            'max_files': 50  # Sample from 215
        },
        {
            'path': '/home/bbrelin/src/repos/hsbc_examples',
            'name': 'hsbc_examples',
            'extensions': ['.py', '.js'],
            'max_files': 100  # Sample from 9,349 (need intelligent sampling!)
        },
        {
            'path': '/home/bbrelin/src/repos/basicpython',
            'name': 'basicpython',
            'extensions': ['.py'],
            'max_files': 30
        },
        {
            'path': '/home/bbrelin/src/repos/intermediatepython',
            'name': 'intermediatepython',
            'extensions': ['.py'],
            'max_files': 30
        },
        {
            'path': '/home/bbrelin/src/repos/CodeBERT',
            'name': 'CodeBERT',
            'extensions': ['.py'],
            'max_files': 30
        },
        {
            'path': '/home/bbrelin/src/repos/pandas-timeseries',
            'name': 'pandas-timeseries',
            'extensions': ['.py', '.ipynb'],
            'max_files': 30
        }
    ]

    # Upload each repository
    total_uploaded = 0
    for repo in repositories:
        count = uploader.upload_repository(
            repo['path'],
            repo['name'],
            repo['extensions'],
            repo['max_files']
        )
        total_uploaded += count

    # Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"✅ Total uploaded: {uploader.uploaded_count}")
    print(f"⏭️  Skipped (low quality): {uploader.skipped_count}")
    print(f"❌ Errors: {uploader.error_count}")
    print()

    # Verify RAG stats
    stats = uploader.rag.get_stats()
    print("📊 RAG Database Stats:")
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print(f"   Notebook examples: {stats['by_type'].get('notebook_example', 0)}")
    print("="*70)


if __name__ == "__main__":
    main()
