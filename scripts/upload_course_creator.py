#!/usr/bin/env python3
"""
Upload Course Creator Repository to RAG Database

Uploads high-quality code examples from the course-creator full-stack application.
"""

import hashlib
from pathlib import Path
from typing import List
from rag_agent import RAGAgent


class CourseCreatorUploader:
    """Upload course-creator code to RAG"""

    def __init__(self, rag_db_path: str = '../.artemis_data/rag_db'):
        self.rag = RAGAgent(db_path=rag_db_path, verbose=True)
        self.uploaded_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def calculate_code_quality(self, file_path: Path) -> float:
        """Calculate quality score for code file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            line_count = len(lines)

            quality = 0.5  # Base score

            # Prefer medium-sized files
            if 20 <= line_count <= 500:
                quality += 0.2
            elif 10 <= line_count <= 1000:
                quality += 0.1

            # Has documentation
            if '"""' in content or "'''" in content or '//' in content or '/*' in content:
                quality += 0.15

            # Has imports
            if 'import ' in content or 'require(' in content or 'from ' in content:
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
        """Detect programming language"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'react',
            '.ts': 'typescript',
            '.tsx': 'react-typescript',
            '.json': 'json',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.md': 'markdown',
            '.sh': 'bash',
            '.css': 'css',
            '.html': 'html'
        }
        return ext_map.get(file_path.suffix.lower(), 'unknown')

    def categorize_file(self, file_path: Path, repo_root: Path) -> str:
        """Categorize file based on path"""
        rel_path = str(file_path.relative_to(repo_root))

        if 'frontend' in rel_path:
            if 'component' in rel_path.lower():
                return 'react-component'
            elif 'service' in rel_path.lower() or 'api' in rel_path.lower():
                return 'frontend-service'
            elif 'hook' in rel_path.lower():
                return 'react-hook'
            else:
                return 'frontend'
        elif 'services' in rel_path:
            return 'backend-service'
        elif 'shared' in rel_path:
            if 'model' in rel_path.lower():
                return 'data-model'
            elif 'util' in rel_path.lower():
                return 'utility'
            else:
                return 'shared-code'
        elif 'test' in rel_path.lower():
            return 'test'
        elif 'config' in rel_path:
            return 'configuration'
        elif 'deploy' in rel_path:
            return 'deployment'
        elif 'script' in rel_path:
            return 'script'
        else:
            return 'other'

    def upload_code_file(self, file_path: Path, repo_root: Path) -> bool:
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

            # Detect language and category
            language = self.detect_language(file_path)
            category = self.categorize_file(file_path, repo_root)

            # Create unique ID
            rel_path = file_path.relative_to(repo_root)
            file_hash = hashlib.md5(str(rel_path).encode()).hexdigest()[:8]
            card_id = f"course-creator-{file_hash}"

            # Prepare metadata
            metadata = {
                'source': 'course_creator_repo',
                'repo_name': 'course-creator',
                'file_path': str(rel_path),
                'category': category,
                'language': language,
                'quality_score': quality_score,
                'file_size_bytes': len(content),
                'line_count': len(content.split('\n')),
                'features': ['course-creator', 'full-stack', category, language]
            }

            # Store in RAG
            artifact_id = self.rag.store_artifact(
                artifact_type="code_example",
                card_id=card_id,
                task_title=f"Course Creator: {rel_path}",
                content=f"```{language}\n{content}\n```",
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

    def upload_repository(self, repo_path: str, file_extensions: List[str], max_files: int = 100) -> int:
        """Upload code examples from course-creator repository"""
        print(f"\n{'='*70}")
        print(f"📁 Repository: course-creator")
        print(f"{'='*70}")

        repo_root = Path(repo_path)

        if not repo_root.exists():
            print(f"   ❌ Path does not exist: {repo_path}")
            return 0

        # Find all matching files
        all_files = []
        for ext in file_extensions:
            all_files.extend(repo_root.rglob(f'*{ext}'))

        # Filter out unwanted directories
        exclude_patterns = [
            'node_modules',
            '__pycache__',
            '.git',
            '.venv',
            'venv',
            'dist',
            'build',
            '.pytest_cache',
            '.aider',
            'lab-storage',
            '.github'
        ]

        filtered_files = []
        for file_path in all_files:
            if not any(pattern in str(file_path) for pattern in exclude_patterns):
                filtered_files.append(file_path)

        print(f"   Found {len(filtered_files)} {', '.join(file_extensions)} files (after filtering)")

        # Score and sort by quality
        files_with_scores = []
        for file_path in filtered_files[:1000]:  # Limit initial scan
            quality = self.calculate_code_quality(file_path)
            files_with_scores.append((file_path, quality))

        # Sort by quality (best first)
        files_with_scores.sort(key=lambda x: x[1], reverse=True)

        # Upload top files
        uploaded_this_repo = 0
        for file_path, quality in files_with_scores[:max_files]:
            rel_path = file_path.relative_to(repo_root)
            print(f"   📄 {rel_path} (quality: {quality:.2f})")
            if self.upload_code_file(file_path, repo_root):
                uploaded_this_repo += 1

        print(f"   ✅ Uploaded {uploaded_this_repo} files from course-creator")
        return uploaded_this_repo


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("COURSE-CREATOR REPOSITORY → RAG DATABASE")
    print("="*70)

    uploader = CourseCreatorUploader()

    # Upload course-creator repository
    uploader.upload_repository(
        repo_path='/home/bbrelin/src/repos/course-creator',
        file_extensions=['.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.yml', '.yaml'],
        max_files=100  # Upload top 100 quality files
    )

    # Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"✅ Total uploaded: {uploader.uploaded_count}")
    print(f"⏭️  Skipped (low quality/size): {uploader.skipped_count}")
    print(f"❌ Errors: {uploader.error_count}")
    print()

    # Verify RAG stats
    stats = uploader.rag.get_stats()
    print("📊 RAG Database Stats:")
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print("="*70)


if __name__ == "__main__":
    main()
