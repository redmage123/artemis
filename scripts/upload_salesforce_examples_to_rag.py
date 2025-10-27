#!/usr/bin/env python3
"""
Upload Salesforce notebooks and HTML presentation files to RAG database.

This provides high-quality examples for developers to learn from.
"""

import json
from pathlib import Path
from rag_agent import RAGAgent


def analyze_notebook(notebook_path: Path) -> dict:
    """Analyze notebook and extract quality metrics."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cells = nb.get('cells', [])
    code_cells = [c for c in cells if c.get('cell_type') == 'code']
    markdown_cells = [c for c in cells if c.get('cell_type') == 'markdown']

    # Calculate metrics
    total_cells = len(cells)
    code_count = len(code_cells)
    markdown_count = len(markdown_cells)
    ratio = code_count / total_cells if total_cells > 0 else 0

    # Calculate total content
    total_chars = sum(len(''.join(c.get('source', []))) for c in cells)
    avg_cell_length = total_chars / total_cells if total_cells > 0 else 0

    # Check for visualizations
    has_matplotlib = any('matplotlib' in ''.join(c.get('source', [])) for c in code_cells)
    has_plotly = any('plotly' in ''.join(c.get('source', [])) for c in code_cells)
    has_seaborn = any('seaborn' in ''.join(c.get('source', [])) for c in code_cells)

    # Estimate quality score
    quality_score = 0.0
    if total_cells >= 20: quality_score += 0.3
    elif total_cells >= 15: quality_score += 0.2
    elif total_cells >= 10: quality_score += 0.1

    if 0.3 <= ratio <= 0.7: quality_score += 0.2
    if avg_cell_length > 300: quality_score += 0.2
    if has_matplotlib or has_plotly or has_seaborn: quality_score += 0.2
    if total_chars > 10000: quality_score += 0.1

    return {
        'total_cells': total_cells,
        'code_cells': code_count,
        'markdown_cells': markdown_count,
        'code_ratio': ratio,
        'total_chars': total_chars,
        'avg_cell_length': avg_cell_length,
        'has_matplotlib': has_matplotlib,
        'has_plotly': has_plotly,
        'has_seaborn': has_seaborn,
        'quality_score': min(1.0, quality_score),
        'file_size_kb': notebook_path.stat().st_size / 1024
    }


def analyze_html(html_path: Path) -> dict:
    """Analyze HTML presentation file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Basic metrics
    file_size_kb = html_path.stat().st_size / 1024
    has_chartjs = 'chart.js' in content.lower() or 'chartjs' in content.lower()
    has_d3 = 'd3.js' in content.lower() or 'd3.min.js' in content.lower()
    has_reveal = 'reveal.js' in content.lower()

    # Count slides (rough estimate)
    slide_count = content.count('<section') + content.count('class="slide"')

    quality_score = 0.5  # Base score for HTML presentations
    if file_size_kb > 30: quality_score += 0.2  # Substantial content
    if has_chartjs or has_d3: quality_score += 0.2  # Interactive visualizations
    if slide_count >= 10: quality_score += 0.1

    return {
        'file_size_kb': file_size_kb,
        'has_chartjs': has_chartjs,
        'has_d3': has_d3,
        'has_reveal': has_reveal,
        'estimated_slides': slide_count,
        'quality_score': min(1.0, quality_score),
        'content_length': len(content)
    }


def upload_notebooks_to_rag():
    """Upload Salesforce notebooks to RAG database."""
    print("="*70)
    print("Uploading Salesforce Notebooks to RAG Database")
    print("="*70)
    print()

    # Initialize RAG
    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=True)

    # Find all notebooks
    notebooks_dir = Path('/home/bbrelin/src/repos/salesforce/src')
    notebooks = list(notebooks_dir.glob('*.ipynb'))

    # Filter out backup and untitled
    notebooks = [nb for nb in notebooks if 'backup' not in nb.name.lower() and 'untitled' not in nb.name.lower()]

    print(f"Found {len(notebooks)} notebooks to upload\n")

    uploaded_count = 0
    for nb_path in notebooks:
        print(f"📓 Processing: {nb_path.name}")

        try:
            # Analyze notebook
            metrics = analyze_notebook(nb_path)

            # Load full notebook for content
            with open(nb_path, 'r', encoding='utf-8') as f:
                nb_data = json.load(f)

            cells = nb_data.get('cells', [])

            # Create content summary (first 5 cells as sample)
            sample_cells = cells[:5]
            content_summary = f"""# Salesforce AI Notebook: {nb_path.stem.replace('_', ' ').title()}

## Quality Metrics
- Total Cells: {metrics['total_cells']}
- Code Cells: {metrics['code_cells']}
- Markdown Cells: {metrics['markdown_cells']}
- Code/Total Ratio: {metrics['code_ratio']:.2f}
- Average Cell Length: {metrics['avg_cell_length']:.0f} characters
- Total Content: {metrics['total_chars']:,} characters
- Quality Score: {metrics['quality_score']:.2f}

## Features
- Matplotlib: {"Yes" if metrics['has_matplotlib'] else "No"}
- Plotly: {"Yes" if metrics['has_plotly'] else "No"}
- Seaborn: {"Yes" if metrics['has_seaborn'] else "No"}

## Sample Cells (First 5)

{json.dumps(sample_cells, indent=2)[:2000]}

## Use Case
This notebook demonstrates production-quality Salesforce AI integrations with:
- Professional structure and flow
- Working code examples
- Real-world use cases
- Best practices for AI integration
"""

            # Prepare metadata
            metadata = {
                'source': 'salesforce_repo',
                'filename': nb_path.name,
                'quality_score': metrics['quality_score'],
                'total_cells': metrics['total_cells'],
                'code_cells': metrics['code_cells'],
                'markdown_cells': metrics['markdown_cells'],
                'code_ratio': metrics['code_ratio'],
                'total_chars': metrics['total_chars'],
                'avg_cell_length': metrics['avg_cell_length'],
                'file_size_kb': metrics['file_size_kb'],
                'features': [
                    'salesforce_integration',
                    'ai_powered',
                    'production_quality'
                ]
            }

            if metrics['has_matplotlib']:
                metadata['features'].append('matplotlib_visualizations')
            if metrics['has_plotly']:
                metadata['features'].append('plotly_visualizations')
            if metrics['has_seaborn']:
                metadata['features'].append('seaborn_visualizations')

            # Store in RAG
            artifact_id = rag.store_artifact(
                artifact_type="notebook_example",
                card_id=f"salesforce-notebook-{nb_path.stem}",
                task_title=f"Salesforce AI: {nb_path.stem.replace('_', ' ').title()}",
                content=content_summary,
                metadata=metadata
            )

            if artifact_id:
                print(f"   ✅ Uploaded (Quality: {metrics['quality_score']:.2f}, Cells: {metrics['total_cells']})")
                uploaded_count += 1
            else:
                print(f"   ❌ Failed to upload")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

    return uploaded_count


