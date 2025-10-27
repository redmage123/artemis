#!/usr/bin/env python3
"""
Upload Bootstrap 5 From Scratch Course Code Examples to RAG
Extracts ZIP files and uploads HTML/CSS/JS code as examples
"""

import sys
import hashlib
import zipfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_agent import RAGAgent
from artemis_logger import ArtemisLogger


def extract_and_upload_zip(zip_path: Path, project_name: str, rag: RAGAgent, logger: ArtemisLogger):
    """
    Extract ZIP file and upload code examples to RAG.

    Args:
        zip_path: Path to ZIP file
        project_name: Name of the project
        rag: RAG agent instance
        logger: Logger instance

    Returns:
        Number of files uploaded
    """
    import tempfile
    import shutil

    # Create temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Extract ZIP
        logger.log(f"   Extracting: {zip_path.name}", "INFO")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_path)

        # Find code files
        code_files = list(temp_path.rglob("*.html")) + \
                     list(temp_path.rglob("*.css")) + \
                     list(temp_path.rglob("*.js")) + \
                     list(temp_path.rglob("*.scss"))

        uploaded_count = 0
        for code_file in code_files:
            try:
                # Read file content
                with open(code_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Skip empty files
                if not content.strip():
                    continue

                # Determine language
                ext = code_file.suffix.lower()
                lang_map = {
                    '.html': 'html',
                    '.css': 'css',
                    '.scss': 'scss',
                    '.js': 'javascript'
                }
                language = lang_map.get(ext, 'text')

                # Upload to RAG
                relative_path = code_file.relative_to(temp_path)
                rag.store_artifact(
                    artifact_type="code_example",
                    card_id=f"bootstrap-course-{hashlib.md5(project_name.encode()).hexdigest()[:8]}",
                    task_title=f"{project_name}: {relative_path}",
                    content=content,
                    metadata={
                        "language": language,
                        "framework": "bootstrap5",
                        "source": "Bootstrap 5 From Scratch Course",
                        "project": project_name,
                        "filename": code_file.name,
                        "file_path": str(relative_path)
                    }
                )
                uploaded_count += 1

            except Exception as e:
                logger.log(f"   ⚠️  Failed to upload {code_file.name}: {e}", "WARNING")

        return uploaded_count


def main():
    """Upload Bootstrap 5 Course code examples"""

    print("\n" + "="*70)
    print("BOOTSTRAP 5 FROM SCRATCH COURSE → RAG")
    print("="*70)

    # Initialize
    logger = ArtemisLogger()
    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=True)

    # Base path for course
    course_path = Path("/home/bbrelin/Downloads/Bootstrap 5 From Scratch  Build 5 Modern Websites/"
                      "[TutsNode.net] - Bootstrap 5 From Scratch  Build 5 Modern Websites")

    if not course_path.exists():
        print(f"❌ Course directory not found: {course_path}")
        return 1

    # Projects to upload
    projects = [
        {
            "name": "Bootstrap Sandbox",
            "zip": course_path / "1. Getting Started" / "6.1 bootstrap-sandbox.zip"
        },
        {
            "name": "Bootstrap Starter Template",
            "zip": course_path / "6. Custom Sass Workflow & Starter Template" / "5.1 bs5-simple-starter.zip"
        },
        {
            "name": "Mini Projects",
            "zip": course_path / "5. Mini-Project Challenges" / "1.1 mini-projects-starter.zip"
        },
        {
            "name": "Ebook Website",
            "zip": course_path / "7. Website 1 - Ebook Website" / "2.1 ebook-website-final.zip"
        },
        {
            "name": "Corso Training Website",
            "zip": course_path / "8. Website 2 - Corso Training Website" / "2.1 corso-website-final.zip"
        },
        {
            "name": "Portfolio Website",
            "zip": course_path / "9. Website 3 - Portfolio Website" / "2.1 portfolio-website-final.zip"
        },
        {
            "name": "Yavin Office Design",
            "zip": course_path / "10. Website 4 - Yavin Office Design" / "2.1 yavin-website-final.zip"
        },
        {
            "name": "Vera Software Solutions",
            "zip": course_path / "11. Website 5 - Vera Software Solutions" / "2.1 vera-website-final.zip"
        }
    ]

    total_uploaded = 0

    for project in projects:
        print(f"\n📦 Processing: {project['name']}")

        if not project['zip'].exists():
            print(f"   ⚠️  ZIP not found: {project['zip'].name}")
            continue

        try:
            count = extract_and_upload_zip(
                zip_path=project['zip'],
                project_name=project['name'],
                rag=rag,
                logger=logger
            )
            print(f"   ✅ Uploaded {count} code files")
            total_uploaded += count

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

    # Show final stats
    print(f"\n{'='*70}")
    print(f"✅ Total code files uploaded: {total_uploaded}")

    if total_uploaded > 0:
        print("\n📊 RAG Database Stats:")
        stats = rag.get_stats()
        print(f"   Total artifacts: {stats['total_artifacts']}")
        print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")

    print("="*70)
    return 0


if __name__ == "__main__":
    exit(main())
