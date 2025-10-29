"""
WHY: Backward compatibility wrapper for BundlerManager.

RESPONSIBILITY:
- Re-export all components from modularized structure
- Maintain API compatibility with existing code
- Provide CLI interface for standalone usage

PATTERNS:
- Facade: Maintain simple import paths
- Backward Compatibility: Zero breaking changes
- Single Responsibility: Only re-exports

MIGRATION:
Clients should eventually migrate to:
    from managers.build.bundler import BundlerManager

But this wrapper ensures existing code continues to work:
    from bundler_manager import BundlerManager
"""
from managers.build.bundler.bundler_manager import BundlerManager
from managers.build.bundler.models import DependencyGroup, BundlerProjectInfo
from managers.build.bundler.gemfile_parser import GemfileParser
from managers.build.bundler.gem_operations import GemOperations
from managers.build.bundler.bundle_operations import BundleOperations
from managers.build.bundler.ruby_version_detector import RubyVersionDetector
from managers.build.bundler.test_stats_extractor import TestStatsExtractor
__all__ = ['BundlerManager', 'DependencyGroup', 'BundlerProjectInfo', 'GemfileParser', 'GemOperations', 'BundleOperations', 'RubyVersionDetector', 'TestStatsExtractor']
if __name__ == '__main__':
    import argparse
    import logging
    import sys
    import json
    from typing import Callable, Dict
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser(description='Bundler Manager')
    parser.add_argument('--project-dir', default='.', help='Project directory')
    parser.add_argument('command', choices=['info', 'install', 'test', 'update', 'add', 'exec', 'show', 'check', 'clean'], help='Command to execute')
    parser.add_argument('--gem', help='Gem name')
    parser.add_argument('--version', help='Gem version')
    parser.add_argument('--group', help='Dependency group')
    parser.add_argument('--deployment', action='store_true', help='Deployment mode')
    parser.add_argument('--without', help='Groups to exclude (comma-separated)')
    parser.add_argument('--exec-cmd', help='Command to execute with bundle exec')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    def handle_info_command(bundler: BundlerManager) -> None:
        """WHY: Display project information from Gemfile."""
        info = bundler.get_project_info()
        
        logger.log(json.dumps(info, indent=2), 'INFO')
        sys.exit(0)

    def handle_install_command(bundler: BundlerManager, args) -> None:
        """WHY: Install dependencies with optional exclusions."""
        without = args.without.split(',') if args.without else None
        result = bundler.install(deployment=args.deployment, without=without)
        
        logger.log(result, 'INFO')
        sys.exit(0 if result.success else 1)

    def handle_test_command(bundler: BundlerManager, args) -> None:
        """WHY: Execute tests and display results."""
        result = bundler.test(verbose=args.verbose)
        
        logger.log(result, 'INFO')
        sys.exit(0 if result.success else 1)

    def handle_update_command(bundler: BundlerManager, args) -> None:
        """WHY: Update dependencies to newer versions."""
        result = bundler.update(gem=args.gem)
        
        logger.log(result, 'INFO')
        sys.exit(0 if result.success else 1)

    def handle_add_command(bundler: BundlerManager, args) -> None:
        """WHY: Add new gem to Gemfile."""
        if not args.gem:
            
            logger.log('Error: --gem required for add command', 'INFO')
            sys.exit(1)
        bundler.install_dependency(args.gem, version=args.version, group=args.group)
        
        logger.log(f'Added {args.gem}', 'INFO')
        sys.exit(0)

    def handle_exec_command(bundler: BundlerManager, args) -> None:
        """WHY: Execute command in bundle context."""
        if not args.exec_cmd:
            
            logger.log('Error: --exec-cmd required for exec command', 'INFO')
            sys.exit(1)
        cmd = args.exec_cmd.split()
        result = bundler.exec(cmd)
        
        logger.log(result, 'INFO')
        sys.exit(0 if result.success else 1)

    def handle_show_command(bundler: BundlerManager, args) -> None:
        """WHY: Display gem information."""
        if not args.gem:
            
            logger.log('Error: --gem required for show command', 'INFO')
            sys.exit(1)
        result = bundler.show(args.gem)
        
        logger.log(result.output, 'INFO')
        sys.exit(0)

    def handle_check_command(bundler: BundlerManager) -> None:
        """WHY: Verify dependency satisfaction."""
        result = bundler.check()
        
        logger.log(result, 'INFO')
        sys.exit(0 if result.success else 1)

    def handle_clean_command(bundler: BundlerManager) -> None:
        """WHY: Remove unused gems."""
        result = bundler.clean()
        
        logger.log(result, 'INFO')
        sys.exit(0)
    COMMAND_HANDLERS: Dict[str, Callable] = {'info': lambda b, a: handle_info_command(b), 'install': handle_install_command, 'test': handle_test_command, 'update': handle_update_command, 'add': handle_add_command, 'exec': handle_exec_command, 'show': handle_show_command, 'check': lambda b, a: handle_check_command(b), 'clean': lambda b, a: handle_clean_command(b)}
    try:
        bundler = BundlerManager(project_dir=args.project_dir)
        handler = COMMAND_HANDLERS.get(args.command)
        if not handler:
            
            logger.log(f'Unknown command: {args.command}', 'INFO')
            sys.exit(1)
        handler(bundler, args)
    except Exception as e:
        logging.error(f'Error: {e}')
        sys.exit(1)