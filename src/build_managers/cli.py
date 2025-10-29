"""
Module: build_managers.cli

WHY: Command-line interface for build system detection and recommendation.
     Enables standalone usage of build system tools.

RESPONSIBILITY:
- Parse command-line arguments
- Execute detect and recommend commands
- Format output as JSON or human-readable text
- Provide CLI entry point for build system operations

PATTERNS:
- Command Pattern: Handler functions for each command
- Strategy Pattern: Different output formatters (JSON vs text)
- Facade: Simplified CLI over build system functionality

USAGE:
    # Detect build system
    python -m build_managers.cli detect --project-dir /path/to/project

    # Detect with JSON output
    python -m build_managers.cli detect --json

    # Recommend build system
    python -m build_managers.cli recommend --language python --type web_api

    # Recommend with JSON output
    python -m build_managers.cli recommend --language python --type web_api --json
"""
import argparse
import json
import logging
from typing import Any, Callable, Dict
from build_managers.models import BuildSystemDetection, BuildSystemRecommendation
from build_managers.universal import UniversalBuildSystem

def handle_detect_command(ubs: UniversalBuildSystem, args: Any) -> None:
    """
    Handle the detect command.

    WHY: Separates command handling logic from main CLI parsing.
    PATTERNS: Guard clause for JSON output (early return).

    Args:
        ubs: UniversalBuildSystem instance
        args: Parsed command-line arguments
    """
    detection = ubs.detect_build_system()
    if args.json:
        print_detection_json(detection)
        return
    print_detection_text(detection)

def handle_recommend_command(ubs: UniversalBuildSystem, args: Any) -> None:
    """
    Handle the recommend command.

    WHY: Separates command handling logic from main CLI parsing.
    PATTERNS: Guard clause for JSON output (early return).

    Args:
        ubs: UniversalBuildSystem instance
        args: Parsed command-line arguments
    """
    recommendation = ubs.recommend_build_system(language=args.language, project_type=args.type or 'unknown')
    if args.json:
        print_recommendation_json(recommendation)
        return
    print_recommendation_text(recommendation)

def print_detection_json(detection: BuildSystemDetection) -> None:
    """
    Print detection result as JSON.

    WHY: Enables machine-readable output for automation and integration.

    Args:
        detection: BuildSystemDetection result
    """
    result = {'build_system': detection.build_system.value, 'confidence': detection.confidence, 'evidence': detection.evidence, 'language': detection.language.value, 'project_type': detection.project_type.value}
    
    logger.log(json.dumps(result, indent=2), 'INFO')

def print_detection_text(detection: BuildSystemDetection) -> None:
    """
    Print detection result as formatted text.

    WHY: Provides human-readable output for interactive CLI usage.
    PATTERNS: Guard clause for empty evidence (early return).

    Args:
        detection: BuildSystemDetection result
    """
    
    logger.log(f"\n{'=' * 60}", 'INFO')
    
    logger.log(f'Build System Detection', 'INFO')
    
    logger.log(f"{'=' * 60}", 'INFO')
    
    logger.log(f'Build System:  {detection.build_system.value}', 'INFO')
    
    logger.log(f'Confidence:    {detection.confidence * 100:.0f}%', 'INFO')
    
    logger.log(f'Language:      {detection.language.value}', 'INFO')
    
    logger.log(f'Project Type:  {detection.project_type.value}', 'INFO')
    if not detection.evidence:
        
        logger.log(f"{'=' * 60}\n", 'INFO')
        return
    
    logger.log(f'Evidence:', 'INFO')
    for evidence in detection.evidence:
        
        logger.log(f'  - {evidence}', 'INFO')
    
    logger.log(f"{'=' * 60}\n", 'INFO')

def print_recommendation_json(recommendation: BuildSystemRecommendation) -> None:
    """
    Print recommendation result as JSON.

    WHY: Enables machine-readable output for automation and integration.

    Args:
        recommendation: BuildSystemRecommendation result
    """
    result = {'build_system': recommendation.build_system.value, 'rationale': recommendation.rationale, 'alternatives': [alt.value for alt in recommendation.alternatives], 'confidence': recommendation.confidence}
    
    logger.log(json.dumps(result, indent=2), 'INFO')

def print_recommendation_text(recommendation: BuildSystemRecommendation) -> None:
    """
    Print recommendation result as formatted text.

    WHY: Provides human-readable output for interactive CLI usage.
    PATTERNS: Guard clause for empty alternatives (early return).

    Args:
        recommendation: BuildSystemRecommendation result
    """
    
    logger.log(f"\n{'=' * 60}", 'INFO')
    
    logger.log(f'Build System Recommendation', 'INFO')
    
    logger.log(f"{'=' * 60}", 'INFO')
    
    logger.log(f'Recommended:  {recommendation.build_system.value}', 'INFO')
    
    logger.log(f'Rationale:    {recommendation.rationale}', 'INFO')
    
    logger.log(f'Confidence:   {recommendation.confidence * 100:.0f}%', 'INFO')
    if not recommendation.alternatives:
        
        logger.log(f"{'=' * 60}\n", 'INFO')
        return
    alts = ', '.join([alt.value for alt in recommendation.alternatives])
    
    logger.log(f'Alternatives: {alts}', 'INFO')
    
    logger.log(f"{'=' * 60}\n", 'INFO')

def main() -> None:
    """
    Main CLI entry point.

    WHY: Provides command-line interface for build system operations.
    PATTERNS: Strategy pattern for command dispatch.
    """
    parser = argparse.ArgumentParser(description='Universal Build System for Artemis', prog='python -m build_managers.cli')
    parser.add_argument('--project-dir', default='.', help='Project directory (default: current directory)')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    detect_parser = subparsers.add_parser('detect', help='Detect build system from project files')
    detect_parser.add_argument('--json', action='store_true', help='Output as JSON')
    recommend_parser = subparsers.add_parser('recommend', help='Recommend build system for new project')
    recommend_parser.add_argument('--language', required=True, help='Programming language (e.g., python, java, rust)')
    recommend_parser.add_argument('--type', help='Project type (e.g., web_api, cli_tool, library)')
    recommend_parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    ubs = UniversalBuildSystem(project_dir=args.project_dir)
    command_handlers: Dict[str, Callable] = {'detect': handle_detect_command, 'recommend': handle_recommend_command}
    handler = command_handlers.get(args.command)
    if not handler:
        parser.print_help()
        return
    handler(ubs, args)
if __name__ == '__main__':
    main()