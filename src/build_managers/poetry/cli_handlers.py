from artemis_logger import get_logger
logger = get_logger('cli_handlers')
'\nPoetry Build Manager - CLI Command Handlers\n\nWHY: Isolate CLI interface logic from core business logic\nRESPONSIBILITY: Handle command-line argument processing and command dispatch\nPATTERNS: Dispatch Table, Single Responsibility, Guard Clauses\n\nThis module provides CLI command handlers for Poetry operations, enabling\ncommand-line usage of the Poetry manager.\n'
import sys
import json
from typing import Dict, Callable, Any

def handle_info_command(poetry: Any, args: Any) -> None:
    """
    Handle info command.

    WHY: Display project information in JSON format
    PATTERNS: Guard clause (implicit via method call)

    Args:
        poetry: PoetryManager instance
        args: Parsed command-line arguments
    """
    info = poetry.get_project_info()
    
    logger.log(json.dumps(info, indent=2), 'INFO')

def handle_build_command(poetry: Any, args: Any) -> None:
    """
    Handle build command.

    WHY: Execute package build with format selection
    PATTERNS: Guard clause - exit on failure

    Args:
        poetry: PoetryManager instance
        args: Parsed command-line arguments
    """
    result = poetry.build(format=args.format)
    
    logger.log(result, 'INFO')
    sys.exit(0 if result.success else 1)

def handle_test_command(poetry: Any, args: Any) -> None:
    """
    Handle test command.

    WHY: Run test suite with optional verbosity
    PATTERNS: Guard clause - exit on failure

    Args:
        poetry: PoetryManager instance
        args: Parsed command-line arguments
    """
    result = poetry.test(verbose=args.verbose)
    
    logger.log(result, 'INFO')
    sys.exit(0 if result.success else 1)

def handle_install_command(poetry: Any, args: Any) -> None:
    """
    Handle install command.

    WHY: Install all project dependencies
    PATTERNS: Guard clause - exit on failure

    Args:
        poetry: PoetryManager instance
        args: Parsed command-line arguments
    """
    result = poetry.install_dependencies()
    
    logger.log(result, 'INFO')
    sys.exit(0 if result.success else 1)

def handle_update_command(poetry: Any, args: Any) -> None:
    """
    Handle update command.

    WHY: Update dependencies to latest versions
    PATTERNS: Optional package parameter for targeted updates

    Args:
        poetry: PoetryManager instance
        args: Parsed command-line arguments
    """
    result = poetry.update_dependencies(package=args.package)
    
    logger.log(result, 'INFO')
    sys.exit(0 if result.success else 1)

def handle_add_command(poetry: Any, args: Any) -> None:
    """
    Handle add command.

    WHY: Add new dependency to project
    PATTERNS: Guard clause - require package name

    Args:
        poetry: PoetryManager instance
        args: Parsed command-line arguments
    """
    if not args.package:
        
        logger.log('Error: --package required for add command', 'INFO')
        sys.exit(1)
    poetry.install_dependency(args.package, version=args.version, group=args.group)
    
    logger.log(f'Added {args.package}', 'INFO')

def handle_show_command(poetry: Any, args: Any) -> None:
    """
    Handle show command.

    WHY: Display package information
    PATTERNS: Guard clause - require package name

    Args:
        poetry: PoetryManager instance
        args: Parsed command-line arguments
    """
    if not args.package:
        
        logger.log('Error: --package required for show command', 'INFO')
        sys.exit(1)
    result = poetry.show_package_info(args.package)
    
    logger.log(result.output, 'INFO')

def handle_run_command(poetry: Any, args: Any) -> None:
    """
    Handle run command.

    WHY: Execute custom script defined in pyproject.toml
    PATTERNS: Guard clause - require script name

    Args:
        poetry: PoetryManager instance
        args: Parsed command-line arguments
    """
    if not args.script:
        
        logger.log('Error: --script required for run command', 'INFO')
        sys.exit(1)
    result = poetry.run_script(args.script)
    
    logger.log(result, 'INFO')
    sys.exit(0 if result.success else 1)

def get_command_handlers() -> Dict[str, Callable]:
    """
    Get command handler dispatch table.

    WHY: Centralize command routing with dispatch table pattern
    PATTERNS: Dispatch table - maps command names to handlers
    RESPONSIBILITY: Provide command-to-handler mapping

    Returns:
        Dictionary mapping command names to handler functions

    Example:
        handlers = get_command_handlers()
        handler = handlers.get(command_name)
        handler(poetry, args)
    """
    return {'info': handle_info_command, 'build': handle_build_command, 'test': handle_test_command, 'install': handle_install_command, 'update': handle_update_command, 'add': handle_add_command, 'show': handle_show_command, 'run': handle_run_command}

def execute_cli_command(command: str, poetry: Any, args: Any) -> None:
    """
    Execute CLI command using dispatch table.

    WHY: Single entry point for all CLI command execution
    PATTERNS: Dispatch table pattern, guard clauses

    Args:
        command: Command name
        poetry: PoetryManager instance
        args: Parsed command-line arguments

    Raises:
        KeyError: If command not found in dispatch table
    """
    handlers = get_command_handlers()
    if command not in handlers:
        raise KeyError(f'Unknown command: {command}')
    handler = handlers[command]
    handler(poetry, args)
__all__ = ['handle_info_command', 'handle_build_command', 'handle_test_command', 'handle_install_command', 'handle_update_command', 'handle_add_command', 'handle_show_command', 'handle_run_command', 'get_command_handlers', 'execute_cli_command']