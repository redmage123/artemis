#!/usr/bin/env python3
"""
Test script for Adaptive Pipeline System

WHY: Validate that the adaptive pipeline correctly detects task complexity
     and builds appropriate pipelines (FAST/MEDIUM/FULL).

USAGE:
    # Test with auto-detection
    python3 test_adaptive_pipeline.py --requirements-file /tmp/artemis_html_demo_requirements.txt

    # Force a specific path
    python3 test_adaptive_pipeline.py --requirements-file /tmp/artemis_html_demo_requirements.txt --force-path fast

    # Compare all paths
    python3 test_adaptive_pipeline.py --requirements-file /tmp/artemis_html_demo_requirements.txt --compare-all

PATTERNS:
- Command-line interface for testing
- Time measurement and comparison
- Quality validation
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from adaptive_pipeline_builder import (
    AdaptivePipelineBuilder,
    PipelinePath,
    TaskComplexity,
    detect_and_recommend_pipeline,
)
from artemis_logger import get_logger
from requirements_parser.parser_agent import RequirementsParserAgent

logger = get_logger(__name__)


def parse_requirements_file(file_path: str) -> Dict:
    """
    Parse requirements from a text file.

    Args:
        file_path: Path to requirements file

    Returns:
        Parsed requirements dict
    """
    logger.log(f"📄 Parsing requirements from: {file_path}", "INFO")

    # Use requirements parser
    parser = RequirementsParserAgent()
    structured_reqs = parser.parse_requirements_file(file_path)

    # Convert StructuredRequirements to dict for adaptive builder
    requirements = {
        'functional': structured_reqs.functional_requirements,
        'non_functional': structured_reqs.non_functional_requirements,
    }

    logger.log(f"✅ Parsed {len(requirements.get('functional', []))} functional requirements", "INFO")
    logger.log(f"✅ Parsed {len(requirements.get('non_functional', []))} non-functional requirements", "INFO")

    return requirements


def create_test_card(title: str = "HTML Presentation Demo") -> Dict:
    """
    Create a test task card.

    Args:
        title: Task title

    Returns:
        Task card dict
    """
    return {
        'title': title,
        'description': 'Create a professional HTML presentation to showcase Artemis AI pipeline',
        'priority': 'high',
        'task_type': 'feature',
    }


def test_pipeline_detection(requirements: Dict, card: Dict, force_path: Optional[str] = None):
    """
    Test the pipeline detection and recommendation.

    Args:
        requirements: Parsed requirements
        card: Task card
        force_path: Optional forced path (fast/medium/full)
    """
    logger.log("\n" + "=" * 80, "INFO")
    logger.log("🧪 TESTING PIPELINE DETECTION", "INFO")
    logger.log("=" * 80 + "\n", "INFO")

    builder = AdaptivePipelineBuilder()

    # Build pipeline
    if force_path:
        path_map = {
            'fast': PipelinePath.FAST,
            'medium': PipelinePath.MEDIUM,
            'full': PipelinePath.FULL,
        }
        forced = path_map.get(force_path.lower())
        if not forced:
            logger.log(f"❌ Invalid path: {force_path}", "ERROR")
            sys.exit(1)

        logger.log(f"⚙️  FORCING pipeline path: {force_path.upper()}", "INFO")
        pipeline_config = builder.build_pipeline(requirements, card, force_path=forced)
    else:
        logger.log("🔍 AUTO-DETECTING optimal pipeline path...", "INFO")
        pipeline_config = detect_and_recommend_pipeline(requirements, card)

    # Display results
    logger.log("\n" + "-" * 80, "INFO")
    logger.log("📊 PIPELINE CONFIGURATION", "INFO")
    logger.log("-" * 80, "INFO")
    logger.log(f"   Path: {pipeline_config['path'].upper()}", "INFO")
    logger.log(f"   Complexity: {pipeline_config['complexity']}", "INFO")
    logger.log(f"   Estimated Duration: {pipeline_config['estimated_duration_minutes']} minutes", "INFO")
    logger.log(f"   Parallel Developers: {pipeline_config['parallel_developers']}", "INFO")
    logger.log(f"   Validation Level: {pipeline_config['validation_level']}", "INFO")
    logger.log(f"\n   Stages ({len(pipeline_config['stages'])}):", "INFO")
    for i, stage in enumerate(pipeline_config['stages'], 1):
        logger.log(f"      {i}. {stage}", "INFO")

    logger.log(f"\n   Skip Flags:", "INFO")
    skip_flags = [k for k, v in pipeline_config.items() if k.startswith('skip_') and v]
    if skip_flags:
        for flag in skip_flags:
            logger.log(f"      ✓ {flag}", "INFO")
    else:
        logger.log(f"      (none - running all stages)", "INFO")

    logger.log(f"\n   Reasoning: {pipeline_config['reasoning']}", "INFO")
    logger.log("-" * 80 + "\n", "INFO")

    return pipeline_config


def run_pipeline_simulation(pipeline_config: Dict) -> Dict:
    """
    Simulate running the pipeline and measure time.

    Args:
        pipeline_config: Pipeline configuration

    Returns:
        Execution results
    """
    logger.log("🚀 SIMULATING PIPELINE EXECUTION", "INFO")

    start_time = time.time()

    # Simulate stage execution times
    stage_times = {
        'requirements_parsing': 2,
        'sprint_planning': 15,
        'ssd_generation': 8,
        'project_analysis': 10,
        'architecture': 8,
        'project_review': 8,
        'research': 2,
        'dependencies': 3,
        'development': 20 if pipeline_config['parallel_developers'] == 1 else 30,
        'arbitration': 10,
        'code_review': 8,
        'uiux': 12,
        'validation': 5,
        'integration': 8,
        'testing': 10,
    }

    total_simulated_time = 0
    for stage in pipeline_config['stages']:
        stage_time = stage_times.get(stage, 5)
        total_simulated_time += stage_time
        logger.log(f"   ✓ {stage} ({stage_time} min)", "INFO")

    end_time = time.time()
    actual_detection_time = end_time - start_time

    logger.log(f"\n✅ Simulation complete", "INFO")
    logger.log(f"   Simulated execution time: {total_simulated_time} minutes", "INFO")
    logger.log(f"   Estimated from config: {pipeline_config['estimated_duration_minutes']} minutes", "INFO")
    logger.log(f"   Detection overhead: {actual_detection_time:.2f} seconds\n", "INFO")

    return {
        'simulated_time_minutes': total_simulated_time,
        'estimated_time_minutes': pipeline_config['estimated_duration_minutes'],
        'detection_time_seconds': actual_detection_time,
    }


def compare_all_paths(requirements: Dict, card: Dict):
    """
    Compare all three pipeline paths for the same task.

    Args:
        requirements: Parsed requirements
        card: Task card
    """
    logger.log("\n" + "=" * 80, "INFO")
    logger.log("🔬 COMPARING ALL PIPELINE PATHS", "INFO")
    logger.log("=" * 80 + "\n", "INFO")

    paths = ['fast', 'medium', 'full']
    results = {}

    for path in paths:
        logger.log(f"\n{'─' * 80}", "INFO")
        logger.log(f"Testing {path.upper()} path...", "INFO")
        logger.log(f"{'─' * 80}\n", "INFO")

        pipeline_config = test_pipeline_detection(requirements, card, force_path=path)
        execution_result = run_pipeline_simulation(pipeline_config)

        results[path] = {
            'config': pipeline_config,
            'execution': execution_result,
        }

    # Display comparison table
    logger.log("\n" + "=" * 80, "INFO")
    logger.log("📊 COMPARISON SUMMARY", "INFO")
    logger.log("=" * 80 + "\n", "INFO")

    logger.log(f"{'Path':<15} {'Stages':<10} {'Estimated':<15} {'Simulated':<15} {'Speedup'}", "INFO")
    logger.log(f"{'-' * 15} {'-' * 10} {'-' * 15} {'-' * 15} {'-' * 10}", "INFO")

    full_time = results['full']['execution']['simulated_time_minutes']

    for path in paths:
        config = results[path]['config']
        exec_result = results[path]['execution']

        stages = len(config['stages'])
        estimated = config['estimated_duration_minutes']
        simulated = exec_result['simulated_time_minutes']
        speedup = full_time / simulated

        logger.log(
            f"{path.upper():<15} {stages:<10} {estimated:<15} {simulated:<15} {speedup:.1f}x",
            "INFO"
        )

    # Recommendations
    logger.log("\n" + "=" * 80, "INFO")
    logger.log("💡 RECOMMENDATIONS", "INFO")
    logger.log("=" * 80 + "\n", "INFO")

    auto_config = detect_and_recommend_pipeline(requirements, card)
    recommended_path = auto_config['path']

    logger.log(f"✅ For this task, AUTO-DETECTION recommends: {recommended_path.upper()}", "INFO")
    logger.log(f"   Reasoning: {auto_config['reasoning']}", "INFO")

    fast_time = results['fast']['execution']['simulated_time_minutes']
    recommended_time = results[recommended_path]['execution']['simulated_time_minutes']
    time_savings = full_time - recommended_time
    savings_percent = (time_savings / full_time) * 100

    logger.log(f"\n📈 Time Savings:", "INFO")
    logger.log(f"   Full pipeline: {full_time} minutes", "INFO")
    logger.log(f"   {recommended_path.upper()} pipeline: {recommended_time} minutes", "INFO")
    logger.log(f"   Savings: {time_savings} minutes ({savings_percent:.1f}%)", "INFO")

    if recommended_path == 'fast':
        logger.log(f"\n🎯 This task is perfect for the FAST path!", "INFO")
        logger.log(f"   It's a simple task that doesn't need the full enterprise pipeline.", "INFO")
    elif recommended_path == 'medium':
        logger.log(f"\n⚖️  This task needs the MEDIUM path for quality.", "INFO")
        logger.log(f"   It has some complexity that requires additional stages.", "INFO")
    else:
        logger.log(f"\n🏗️  This task requires the FULL path for quality.", "INFO")
        logger.log(f"   It's complex and needs all stages for best results.", "INFO")

    logger.log("\n" + "=" * 80 + "\n", "INFO")


def save_results(results: Dict, output_file: str):
    """
    Save test results to JSON file.

    Args:
        results: Test results
        output_file: Output file path
    """
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    logger.log(f"💾 Results saved to: {output_file}", "INFO")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test Adaptive Pipeline System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect optimal pipeline
  %(prog)s --requirements-file /tmp/artemis_html_demo_requirements.txt

  # Force FAST path
  %(prog)s --requirements-file /tmp/artemis_html_demo_requirements.txt --force-path fast

  # Compare all paths
  %(prog)s --requirements-file /tmp/artemis_html_demo_requirements.txt --compare-all

  # Save results to file
  %(prog)s --requirements-file /tmp/artemis_html_demo_requirements.txt --compare-all --output results.json
        """
    )

    parser.add_argument(
        '--requirements-file',
        required=True,
        help='Path to requirements text file'
    )
    parser.add_argument(
        '--force-path',
        choices=['fast', 'medium', 'full'],
        help='Force a specific pipeline path'
    )
    parser.add_argument(
        '--compare-all',
        action='store_true',
        help='Compare all three pipeline paths'
    )
    parser.add_argument(
        '--output',
        help='Save results to JSON file'
    )
    parser.add_argument(
        '--title',
        default='HTML Presentation Demo',
        help='Task title (default: HTML Presentation Demo)'
    )

    args = parser.parse_args()

    # Validate requirements file
    if not Path(args.requirements_file).exists():
        logger.log(f"❌ Requirements file not found: {args.requirements_file}", "ERROR")
        sys.exit(1)

    try:
        # Parse requirements
        requirements = parse_requirements_file(args.requirements_file)

        # Create test card
        card = create_test_card(args.title)

        # Run tests
        if args.compare_all:
            compare_all_paths(requirements, card)
        else:
            pipeline_config = test_pipeline_detection(requirements, card, args.force_path)
            execution_result = run_pipeline_simulation(pipeline_config)

            # Save results if requested
            if args.output:
                results = {
                    'pipeline_config': pipeline_config,
                    'execution_result': execution_result,
                    'requirements_file': args.requirements_file,
                    'task_title': args.title,
                }
                save_results(results, args.output)

        logger.log("✅ Test completed successfully!", "INFO")

    except Exception as e:
        logger.log(f"❌ Test failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
