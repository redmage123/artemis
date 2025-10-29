from artemis_logger import get_logger
logger = get_logger('code_review_agent')
'\nBACKWARD COMPATIBILITY WRAPPER\n\nWHY: Maintain existing import paths during migration period\nRESPONSIBILITY: Re-export all components from code_review package\nPATTERNS: Facade pattern, deprecation notice\n\nOriginal: 1,006 lines (monolithic)\nRefactored: ~200 lines (orchestration + imports)\n\nNew structure:\n- code_review/agent.py: CodeReviewAgent class (main orchestrator)\n- code_review/strategies.py: Review strategies and prompt building\n- code_review/response_parser.py: LLM response parsing and extraction\n- code_review/report_generator.py: JSON and Markdown report generation\n- code_review/schema_normalizer.py: Schema normalization and scoring\n\nFor new code, prefer importing from code_review package:\n    from code_review import CodeReviewAgent\n    from code_review.strategies import build_base_review_prompt\n    from code_review.response_parser import parse_review_response\n    from code_review.report_generator import write_review_report\n    from code_review.schema_normalizer import normalize_review_schema\n'
from code_review import CodeReviewAgent, build_base_review_prompt, build_review_request_legacy, extract_file_types, enhance_messages_with_kg_context, read_review_prompt, try_load_rag_prompt, load_prompt_from_file, parse_review_response, extract_json_from_response, remove_code_block_markers, log_review_summary, write_review_report, write_review_summary, build_header_section, build_issues_summary_section, build_critical_issues_section, build_high_issues_section, build_positive_findings_section, build_recommendations_section, format_critical_issue, normalize_review_schema, collect_issues_from_categories, process_category_issues, calculate_overall_score, determine_overall_status
__all__ = ['CodeReviewAgent', 'build_base_review_prompt', 'build_review_request_legacy', 'extract_file_types', 'enhance_messages_with_kg_context', 'read_review_prompt', 'try_load_rag_prompt', 'load_prompt_from_file', 'parse_review_response', 'extract_json_from_response', 'remove_code_block_markers', 'log_review_summary', 'write_review_report', 'write_review_summary', 'build_header_section', 'build_issues_summary_section', 'build_critical_issues_section', 'build_high_issues_section', 'build_positive_findings_section', 'build_recommendations_section', 'format_critical_issue', 'normalize_review_schema', 'collect_issues_from_categories', 'process_category_issues', 'calculate_overall_score', 'determine_overall_status']

def main():
    """Test the code review agent."""
    import argparse
    parser = argparse.ArgumentParser(description='Code Review Agent')
    parser.add_argument('--developer', required=True, help='Developer name (e.g., developer-a)')
    parser.add_argument('--implementation-dir', required=True, help='Directory with implementation')
    parser.add_argument('--output-dir', required=True, help='Output directory for review report')
    parser.add_argument('--task-title', default='Test Task', help='Task title')
    parser.add_argument('--task-description', default='Test implementation', help='Task description')
    args = parser.parse_args()
    agent = CodeReviewAgent(developer_name=args.developer)
    result = agent.review_implementation(implementation_dir=args.implementation_dir, task_title=args.task_title, task_description=args.task_description, output_dir=args.output_dir)
    
    logger.log(f"\n{'=' * 80}", 'INFO')
    
    logger.log(f"Review Result: {result['review_status']}", 'INFO')
    
    logger.log(f"Overall Score: {result.get('overall_score', 0)}/100", 'INFO')
    
    logger.log(f"Total Issues: {result['total_issues']}", 'INFO')
    
    logger.log(f"  Critical: {result['critical_issues']}", 'INFO')
    
    logger.log(f"  High: {result['high_issues']}", 'INFO')
    
    logger.log(f"Report: {result.get('report_file', 'N/A')}", 'INFO')
    
    logger.log(f"{'=' * 80}\n", 'INFO')
if __name__ == '__main__':
    main()