def upload_html_to_rag():
    """Upload HTML presentation files to RAG database."""
    print("="*70)
    print("Uploading HTML Presentation Files to RAG Database")
    print("="*70)
    print()

    # Initialize RAG
    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=True)

    # Find all HTML files
    slides_dir = Path('/home/bbrelin/src/repos/salesforce/slides')
    html_files = list(slides_dir.glob('*.html'))

    print(f"Found {len(html_files)} HTML files to upload\n")

    uploaded_count = 0
    for html_path in html_files:
        print(f"🎨 Processing: {html_path.name}")

        try:
            # Analyze HTML
            metrics = analyze_html(html_path)

            # Load content (first 3000 chars)
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()

            content_summary = f"""# HTML Presentation: {html_path.stem.replace('_', ' ').title()}

## Quality Metrics
- File Size: {metrics['file_size_kb']:.1f} KB
- Estimated Slides: {metrics['estimated_slides']}
- Quality Score: {metrics['quality_score']:.2f}

## Features
- Chart.js: {"Yes" if metrics['has_chartjs'] else "No"}
- D3.js: {"Yes" if metrics['has_d3'] else "No"}
- Reveal.js: {"Yes" if metrics['has_reveal'] else "No"}

## Content Preview (First 3000 chars)

{content[:3000]}

## Use Case
This HTML presentation demonstrates:
- Professional slide design
- Interactive visualizations
- Presentation best practices
- HTML/CSS/JavaScript integration
"""

            # Prepare metadata
            metadata = {
                'source': 'salesforce_repo',
                'filename': html_path.name,
                'type': 'html_presentation',
                'quality_score': metrics['quality_score'],
                'file_size_kb': metrics['file_size_kb'],
                'estimated_slides': metrics['estimated_slides'],
                'has_chartjs': metrics['has_chartjs'],
                'has_d3': metrics['has_d3'],
                'has_reveal': metrics['has_reveal'],
                'features': [
                    'html_presentation',
                    'interactive',
                    'professional_design'
                ]
            }

            if metrics['has_chartjs']:
                metadata['features'].append('chartjs_visualizations')
            if metrics['has_d3']:
                metadata['features'].append('d3_visualizations')
            if metrics['has_reveal']:
                metadata['features'].append('reveal_js')

            # Store in RAG (use code_example type since presentation_example doesn't exist)
            artifact_id = rag.store_artifact(
                artifact_type="code_example",
                card_id=f"salesforce-slides-{html_path.stem}",
                task_title=f"HTML Presentation: {html_path.stem.replace('_', ' ').title()}",
                content=content_summary,
                metadata=metadata
            )

            if artifact_id:
                print(f"   ✅ Uploaded (Quality: {metrics['quality_score']:.2f}, Slides: {metrics['estimated_slides']})")
                uploaded_count += 1
            else:
                print(f"   ❌ Failed to upload")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

    return uploaded_count


def main():
    """Main execution."""
    print("\n" + "="*70)
    print("SALESFORCE EXAMPLES → RAG DATABASE UPLOAD")
    print("="*70)
    print()

    # Upload notebooks
    notebooks_uploaded = upload_notebooks_to_rag()

    # Upload HTML presentations
    html_uploaded = upload_html_to_rag()

    # Summary
    print("="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    print(f"✅ Notebooks uploaded: {notebooks_uploaded}")
    print(f"✅ HTML presentations uploaded: {html_uploaded}")
    print(f"✅ Total examples added: {notebooks_uploaded + html_uploaded}")
    print()

    # Verify RAG stats
    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=False)
    stats = rag.get_stats()
    print("📊 RAG Database Stats:")
    print(f"   Total artifacts: {stats['total_artifacts']}")
    print(f"   Notebook examples: {stats['by_type'].get('notebook_example', 0)}")
    print(f"   Code examples (includes HTML): {stats['by_type'].get('code_example', 0)}")
    print("="*70)


if __name__ == "__main__":
    main()
