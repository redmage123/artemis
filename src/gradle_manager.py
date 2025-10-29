"""
WHY: Backward compatibility wrapper for modularized Gradle manager.

RESPONSIBILITY:
- Re-export all components from managers.build_managers.gradle
- Maintain existing import paths for legacy code
- Provide CLI interface for standalone usage
- Ensure zero breaking changes

PATTERNS:
- Transparent re-export pattern
- Backward compatibility layer
- CLI delegation
- Import forwarding

MIGRATION:
Old imports (still supported):
    from gradle_manager import GradleManager

New imports (preferred):
    from managers.build_managers.gradle import GradleManager

Both work identically - this file ensures backward compatibility.
"""
from managers.build_managers.gradle import GradleManager, GradleDSL, GradleDependency, GradlePlugin, GradleProjectInfo, GradleBuildResult, GradleWrapper, BuildFileParser, DependencyManager, ProjectAnalyzer, TaskExecutor
__all__ = ['GradleManager', 'GradleDSL', 'GradleDependency', 'GradlePlugin', 'GradleProjectInfo', 'GradleBuildResult', 'GradleWrapper', 'BuildFileParser', 'DependencyManager', 'ProjectAnalyzer', 'TaskExecutor']
if __name__ == '__main__':
    import argparse
    import logging
    from typing import Optional, Any

    def handle_info_command(gradle: GradleManager) -> None:
        """
        WHY: Display comprehensive project information.

        PATTERNS:
        - Guard clauses for optional fields
        - Formatted output with separators
        """
        info = gradle.get_project_info()
        
        logger.log(f"\n{'=' * 60}", 'INFO')
        
        logger.log(f'Gradle Project Information', 'INFO')
        
        logger.log(f"{'=' * 60}", 'INFO')
        
        logger.log(f'Name:         {info.name}', 'INFO')
        
        logger.log(f'Group:        {info.group}', 'INFO')
        
        logger.log(f'Version:      {info.version}', 'INFO')
        
        logger.log(f'DSL:          {info.dsl.value}', 'INFO')
        
        logger.log(f'Multi-project: {info.is_multi_project}', 'INFO')
        
        logger.log(f'Android:      {info.is_android}', 'INFO')
        if info.source_compatibility:
            
            logger.log(f'Java Source:  {info.source_compatibility}', 'INFO')
        if info.target_compatibility:
            
            logger.log(f'Java Target:  {info.target_compatibility}', 'INFO')
        if info.subprojects:
            
            logger.log(f"Subprojects:  {', '.join(info.subprojects)}", 'INFO')
        
        logger.log(f'Plugins:      {len(info.plugins)}', 'INFO')
        
        logger.log(f'Dependencies: {len(info.dependencies)}', 'INFO')
        
        logger.log(f'Tasks:        {len(info.tasks)}', 'INFO')
        
        logger.log(f"{'=' * 60}\n", 'INFO')

    def handle_build_command(gradle: GradleManager, args: Any) -> None:
        """
        WHY: Execute build and display results.

        PATTERNS:
        - Guard clause for test results
        - Error limiting
        """
        result = gradle.build(task=args.task, clean=not args.no_clean)
        
        logger.log(f"\n{'=' * 60}", 'INFO')
        
        logger.log(f"Build Result: {('SUCCESS' if result.success else 'FAILURE')}", 'INFO')
        
        logger.log(f"{'=' * 60}", 'INFO')
        
        logger.log(f'Task:      {result.task}', 'INFO')
        
        logger.log(f'Duration:  {result.duration:.2f}s', 'INFO')
        
        logger.log(f'Exit Code: {result.exit_code}', 'INFO')
        if result.tests_run > 0:
            
            logger.log(f'Tests:     {result.tests_passed}/{result.tests_run} passed', 'INFO')
        if result.errors:
            
            logger.log(f'\nErrors:', 'INFO')
            for error in result.errors[:5]:
                
                logger.log(f'  - {error}', 'INFO')
        
        logger.log(f"{'=' * 60}\n", 'INFO')

    def handle_test_command(gradle: GradleManager, args: Any) -> None:
        """
        WHY: Execute tests and display results.

        PATTERNS:
        - Structured output format
        """
        result = gradle.run_tests(test_class=args.test_class, test_method=args.test_method)
        
        logger.log(f"\n{'=' * 60}", 'INFO')
        
        logger.log(f"Test Result: {('SUCCESS' if result.success else 'FAILURE')}", 'INFO')
        
        logger.log(f"{'=' * 60}", 'INFO')
        
        logger.log(f'Tests Run:    {result.tests_run}', 'INFO')
        
        logger.log(f'Passed:       {result.tests_passed}', 'INFO')
        
        logger.log(f'Failed:       {result.tests_failed}', 'INFO')
        
        logger.log(f'Skipped:      {result.tests_skipped}', 'INFO')
        
        logger.log(f'Duration:     {result.duration:.2f}s', 'INFO')
        
        logger.log(f"{'=' * 60}\n", 'INFO')
    parser = argparse.ArgumentParser(description='Gradle Build System Manager')
    parser.add_argument('--project-dir', default='.', help='Gradle project directory')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    subparsers.add_parser('info', help='Show project information')
    build_parser = subparsers.add_parser('build', help='Build project')
    build_parser.add_argument('--task', default='build', help='Gradle task')
    build_parser.add_argument('--no-clean', action='store_true', help="Don't clean before build")
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--class', dest='test_class', help='Test class to run')
    test_parser.add_argument('--method', dest='test_method', help='Test method to run')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    gradle = GradleManager(project_dir=args.project_dir)
    command_handlers = {'info': lambda: handle_info_command(gradle), 'build': lambda: handle_build_command(gradle, args), 'test': lambda: handle_test_command(gradle, args)}
    handler = command_handlers.get(args.command)
    if handler:
        handler()
    else:
        parser.print_help()