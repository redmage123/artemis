#!/usr/bin/env python3
"""
Store Reference Implementation in RAG

WHY: Store high-quality reference implementations so future AI generations
     can learn from excellent examples.

RESPONSIBILITY:
- Read reference implementation
- Extract key features and patterns
- Store in RAG with rich metadata
- Enable example-driven development

USAGE:
    python store_reference_implementation.py /path/to/reference.html
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from rag_agent import RAGAgent
from artemis_logger import get_logger

logger = get_logger(__name__)


def extract_features(content: str, file_type: str) -> dict:
    """
    Extract features and patterns from reference implementation.

    Args:
        content: File content
        file_type: Type of file (html, css, js, python, etc.)

    Returns:
        Dictionary of extracted features
    """
    features = {
        'file_type': file_type,
        'lines_of_code': len(content.splitlines()),
        'has_inline_css': 'style>' in content if file_type == 'html' else False,
        'has_inline_js': 'script>' in content if file_type == 'html' else False,
        'uses_cdn': 'cdn.' in content.lower(),
        'frameworks': []
    }

    # Detect frameworks/libraries
    if 'chart.js' in content.lower():
        features['frameworks'].append('Chart.js')
    if 'react' in content.lower():
        features['frameworks'].append('React')
    if 'vue' in content.lower():
        features['frameworks'].append('Vue')
    if 'angular' in content.lower():
        features['frameworks'].append('Angular')

    # HTML-specific features
    if file_type == 'html':
        features['has_hero_section'] = 'hero' in content.lower()
        features['has_charts'] = 'chart' in content.lower() or 'canvas' in content
        features['has_grid_layout'] = 'grid' in content
        features['has_flexbox'] = 'flex' in content
        features['has_gradients'] = 'gradient' in content
        features['has_animations'] = 'transition' in content or 'animation' in content
        features['responsive'] = 'viewport' in content or '@media' in content
        features['self_contained'] = features['has_inline_css'] and features['has_inline_js']

    return features


def store_reference_implementation(
    file_path: str,
    category: str,
    quality_score: float,
    description: str,
    rag: RAGAgent
) -> str:
    """
    Store reference implementation in RAG.

    Args:
        file_path: Path to reference file
        category: Category (presentation, dashboard, api, etc.)
        quality_score: Quality score 0-10
        description: Human description of what makes this good
        rag: RAGAgent instance

    Returns:
        Artifact ID
    """
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract file info
    file_name = Path(file_path).name
    file_type = Path(file_path).suffix[1:]  # Remove leading dot

    # Extract features
    features = extract_features(content, file_type)

    # Create rich metadata
    metadata = {
        'category': category,
        'file_name': file_name,
        'file_type': file_type,
        'quality_score': quality_score,
        'description': description,
        'lines_of_code': features['lines_of_code'],
        'frameworks': ','.join(features['frameworks']),
        **{k: v for k, v in features.items() if k not in ['file_type', 'lines_of_code', 'frameworks']}
    }

    # Store in RAG
    artifact_id = rag.store_artifact(
        artifact_type='code_example',
        card_id='reference-implementation',
        task_title=f'Reference: {category} - {file_name}',
        content=content,
        metadata=metadata
    )

    logger.log(f"✅ Stored reference implementation: {artifact_id}", "INFO")
    logger.log(f"   Category: {category}", "INFO")
    logger.log(f"   Quality: {quality_score}/10", "INFO")
    logger.log(f"   Lines: {features['lines_of_code']}", "INFO")
    logger.log(f"   Features: {len([k for k, v in features.items() if v])}", "INFO")

    return artifact_id


def main():
    """Store manual HTML demo as reference implementation."""

    logger.log("=" * 70, "INFO")
    logger.log("STORING REFERENCE IMPLEMENTATION IN RAG", "INFO")
    logger.log("=" * 70, "INFO")
    logger.log("", "INFO")

    # Initialize RAG
    rag = RAGAgent(db_path='db')

    # Store manual HTML demo
    manual_demo_path = '/home/bbrelin/src/repos/artemis/.artemis_data/developer_output/demo/artemis_demo.html'

    if not os.path.exists(manual_demo_path):
        logger.log(f"❌ Reference file not found: {manual_demo_path}", "ERROR")
        sys.exit(1)

    logger.log(f"📂 Reading: {manual_demo_path}", "INFO")
    logger.log("", "INFO")

    description = """
    High-quality HTML presentation demo showcasing Artemis AI pipeline.

    STRENGTHS:
    - Self-contained (488 lines, single file)
    - 4 interactive Chart.js visualizations (line, radar, bar, doughnut)
    - Modern gradient design with animations
    - Responsive grid layouts
    - 8 pipeline stages with visual flow
    - 8 detailed feature cards
    - Statistics dashboard
    - Professional typography and spacing
    - Hero section with compelling copy
    - Hover effects and transitions

    USE THIS AS REFERENCE FOR:
    - Interactive presentations
    - Data visualizations
    - Marketing landing pages
    - Dashboard UIs
    - Single-page applications

    PATTERNS TO LEARN:
    - Self-contained design (inline CSS/JS)
    - Responsive grid layouts (auto-fit)
    - Chart.js integration
    - Visual hierarchy
    - Color consistency
    - Component-based structure (hero, stats, pipeline, charts, features)
    """

    artifact_id = store_reference_implementation(
        file_path=manual_demo_path,
        category='interactive_presentation',
        quality_score=9.2,
        description=description.strip(),
        rag=rag
    )

    logger.log("", "INFO")
    logger.log("=" * 70, "INFO")
    logger.log("✅ REFERENCE IMPLEMENTATION STORED", "INFO")
    logger.log("=" * 70, "INFO")
    logger.log("", "INFO")
    logger.log(f"Artifact ID: {artifact_id}", "INFO")
    logger.log("", "INFO")
    logger.log("Future generations can now query:", "INFO")
    logger.log('  - "Show me examples of interactive presentations"', "INFO")
    logger.log('  - "How to create Chart.js visualizations"', "INFO")
    logger.log('  - "Best practices for HTML presentations"', "INFO")
    logger.log("", "INFO")


if __name__ == '__main__':
    main()
