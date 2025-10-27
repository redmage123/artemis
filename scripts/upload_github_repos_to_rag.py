#!/usr/bin/env python3
"""
Upload Newly Cloned GitHub Repositories to RAG Database

Uses intelligent quality scoring to select the best code examples from each repository.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
from rag_agent import RAGAgent


# List of newly cloned repositories
NEWLY_CLONED_REPOS = [
    'automate', 'linux_fundamentals', 'nimcp', 'agentic', 'JavaExamples2024',
    'esa-webinar', 'agent_demo', 'aiops_infrastructure', 'FarmersAssistent',
    'codespace_demo', 'langchain-course', 'cplusplus', 'refactor_datascience',
    'functional_python', 'jenkins', 'example-repo', 'ethereum-workshop',
    'financialengineering', 'nltk', 'CitiProject1', 'deep-learning-sklearn',
    'pushtechnology', 'kubernetes-course', 'ds-graduate-course', 'anomaly_detection',
    'problem_solvers', 'lambda-calculus', 'copper-analysis', 'terraform-course',
    'dataanalysis', 'terraform_scripts', 'iac', 'CitiDataScience', 'devops-course',
    'hadoop', 'Introduction-to-Saltstack', 'perl-programming-introduction',
    'bash-shell-programming', 'postgressql-developers', 'Introduction-to-hyperledger',
    'python-for-network-engineers', 'basiclinux', 'deep_learning_tensorflow',
    'btc-introductory-workshop', 'pythonfortooldevelopers', 'git', 'python-django',
    'advancedpython', 'JavaExamples', 'btcworkshop', 'GettingandCleaningDataProject',
    'datasciencecoursera', 'project1', 'test1', 'demo', 'margadh'
]


class GitHubRepoUploader:
    """Upload code examples from cloned GitHub repositories to RAG"""

    def __init__(self, rag_db_path: str = '../.artemis_data/rag_db'):
        self.rag = RAGAgent(db_path=rag_db_path, verbose=True)
        self.uploaded_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def calculate_code_quality(self, file_path: Path) -> float:
        """Calculate quality score for code file based on various metrics"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Size metrics
            lines = content.split('\n')
            line_count = len(lines)

            # Basic quality heuristics
            quality = 0.5  # Base score

            # Prefer medium-sized files
            if 20 <= line_count <= 300:
                quality += 0.2
            elif 10 <= line_count <= 500:
                quality += 0.1

            # Has documentation
            if '"""' in content or "'''" in content or '//' in content or '/*' in content:
                quality += 0.15

            # Has imports
            if 'import ' in content or 'require(' in content or 'package ' in content:
                quality += 0.1

            # Has functions/classes
            if 'def ' in content or 'class ' in content or 'function ' in content:
                quality += 0.1

            # Not too many empty lines
            empty_lines = sum(1 for line in lines if line.strip() == '')
            if line_count > 0 and empty_lines / line_count < 0.3:
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
            '.scala': 'scala',
            '.sh': 'bash',
            '.ps1': 'powershell',
            '.tf': 'terraform',
            '.pl': 'perl',
            '.r': 'r',
            '.sql': 'sql',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.md': 'markdown'
        }
        return ext_map.get(file_path.suffix.lower(), 'unknown')

    def extract_description(self, file_path: Path, content: str) -> str:
        """Extract description from file"""
        lines = content.split('\n')[:10]

        for line in lines:
            line = line.strip()
            if line.startswith('"""') or line.startswith("'''"):
                return line.strip('"').strip("'").strip()
            elif line.startswith('//') or line.startswith('#'):
                desc = line.lstrip('/#').strip()
                if len(desc) > 20:
                    return desc

        return f"Code example from {file_path.stem}"

    def upload_code_file(self, file_path: Path, repo_name: str) -> bool:
        """Upload a single code file to RAG"""
        try:
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
            card_id = f"github-{repo_name}-{file_hash}"

            # Prepare metadata
            metadata = {
                'source': 'github_repository',
                'repo_name': repo_name,
                'file_path': str(file_path),
                'language': language,
                'quality_score': quality_score,
                'file_size_bytes': len(content),
                'line_count': len(content.split('\n')),
                'features': [f'{repo_name}_example', language, 'github_code']
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
        max_files: int = 30
    ) -> int:
        """Upload code examples from a repository"""
        print(f"\n{'='*70}")
        print(f"📁 Repository: {repo_name}")
        print(f"{'='*70}")

        repo_path_obj = Path(repo_path)

        if not repo_path_obj.exists():
            print(f"   ❌ Path does not exist: {repo_path}")
            return 0

        # Common code extensions
        code_extensions = [
            '.py', '.ipynb', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c',
            '.rb', '.php', '.cs', '.swift', '.kt', '.scala', '.sh', '.ps1',
            '.tf', '.pl', '.r', '.sql'
        ]

        # Find all matching files
        all_files = []
        for ext in code_extensions:
            all_files.extend(repo_path_obj.rglob(f'*{ext}'))

        # Filter out test files and build directories
        filtered_files = [
            f for f in all_files
            if not any(exclude in str(f) for exclude in [
                '/test/', '/tests/', '/__pycache__/', '/node_modules/',
                '/vendor/', '/build/', '/dist/', '/.git/'
            ])
        ]

        print(f"   Found {len(filtered_files)} code files")

        if not filtered_files:
            print(f"   ⏭️  No code files found")
            return 0

        # Score and sort by quality
        files_with_scores = []
        for file_path in filtered_files[:500]:  # Limit initial scan
            quality = self.calculate_code_quality(file_path)
            if quality >= 0.5:  # Pre-filter
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
    print("GITHUB REPOSITORIES → RAG DATABASE")
    print("="*70)

    uploader = GitHubRepoUploader()

    # Upload each newly cloned repository
    total_uploaded = 0
    repos_base_path = Path('/home/bbrelin/src/repos')

    for repo_name in NEWLY_CLONED_REPOS:
        repo_path = repos_base_path / repo_name

        count = uploader.upload_repository(
            str(repo_path),
            repo_name,
            max_files=30  # Limit to top 30 files per repo
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
