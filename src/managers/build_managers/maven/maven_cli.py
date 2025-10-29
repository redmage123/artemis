"""
Module: Maven CLI Handler

WHY: Command-line interface for Maven operations (standalone tool).
RESPONSIBILITY: Parse CLI arguments and execute Maven commands.
PATTERNS: Command pattern (dispatch table), Facade pattern.

Dependencies: maven_manager, maven_enums
"""
import argparse
import logging
from typing import Any, Callable, Dict
from .maven_manager import MavenManager
from .maven_enums import MavenPhase

def handle_info_command(maven: MavenManager) -> None:
    """
    Handle 'info' command to display project information.

    WHY: Display comprehensive project metadata.
    RESPONSIBILITY: Query project info and format output.

    Args:
        maven: MavenManager instance
    """
    info = maven.get_project_info()
    
    logger.log(f"\n{'=' * 60}", 'INFO')
    
    logger.log(f'Maven Project Information', 'INFO')
    
    logger.log(f"{'=' * 60}", 'INFO')
    
    logger.log(f'Project:      {info}', 'INFO')
    
    logger.log(f'Name:         {info.name}', 'INFO')
    
    logger.log(f'Packaging:    {info.packaging}', 'INFO')
    if info.description:
        
        logger.log(f'Description:  {info.description}', 'INFO')
    
    logger.log(f'Multi-module: {info.is_multi_module}', 'INFO')
    if info.modules:
        
        logger.log(f"Modules:      {', '.join(info.modules)}", 'INFO')
    
    logger.log(f'Dependencies: {len(info.dependencies)}', 'INFO')
    
    logger.log(f'Plugins:      {len(info.plugins)}', 'INFO')
    
    logger.log(f"{'=' * 60}\n", 'INFO')

def handle_build_command(maven: MavenManager, args: Any) -> None:
    """
    Handle 'build' command to build the project.

    WHY: Execute build with user-specified configuration.
    RESPONSIBILITY: Parse args, execute build, display results.

    Args:
        maven: MavenManager instance
        args: Parsed command-line arguments
    """
    phase = MavenPhase(args.phase)
    result = maven.build(phase=phase, skip_tests=args.skip_tests, clean=not args.no_clean)
    
    logger.log(f"\n{'=' * 60}", 'INFO')
    
    logger.log(f"Build Result: {('SUCCESS' if result.success else 'FAILURE')}", 'INFO')
    
    logger.log(f"{'=' * 60}", 'INFO')
    
    logger.log(f'Phase:     {result.phase}', 'INFO')
    
    logger.log(f'Duration:  {result.duration:.2f}s', 'INFO')
    
    logger.log(f'Exit Code: {result.exit_code}', 'INFO')
    if not args.skip_tests:
        
        logger.log(f'Tests:     {result.tests_passed}/{result.tests_run} passed', 'INFO')
    if result.errors:
        
        logger.log(f'\nErrors:', 'INFO')
        for error in result.errors[:5]:
            
            logger.log(f'  - {error}', 'INFO')
    
    logger.log(f"{'=' * 60}\n", 'INFO')

def handle_test_command(maven: MavenManager, args: Any) -> None:
    """
    Handle 'test' command to run tests.

    WHY: Execute tests with optional filtering.
    RESPONSIBILITY: Parse args, run tests, display results.

    Args:
        maven: MavenManager instance
        args: Parsed command-line arguments
    """
    result = maven.run_tests(test_class=args.test_class, test_method=args.test_method)
    
    logger.log(f"\n{'=' * 60}", 'INFO')
    
    logger.log(f"Test Result: {('SUCCESS' if result.success else 'FAILURE')}", 'INFO')
    
    logger.log(f"{'=' * 60}", 'INFO')
    
    logger.log(f'Tests Run:    {result.tests_run}', 'INFO')
    
    logger.log(f'Passed:       {result.tests_passed}', 'INFO')
    
    logger.log(f'Failed:       {result.tests_failed}', 'INFO')
    
    logger.log(f'Skipped:      {result.tests_skipped}', 'INFO')
    
    logger.log(f'Duration:     {result.duration:.2f}s', 'INFO')
    
    logger.log(f"{'=' * 60}\n", 'INFO')

def handle_add_dep_command(maven: MavenManager, args: Any) -> None:
    """
    Handle 'add-dep' command to add a dependency.

    WHY: Programmatically add dependencies without manual XML editing.
    RESPONSIBILITY: Parse args, add dependency, display result.

    Args:
        maven: MavenManager instance
        args: Parsed command-line arguments
    """
    success = maven.add_dependency(args.group_id, args.artifact_id, args.version, args.scope)
    if success:
        
        logger.log(f'Added dependency: {args.group_id}:{args.artifact_id}:{args.version}', 'INFO')
    else:
        
        logger.log(f'Failed to add dependency', 'INFO')

def create_parser() -> argparse.ArgumentParser:
    """
    Create CLI argument parser.

    WHY: Centralized CLI definition.
    RESPONSIBILITY: Define all commands, subcommands, and arguments.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(description='Maven Build System Manager')
    parser.add_argument('--project-dir', default='.', help='Maven project directory')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    subparsers.add_parser('info', help='Show project information')
    build_parser = subparsers.add_parser('build', help='Build project')
    build_parser.add_argument('--phase', default='package', help='Maven phase')
    build_parser.add_argument('--skip-tests', action='store_true', help='Skip tests')
    build_parser.add_argument('--no-clean', action='store_true', help="Don't clean before build")
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--class', dest='test_class', help='Test class to run')
    test_parser.add_argument('--method', dest='test_method', help='Test method to run')
    dep_parser = subparsers.add_parser('add-dep', help='Add dependency')
    dep_parser.add_argument('group_id', help='Group ID')
    dep_parser.add_argument('artifact_id', help='Artifact ID')
    dep_parser.add_argument('version', help='Version')
    dep_parser.add_argument('--scope', default='compile', help='Dependency scope')
    return parser

def main() -> None:
    """
    Main CLI entry point.

    WHY: Execute CLI commands using dispatch table pattern.
    RESPONSIBILITY: Parse args, create manager, dispatch to handler.
    """
    parser = create_parser()
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    maven = MavenManager(project_dir=args.project_dir)
    command_handlers: Dict[str, Callable[[MavenManager, Any], None]] = {'info': lambda m, a: handle_info_command(m), 'build': handle_build_command, 'test': handle_test_command, 'add-dep': handle_add_dep_command}
    handler = command_handlers.get(args.command)
    if handler:
        if args.command == 'info':
            handler(maven, args)
        else:
            handler(maven, args)
    else:
        parser.print_help()
if __name__ == '__main__':
    main()