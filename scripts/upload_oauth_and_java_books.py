#!/usr/bin/env python3
"""
Upload OAuth 2.0 and Java Real World Projects Books to RAG

Uploads both security and Java books to the RAG database.
"""

import sys
from pathlib import Path

# Add src and scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from upload_pdf_to_rag import PDFToRAGUploader
from artemis_logger import ArtemisLogger


def main():
    """Upload OAuth and Java books to RAG"""

    logger = ArtemisLogger()

    # Book paths
    oauth_book = Path("/home/bbrelin/Downloads/Getting Started with OAuth 2.0 (Ryan Boyd) (Z-Library).pdf")
    java_book = Path("/home/bbrelin/Downloads/Java Real World Projects A pragmatic guide for building modern Java applications (Davi Vieira) (Z-Library).pdf")

    # Initialize uploader
    uploader = PDFToRAGUploader(rag_db_path='../.artemis_data/rag_db')

    print("\n" + "="*70)
    print("UPLOADING BOOKS TO RAG")
    print("="*70)

    # Upload OAuth book
    if oauth_book.exists():
        print("\n📚 Uploading: Getting Started with OAuth 2.0")
        print("-" * 70)

        try:
            result = uploader.upload_book(
                pdf_path=oauth_book,
                book_title="Getting Started with OAuth 2.0",
                metadata={
                    'author': 'Ryan Boyd',
                    'publisher': "O'Reilly Media",
                    'category': 'security',
                    'topics': ['oauth', 'oauth2', 'authentication', 'authorization', 'api_security', 'web_security', 'rest_api'],
                    'language': 'general',
                    'skill_level': 'beginner',
                    'year': '2012'
                }
            )

            if result['success']:
                print(f"\n✅ OAuth book uploaded successfully")
                print(f"   Pages: {result.get('total_pages', 'N/A')}")
                print(f"   Chunks: {result.get('chunks_created', 'N/A')}")
            else:
                print(f"\n❌ OAuth book upload failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"\n❌ Error uploading OAuth book: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n⚠️  OAuth book not found: {oauth_book}")

    # Upload Java book
    if java_book.exists():
        print("\n📚 Uploading: Java Real World Projects")
        print("-" * 70)

        try:
            result = uploader.upload_book(
                pdf_path=java_book,
                book_title="Java Real World Projects: A Pragmatic Guide",
                metadata={
                    'author': 'Davi Vieira',
                    'publisher': 'Packt Publishing',
                    'category': 'programming',
                    'topics': ['java', 'software_architecture', 'design_patterns', 'microservices', 'spring_boot', 'real_world_projects', 'backend'],
                    'language': 'java',
                    'skill_level': 'intermediate',
                    'year': '2023'
                }
            )

            if result['success']:
                print(f"\n✅ Java book uploaded successfully")
                print(f"   Pages: {result.get('total_pages', 'N/A')}")
                print(f"   Chunks: {result.get('chunks_created', 'N/A')}")
            else:
                print(f"\n❌ Java book upload failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"\n❌ Error uploading Java book: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n⚠️  Java book not found: {java_book}")

    # Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"   Total uploaded: {uploader.uploaded_count} chunks")
    print(f"   Errors: {uploader.error_count}")

    # Show RAG stats
    print("\n📊 RAG Database Stats:")
    stats = uploader.rag.get_stats()
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Knowledge base entries: {stats['by_type'].get('knowledge_base', 0)}")

    print("="*70)
    return 0


if __name__ == "__main__":
    exit(main())
