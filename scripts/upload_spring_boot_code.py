#!/usr/bin/env python3
"""
Upload Spring Boot Code Examples to RAG Database

Extracts and uploads Spring Boot code samples from course materials.
"""

import os
from pathlib import Path
from rag_agent import RAGAgent


def main():
    """Upload Spring Boot code examples"""

    print("\n" + "="*70)
    print("SPRING BOOT CODE EXAMPLES → RAG DATABASE")
    print("="*70)

    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=True)

    # Path to extracted Spring Boot code
    code_dir = Path("/tmp/spring-boot-code/springboot-rest-api")

    if not code_dir.exists():
        print(f"❌ Code directory not found: {code_dir}")
        return

    # Find all Java files
    java_files = list(code_dir.rglob("*.java"))

    # Also look for other relevant files
    config_files = list(code_dir.rglob("*.properties")) + \
                   list(code_dir.rglob("*.yml")) + \
                   list(code_dir.rglob("*.yaml")) + \
                   list(code_dir.rglob("pom.xml"))

    all_files = java_files + config_files

    print(f"\n📁 Found {len(java_files)} Java files")
    print(f"📁 Found {len(config_files)} configuration files")
    print(f"📁 Total files to upload: {len(all_files)}")

    uploaded = 0
    errors = 0

    for file_path in all_files:
        try:
            # Skip macOS metadata files
            if '.__MACOSX' in str(file_path) or file_path.name.startswith('._'):
                continue

            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Skip empty files
            if not content.strip():
                continue

            # Get relative path for better organization
            rel_path = file_path.relative_to(code_dir)

            # Determine file type
            if file_path.suffix == '.java':
                file_type = 'java'
                category = 'controller' if 'Controller' in file_path.name else \
                          'model' if 'bean' in str(file_path.parent) else \
                          'application' if 'Application' in file_path.name else \
                          'test' if 'test' in str(file_path) else 'java'
            elif file_path.suffix in ['.properties', '.yml', '.yaml']:
                file_type = 'config'
                category = 'configuration'
            elif file_path.name == 'pom.xml':
                file_type = 'maven'
                category = 'build'
            else:
                file_type = 'other'
                category = 'misc'

            # Metadata
            metadata = {
                'source': 'spring_boot_course',
                'file_name': file_path.name,
                'file_path': str(rel_path),
                'file_type': file_type,
                'category': category,
                'language': 'java' if file_type == 'java' else 'config',
                'framework': 'spring_boot',
                'features': ['spring-boot', 'rest-api', 'java', 'backend']
            }

            # Create card ID based on file path
            card_id = f"springboot-{hash(str(rel_path)) % 100000:05d}"

            # Upload to RAG
            artifact_id = rag.store_artifact(
                artifact_type="code_example",
                card_id=card_id,
                task_title=f"Spring Boot: {rel_path}",
                content=content,
                metadata=metadata
            )

            if artifact_id:
                uploaded += 1
                print(f"   ✅ Uploaded: {rel_path}")
            else:
                errors += 1

        except Exception as e:
            print(f"   ❌ Error uploading {file_path.name}: {e}")
            errors += 1
            continue

    # Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"✅ Successfully uploaded: {uploaded} files")
    print(f"❌ Errors: {errors}")
    print()

    # Verify RAG stats
    stats = rag.get_stats()
    print("📊 RAG Database Stats:")
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print("="*70)


if __name__ == "__main__":
    main()
