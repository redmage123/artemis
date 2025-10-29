from artemis_logger import get_logger
logger = get_logger('requirements_parser_agent')
'\nRequirements Parser Agent - Backward Compatibility Wrapper\n\nWHY: Maintain backward compatibility while using modularized package\nRESPONSIBILITY: Re-export RequirementsParserAgent from requirements_parser package\nPATTERNS: Facade pattern - thin wrapper around modularized implementation\n\nMIGRATION: This is now a thin wrapper. The real implementation is in requirements_parser/\n\nOriginal file: 1,120 lines\nThis wrapper: ~50 lines\nReduction: 95.5%\n\nFor new code, import directly from package:\n    from requirements_parser import RequirementsParserAgent\n'
from requirements_parser import RequirementsParserAgent
from requirements_parser import ExtractionEngine, RequirementsConverter, PromptManagerIntegration, AIServiceIntegration, KnowledgeGraphIntegration
__all__ = ['RequirementsParserAgent', 'ExtractionEngine', 'RequirementsConverter', 'PromptManagerIntegration', 'AIServiceIntegration', 'KnowledgeGraphIntegration']

def main():
    """Example usage - CLI interface"""
    import argparse
    from requirements_models import StructuredRequirements
    parser = argparse.ArgumentParser(description='Parse free-form requirements into structured format')
    parser.add_argument('input_file', help='Path to requirements document')
    parser.add_argument('--output', '-o', help='Output file path (default: requirements.yaml)')
    parser.add_argument('--format', '-f', choices=['yaml', 'json'], default='yaml', help='Output format')
    parser.add_argument('--project-name', '-p', help='Project name')
    parser.add_argument('--llm-provider', default='openai', help='LLM provider')
    parser.add_argument('--llm-model', help='LLM model')
    args = parser.parse_args()
    parser_agent = RequirementsParserAgent(llm_provider=args.llm_provider, llm_model=args.llm_model, verbose=True)
    structured_reqs = parser_agent.parse_requirements_file(input_file=args.input_file, project_name=args.project_name, output_format=args.format)
    output_file = args.output or f'requirements.{args.format}'
    if args.format == 'yaml':
        structured_reqs.to_yaml(output_file)
    else:
        structured_reqs.to_json(output_file)
    
    logger.log(f'\n✅ Requirements parsed and saved to: {output_file}', 'INFO')
    
    logger.log(f'\n{structured_reqs.get_summary()}', 'INFO')
if __name__ == '__main__':
    main()