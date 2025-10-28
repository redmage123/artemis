#!/usr/bin/env python3
"""
HTML Generator

WHY: Generates HTML representation of SSD documents with embedded diagrams.
RESPONSIBILITY: Convert SSDDocument to HTML format with Mermaid.js support.
PATTERNS:
- Generator pattern (Pattern #11) for large content processing
- Single Responsibility
"""

from typing import Generator

from ssd_generation.models.ssd_document import SSDDocument


class HTMLGenerator:
    """
    Generates HTML representation with embedded Mermaid diagrams

    WHY: Produces browser-renderable HTML with interactive diagrams.
    WHEN: Called during output generation to create .html files.
    Uses Mermaid.js for rendering diagrams in the browser.
    """

    @staticmethod
    def generate_html(ssd_document: SSDDocument) -> str:
        """
        Generate HTML representation with embedded Mermaid diagrams

        Uses Mermaid.js for rendering diagrams in the browser
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSD: {ssd_document.project_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        .requirement {{
            background-color: #ecf0f1;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
        }}
        .priority-must_have {{
            border-left-color: #e74c3c;
        }}
        .priority-should_have {{
            border-left-color: #f39c12;
        }}
        .priority-nice_to_have {{
            border-left-color: #95a5a6;
        }}
        .diagram {{
            margin: 20px 0;
            padding: 20px;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
        }}
        .metadata {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        ul {{
            margin: 10px 0;
        }}
        .section {{
            margin: 30px 0;
        }}
    </style>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</head>
<body>
    <div class="container">
        <h1>Software Specification Document</h1>
        <h2>{ssd_document.project_name}</h2>

        <div class="metadata">
            <p><strong>Generated:</strong> {ssd_document.generated_at}</p>
            <p><strong>Card ID:</strong> {ssd_document.card_id}</p>
        </div>

        <div class="section">
            <h2>Executive Summary</h2>
            <p>{ssd_document.executive_summary}</p>
        </div>

        <div class="section">
            <h2>Business Case</h2>
            <p>{ssd_document.business_case}</p>
        </div>

        <div class="section">
            <h2>Functional Requirements</h2>
"""

        # Pattern #11: Generator for functional requirements HTML
        def _format_functional_req_html() -> Generator[str, None, None]:
            """Generator yielding HTML for functional requirements"""
            for req in ssd_document.functional_requirements:
                deps = f'<p><strong>Dependencies:</strong> {", ".join(req.dependencies)}</p>' if req.dependencies else ''
                yield f"""
            <div class="requirement priority-{req.priority}">
                <h3>{req.id}: {req.description}</h3>
                <p><strong>Priority:</strong> {req.priority.replace('_', ' ').title()}</p>
                <p><strong>Acceptance Criteria:</strong></p>
                <ul>
                    {''.join(f'<li>{criterion}</li>' for criterion in req.acceptance_criteria)}
                </ul>
                {deps}
            </div>
"""

        html += ''.join(_format_functional_req_html())

        html += """
        </div>

        <div class="section">
            <h2>Non-Functional Requirements</h2>
"""

        # Pattern #11: Generator for non-functional requirements HTML
        def _format_non_functional_req_html() -> Generator[str, None, None]:
            """Generator yielding HTML for non-functional requirements"""
            for req in ssd_document.non_functional_requirements:
                yield f"""
            <div class="requirement priority-{req.priority}">
                <h3>{req.id}: {req.description}</h3>
                <p><strong>Priority:</strong> {req.priority.replace('_', ' ').title()}</p>
                <p><strong>Acceptance Criteria:</strong></p>
                <ul>
                    {''.join(f'<li>{criterion}</li>' for criterion in req.acceptance_criteria)}
                </ul>
            </div>
"""

        html += ''.join(_format_non_functional_req_html())

        html += """
        </div>

        <div class="section">
            <h2>Business Requirements</h2>
"""

        # Pattern #11: Generator for business requirements HTML
        def _format_business_req_html() -> Generator[str, None, None]:
            """Generator yielding HTML for business requirements"""
            for req in ssd_document.business_requirements:
                yield f"""
            <div class="requirement priority-{req.priority}">
                <h3>{req.id}: {req.description}</h3>
                <p><strong>Priority:</strong> {req.priority.replace('_', ' ').title()}</p>
            </div>
"""

        html += ''.join(_format_business_req_html())

        html += """
        </div>

        <div class="section">
            <h2>Architecture & Design</h2>
"""

        # Pattern #11: Generator for diagrams HTML
        def _format_diagrams_html() -> Generator[str, None, None]:
            """Generator yielding HTML for diagrams"""
            for diagram in ssd_document.diagrams:
                mermaid_code = diagram.mermaid_syntax if diagram.mermaid_syntax else ""
                yield f"""
            <div class="diagram">
                <h3>{diagram.title}</h3>
                <p>{diagram.description}</p>
                <div class="mermaid">
{mermaid_code}
                </div>
            </div>
"""

        html += ''.join(_format_diagrams_html())

        html += f"""
        </div>

        <div class="section">
            <h2>Constraints</h2>
            <ul>
                {''.join(f'<li>{constraint}</li>' for constraint in ssd_document.constraints)}
            </ul>
        </div>

        <div class="section">
            <h2>Assumptions</h2>
            <ul>
                {''.join(f'<li>{assumption}</li>' for assumption in ssd_document.assumptions)}
            </ul>
        </div>

        <div class="section">
            <h2>Risks</h2>
            <ul>
                {''.join(f'<li>{risk}</li>' for risk in ssd_document.risks)}
            </ul>
        </div>

        <div class="section">
            <h2>Success Criteria</h2>
            <ul>
                {''.join(f'<li>{criterion}</li>' for criterion in ssd_document.success_criteria)}
            </ul>
        </div>
    </div>
</body>
</html>
"""

        return html
