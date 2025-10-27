#!/usr/bin/env python3
"""
Upload C# Udemy Course Videos to RAG Database

Transcribes video lectures using Whisper and uploads transcripts as code examples.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict
import hashlib
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_agent import RAGAgent


class CSharpCourseUploader:
    """Upload C# course videos with transcription"""

    def __init__(self, rag_db_path: str = '../.artemis_data/rag_db'):
        """
        Initialize uploader.

        WHY: Video courses contain valuable code examples and explanations.
             Transcribing allows RAG to search lecture content.
        """
        self.rag = RAGAgent(db_path=rag_db_path, verbose=True)
        self.uploaded_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def transcribe_video(self, video_path: Path) -> str:
        """
        Transcribe video using OpenAI Whisper.

        WHY: Convert spoken content to searchable text.
        WHAT: Uses whisper for accurate transcription.

        Args:
            video_path: Path to video file

        Returns:
            Transcribed text
        """
        try:
            import whisper

            print(f"      🎙️  Transcribing: {video_path.name}")

            # Load whisper model (base is good balance of speed/accuracy)
            model = whisper.load_model("base")

            # Transcribe
            result = model.transcribe(str(video_path))

            return result["text"]

        except Exception as e:
            print(f"      ❌ Transcription failed: {e}")
            return ""

    def extract_code_from_transcript(self, transcript: str) -> List[str]:
        """
        Extract code snippets from transcript.

        WHY: Code examples are most valuable for RAG validation.
        WHAT: Looks for C# keywords and code patterns.

        Args:
            transcript: Video transcript text

        Returns:
            List of code snippet strings
        """
        code_snippets = []

        # C# code indicators
        code_keywords = [
            'class', 'public', 'private', 'protected',
            'void', 'int', 'string', 'bool', 'var',
            'namespace', 'using', 'static', 'async', 'await',
            'interface', 'abstract', 'override', 'virtual'
        ]

        # Split into sentences
        sentences = transcript.split('.')

        current_snippet = []
        in_code_block = False

        for sentence in sentences:
            sentence = sentence.strip()

            # Check if sentence contains C# keywords
            has_code = any(keyword in sentence.lower() for keyword in code_keywords)

            if has_code:
                in_code_block = True
                current_snippet.append(sentence)
            elif in_code_block and len(current_snippet) > 0:
                # End of code block
                if len(current_snippet) >= 2:  # At least 2 sentences
                    code_snippets.append('. '.join(current_snippet))
                current_snippet = []
                in_code_block = False

        # Add final snippet if exists
        if len(current_snippet) >= 2:
            code_snippets.append('. '.join(current_snippet))

        return code_snippets

    def upload_video_to_rag(
        self,
        video_path: Path,
        chapter_name: str,
        lecture_title: str
    ) -> int:
        """
        Upload video transcript to RAG.

        WHY: Makes video content searchable for RAG validation.

        Args:
            video_path: Path to video file
            chapter_name: Chapter name from directory structure
            lecture_title: Lecture title from filename

        Returns:
            Number of chunks uploaded
        """
        try:
            # Transcribe video
            transcript = self.transcribe_video(video_path)

            if not transcript:
                print(f"      ⚠️  Empty transcript, skipping")
                self.skipped_count += 1
                return 0

            # Extract code snippets
            code_snippets = self.extract_code_from_transcript(transcript)

            if not code_snippets:
                # No code found - upload full transcript
                code_snippets = [transcript]

            print(f"      📝 Found {len(code_snippets)} code snippets")

            # Upload each snippet to RAG
            chunks_uploaded = 0

            for idx, snippet in enumerate(code_snippets):
                # Create unique ID
                content_hash = hashlib.md5(snippet.encode()).hexdigest()[:8]
                artifact_id = f"csharp-course-{content_hash}-{idx}"

                # Store in RAG as code_example
                metadata = {
                    "type": "code_example",
                    "language": "csharp",
                    "source": f"Udemy C# Course - {chapter_name}",
                    "lecture": lecture_title,
                    "framework": "dotnet",
                    "video_file": video_path.name,
                    "snippet_index": idx,
                    "total_snippets": len(code_snippets)
                }

                self.rag.store_artifact(
                    artifact_id=artifact_id,
                    content=snippet,
                    artifact_type="code_example",
                    metadata=metadata
                )

                chunks_uploaded += 1

            self.uploaded_count += chunks_uploaded
            print(f"      ✅ Uploaded {chunks_uploaded} chunks")

            return chunks_uploaded

        except Exception as e:
            print(f"      ❌ Error uploading: {e}")
            self.error_count += 1
            return 0

    def scan_course_directory(self, course_root: Path) -> List[Dict]:
        """
        Scan course directory for video files.

        WHY: Organize videos by chapter and lecture for metadata.

        Args:
            course_root: Root directory of course

        Returns:
            List of video info dicts
        """
        videos = []

        # Find all .mp4 files
        for video_path in course_root.rglob("*.mp4"):
            # Extract chapter name from parent directory
            parent_dir = video_path.parent.name

            # Extract lecture title from filename
            lecture_title = video_path.stem

            videos.append({
                'path': video_path,
                'chapter': parent_dir,
                'title': lecture_title
            })

        return videos

    def upload_course(self, course_root: Path, max_videos: int = 10) -> int:
        """
        Upload entire course to RAG.

        WHY: Process all course videos.
        WHAT: Transcribes and uploads videos in batches.

        Args:
            course_root: Root directory of course
            max_videos: Maximum videos to process (for testing)

        Returns:
            Total chunks uploaded
        """
        print(f"\n{'='*70}")
        print(f"Scanning course directory: {course_root}")
        print(f"{'='*70}")

        videos = self.scan_course_directory(course_root)

        print(f"\n📹 Found {len(videos)} video lectures")
        print(f"   Processing first {min(max_videos, len(videos))} videos")

        total_chunks = 0

        for idx, video_info in enumerate(videos[:max_videos], 1):
            print(f"\n{'='*70}")
            print(f"📹 Video {idx}/{min(max_videos, len(videos))}")
            print(f"   Chapter: {video_info['chapter']}")
            print(f"   Title: {video_info['title']}")
            print(f"{'='*70}")

            chunks = self.upload_video_to_rag(
                video_path=video_info['path'],
                chapter_name=video_info['chapter'],
                lecture_title=video_info['title']
            )

            total_chunks += chunks

        return total_chunks


def main():
    """Main entry point"""

    print("\n" + "="*70)
    print("C# UDEMY COURSE → RAG DATABASE")
    print("="*70)

    uploader = CSharpCourseUploader()

    course_path = Path("/home/bbrelin/Downloads/Udemy - Learn C Sharp Coding Basics for Beginners C Sharp Fundamentals")

    if not course_path.exists():
        print(f"❌ Course directory not found: {course_path}")
        return 1

    try:
        # Upload first 10 videos as a test
        total_chunks = uploader.upload_course(
            course_root=course_path,
            max_videos=10  # Start with 10 videos
        )

        # Summary
        print("\n" + "="*70)
        print("UPLOAD SUMMARY")
        print("="*70)
        print(f"✅ Total chunks uploaded: {total_chunks}")
        print(f"⚠️  Videos skipped: {uploader.skipped_count}")
        print(f"❌ Errors: {uploader.error_count}")

        # RAG stats
        print("\n📊 RAG Database Stats:")
        stats = uploader.rag.get_stats()
        print(f"   Total artifacts: {stats['total_artifacts']}")
        print(f"   Code examples: {stats['by_type'].get('code_example', 0)}")
        print("="*70)

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
