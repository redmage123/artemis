#!/usr/bin/env python3
"""
Upload Bootstrap: The Ultimate Guide to RAG
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upload_epub_to_rag import EPUBToRAGUploader


def main():
    """Upload Bootstrap Ultimate Guide EPUB"""

    print("\n" + "="*70)
    print("BOOTSTRAP: THE ULTIMATE GUIDE → RAG")
    print("="*70)

    uploader = EPUBToRAGUploader()

    book_path = Path("/home/bbrelin/Downloads/Bootstrap The Ultimate Guide/Bootstrap The Ultimate Guide.epub")

    if not book_path.exists():
        print(f"❌ Book not found: {book_path}")
        return 1

    print(f"\n📚 Uploading: Bootstrap: The Ultimate Guide")
    print(f"   Format: EPUB")
    print(f"   Path: {book_path}")

    try:
        # Upload the book
        chunks_uploaded = uploader.upload_epub_to_rag(
            epub_path=book_path,
            book_title="Bootstrap: The Ultimate Guide",
            author="Unknown",
            chunk_size=10  # 10 chapters per chunk
        )

        if chunks_uploaded > 0:
            print(f"\n✅ Successfully uploaded {chunks_uploaded} chunks")

            # Show RAG stats
            print("\n📊 RAG Database Stats:")
            stats = uploader.rag.get_stats()
            print(f"   Total artifacts: {stats['total_artifacts']}")
            print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
            print("="*70)

            return 0
        else:
            print("\n❌ Upload failed")
            return 1

    except Exception as e:
        print(f"\n❌ Error uploading: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
