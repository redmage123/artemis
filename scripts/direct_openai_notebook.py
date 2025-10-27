#!/usr/bin/env python3
"""
Direct OpenAI call - No Artemis orchestration.
Creates notebook demo directly with GPT-5.
"""

import json
import os
from openai import OpenAI

def create_notebook_direct():
    """Call GPT-5 directly to create Artemis demo notebook with proper context."""

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Load context from repo
    import glob

    # Read markdown files to understand Artemis
    md_files = glob.glob('/home/bbrelin/src/repos/artemis/*.md')
    artemis_docs = []
    for md_file in md_files[:5]:  # First 5 markdown files
        try:
            with open(md_file, 'r') as f:
                content = f.read()[:2000]  # First 2000 chars
                artemis_docs.append(f"## {md_file.split('/')[-1]}\n{content}")
        except:
            pass

    docs_context = "\n\n".join(artemis_docs)

    # Get example from RAG
    from rag_agent import RAGAgent
    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=False)

    rag_examples = rag.query_similar(
        query_text="high-quality jupyter notebook example demonstration",
        artifact_types=["notebook_example"],
        top_k=1
    )

    example_context = ""
    if rag_examples:
        example = rag_examples[0]
        metadata = example.get('metadata', {})
        example_context = f"""
**HIGH-QUALITY EXAMPLE FROM RAG:**

Quality Score: {metadata.get('quality_score', 'N/A')}
Total Cells: {metadata.get('total_cells', 'N/A')}
Features: {', '.join(metadata.get('features', [])[:5])}

{example.get('content', '')[:2000]}

KEY QUALITY INDICATORS:
- Use HTML/CSS/Chart.js for interactive visualizations
- Working imports only (no placeholders)
- 15+ cells minimum
- Rich narrative flow
- Professional structure
"""

    prompt = f"""I want to generate a Jupyter notebook that will create and run a slide demo on the Artemis project, which is in the current repo.

**CONTEXT FROM REPO DOCUMENTATION:**
{docs_context}

{example_context}

**YOUR TASK:**
Create a comprehensive Jupyter notebook demonstrating Artemis architecture and features.

**REQUIREMENTS:**
1. Use HTML, CSS, and Chart.js to create interactive charts and graphs
2. Describe what Artemis does and its architecture
3. Include these sections:
   - Introduction to Artemis
   - Core Architecture (Supervisor, Stages, Orchestrator)
   - Intelligent Router with advanced routing
   - Advanced Features (Thermodynamic, Dynamic Pipeline, Two-Pass)
   - Hybrid AI Approach for cost optimization
   - Live demos with working code
   - Performance metrics with Chart.js visualizations
   - Conclusion and Q&A

4. Technical Requirements:
   - 20+ cells (mix of markdown and code)
   - Use Chart.js for bar charts, line charts, pie charts
   - Use HTML/CSS for styling and layout
   - Include IPython.display for HTML rendering
   - NO placeholder imports (only real libraries)
   - Professional presentation quality

Return ONLY valid JSON in Jupyter notebook format (.ipynb). No markdown wrapper, just pure JSON."""

    print("📡 Calling GPT-5 directly...")

    response = client.chat.completions.create(
        model="gpt-4o",  # or gpt-5 if available
        messages=[
            {"role": "system", "content": "You are an expert Jupyter notebook creator. Return only valid .ipynb JSON format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=16000
    )

    content = response.choices[0].message.content

    # Try to extract JSON if wrapped in markdown
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    # Parse and save
    try:
        notebook = json.loads(content)

        output_path = "/home/bbrelin/src/repos/artemis/direct_openai_demo.ipynb"
        with open(output_path, 'w') as f:
            json.dump(notebook, f, indent=2)

        # Calculate stats
        cells = notebook.get('cells', [])
        code_cells = [c for c in cells if c.get('cell_type') == 'code']
        markdown_cells = [c for c in cells if c.get('cell_type') == 'markdown']

        print(f"\n✅ Direct GPT-5 notebook created!")
        print(f"   Output: {output_path}")
        print(f"   Total cells: {len(cells)}")
        print(f"   Code cells: {len(code_cells)}")
        print(f"   Markdown cells: {len(markdown_cells)}")
        print(f"   Size: {len(content)} bytes")
        print(f"   Tokens used: {response.usage.total_tokens}")

        return output_path

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        print(f"Response preview: {content[:500]}")
        return None

if __name__ == "__main__":
    print("="*70)
    print("Direct OpenAI Call - No Artemis Orchestration")
    print("="*70)
    print()

    output_path = create_notebook_direct()

    if output_path:
        print("\n✅ SUCCESS: Direct OpenAI notebook created")
        print(f"\nCompare with:")
        print(f"  - Claude's notebook: /home/bbrelin/src/repos/artemis/artemis_feature_demo_claude.ipynb")
        print(f"  - Artemis developer-a: .artemis_data/developer_output/developer-a/artemis_feature_demo.ipynb")
        print(f"  - Artemis developer-b: .artemis_data/developer_output/developer-b/artemis_feature_demo.ipynb")
    else:
        print("\n❌ FAILED: Could not create notebook")
