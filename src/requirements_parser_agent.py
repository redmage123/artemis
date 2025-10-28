#!/usr/bin/env python3
"""
Requirements Parser Agent - Backward Compatibility Wrapper

WHY: Maintain backward compatibility while using modularized package
RESPONSIBILITY: Re-export RequirementsParserAgent from requirements_parser package
PATTERNS: Facade pattern - thin wrapper around modularized implementation

MIGRATION: This is now a thin wrapper. The real implementation is in requirements_parser/

Original file: 1,120 lines
This wrapper: ~50 lines
Reduction: 95.5%

For new code, import directly from package:
    from requirements_parser import RequirementsParserAgent
"""

# Re-export main class from modularized package
from requirements_parser import RequirementsParserAgent

# Re-export internal components for advanced usage
from requirements_parser import (
    ExtractionEngine,
    RequirementsConverter,
    PromptManagerIntegration,
    AIServiceIntegration,
    KnowledgeGraphIntegration
)

__all__ = [
    "RequirementsParserAgent",
    "ExtractionEngine",
    "RequirementsConverter",
    "PromptManagerIntegration",
    "AIServiceIntegration",
    "KnowledgeGraphIntegration",
]


def main():
    """Example usage - CLI interface"""
    import argparse
    from requirements_models import StructuredRequirements

    parser = argparse.ArgumentParser(description="Parse free-form requirements into structured format")
    parser.add_argument("input_file", help="Path to requirements document")
    parser.add_argument("--output", "-o", help="Output file path (default: requirements.yaml)")
    parser.add_argument("--format", "-f", choices=["yaml", "json"], default="yaml", help="Output format")
    parser.add_argument("--project-name", "-p", help="Project name")
    parser.add_argument("--llm-provider", default="openai", help="LLM provider")
    parser.add_argument("--llm-model", help="LLM model")

    args = parser.parse_args()

    # Initialize parser
    parser_agent = RequirementsParserAgent(
        llm_provider=args.llm_provider,
        llm_model=args.llm_model,
        verbose=True
    )

    # Parse requirements
    structured_reqs = parser_agent.parse_requirements_file(
        input_file=args.input_file,
        project_name=args.project_name,
        output_format=args.format
    )

    # Save output
    output_file = args.output or f"requirements.{args.format}"
    if args.format == "yaml":
        structured_reqs.to_yaml(output_file)
    else:
        structured_reqs.to_json(output_file)

    print(f"\n✅ Requirements parsed and saved to: {output_file}")
    print(f"\n{structured_reqs.get_summary()}")


if __name__ == "__main__":
    main()
