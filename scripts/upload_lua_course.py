#!/usr/bin/env python3
"""
Upload Lua Programming Course Materials to RAG Database

Uploads all PDF lecture notes from the Complete Lua Programming Course.
"""

import os
from pathlib import Path
from upload_pdf_to_rag import PDFToRAGUploader


def main():
    """Upload Lua course PDFs"""

    print("\n" + "="*70)
    print("LUA PROGRAMMING COURSE → RAG DATABASE")
    print("="*70)

    uploader = PDFToRAGUploader()

    # Find all Lua course PDFs
    lua_course_dir = Path("/home/bbrelin/Downloads/GetFreeCourses.Co-Udemy-The Complete Lua Programming Course From Zero to Expert")

    if not lua_course_dir.exists():
        print(f"❌ Course directory not found: {lua_course_dir}")
        return

    # Find all PDF files
    pdf_files = sorted(lua_course_dir.rglob("*.pdf"))

    print(f"\n📁 Found {len(pdf_files)} PDF files")
    print(f"📚 Course: The Complete Lua Programming Course From Zero to Expert")

    successful_uploads = 0
    failed_uploads = 0

    # Upload each PDF sequentially
    for i, pdf_path in enumerate(pdf_files, 1):
        # Extract chapter/section from parent directory
        section = pdf_path.parent.name
        file_name = pdf_path.stem

        print(f"\n{'='*70}")
        print(f"📄 FILE {i}/{len(pdf_files)}")
        print(f"{'='*70}")
        print(f"   Section: {section}")
        print(f"   File: {file_name}")

        try:
            # Create descriptive title
            title = f"Lua Course - {section} - {file_name}"

            chunks_uploaded = uploader.upload_pdf_to_rag(
                pdf_path=pdf_path,
                book_title=title,
                author="Udemy - Complete Lua Course",
                chunk_size=3  # Smaller chunks for course materials
            )

            if chunks_uploaded > 0:
                successful_uploads += 1
                print(f"   ✅ Successfully uploaded {i}/{len(pdf_files)}")
            else:
                failed_uploads += 1
                print(f"   ❌ Failed to upload {i}/{len(pdf_files)}")

        except Exception as e:
            print(f"\n   ❌ Error uploading {i}/{len(pdf_files)}: {e}")
            failed_uploads += 1
            continue

    # Final Summary
    print("\n" + "="*70)
    print("FINAL UPLOAD SUMMARY")
    print("="*70)
    print(f"📚 Total PDFs processed: {len(pdf_files)}")
    print(f"✅ Successfully uploaded: {successful_uploads}")
    print(f"❌ Failed uploads: {failed_uploads}")
    print(f"📊 Total chunks uploaded: {uploader.uploaded_count}")
    print(f"❌ Total errors: {uploader.error_count}")
    print("="*70)

    # Verify RAG stats
    print("\n📊 RAG Database Stats:")
    stats = uploader.rag.get_stats()
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
    print("="*70)


if __name__ == "__main__":
    main()
