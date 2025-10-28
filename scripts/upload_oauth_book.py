#!/usr/bin/env python3
"""
Upload OAuth 2.0 Book to RAG

Uploads "Getting Started with OAuth 2.0" by Ryan Boyd to the RAG database.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upload_pdf_to_rag import upload_pdf_to_rag
from artemis_logger import ArtemisLogger


def main():
    """Upload OAuth 2.0 book to RAG"""

    logger = ArtemisLogger()

    oauth_book = Path("/home/bbrelin/Downloads/Getting Started with OAuth 2.0 (Ryan Boyd) (Z-Library).pdf")

    if not oauth_book.exists():
        print(f"❌ OAuth book not found: {oauth_book}")
        return 1

    print("\n" + "="*70)
    print("OAUTH 2.0 BOOK → RAG")
    print("="*70)

    # Upload the PDF
    result = upload_pdf_to_rag(
        pdf_path=oauth_book,
        book_title="Getting Started with OAuth 2.0",
        metadata={
            'author': 'Ryan Boyd',
            'publisher': "O'Reilly",
            'category': 'security',
            'topics': ['oauth', 'authentication', 'authorization', 'api_security', 'web_security'],
            'language': 'general',  # OAuth concepts apply to any language
            'skill_level': 'beginner'
        }
    )

    if result['success']:
        print(f"\n✅ Successfully uploaded OAuth 2.0 book")
        print(f"   Pages: {result['total_pages']}")
        print(f"   Chunks: {result['chunks_created']}")
        print(f"   Artifact ID: {result['artifact_id']}")
    else:
        print(f"\n❌ Failed to upload: {result.get('error', 'Unknown error')}")
        return 1

    print("="*70)
    return 0


if __name__ == "__main__":
    exit(main())
