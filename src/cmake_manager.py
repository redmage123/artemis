"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in build_managers/cmake/.

All functionality has been refactored into:
- build_managers/cmake/models.py - CMakeGenerator, BuildType, CMakeProjectInfo
- build_managers/cmake/validator.py - Installation/project validation
- build_managers/cmake/project_parser.py - CMakeLists.txt parsing
- build_managers/cmake/configurator.py - CMake configuration
- build_managers/cmake/builder.py - Build operations
- build_managers/cmake/test_runner.py - CTest operations
- build_managers/cmake/test_stats_parser.py - Test statistics
- build_managers/cmake/manager.py - CMakeManager orchestrator

To migrate your code:
    OLD: from cmake_manager import CMakeManager, CMakeGenerator, BuildType
    NEW: from build_managers.cmake import CMakeManager, CMakeGenerator, BuildType

No breaking changes - all imports remain identical.
"""
from build_managers.cmake import CMakeManager, CMakeGenerator, BuildType, CMakeProjectInfo
__all__ = ['CMakeManager', 'CMakeGenerator', 'BuildType', 'CMakeProjectInfo']
if __name__ == '__main__':
    import argparse
    import logging
    import sys
    import json
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser(description='CMake Manager')
    parser.add_argument('--project-dir', default='.', help='Project directory')
    parser.add_argument('--build-dir', help='Build directory')
    parser.add_argument('command', choices=['info', 'configure', 'build', 'test', 'clean'], help='Command to execute')
    parser.add_argument('--build-type', default='Release', help='Build type')
    parser.add_argument('--target', help='Build target')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    try:
        cmake = CMakeManager(project_dir=args.project_dir, build_dir=args.build_dir)
        if args.command == 'info':
            info = cmake.get_project_info()
            
            logger.log(json.dumps(info, indent=2), 'INFO')
            sys.exit(0)
        if args.command == 'configure':
            result = cmake.configure(build_type=args.build_type)
            
            logger.log(result, 'INFO')
            sys.exit(0 if result.success else 1)
        if args.command == 'build':
            result = cmake.build(target=args.target)
            
            logger.log(result, 'INFO')
            sys.exit(0 if result.success else 1)
        if args.command == 'test':
            result = cmake.test(verbose=args.verbose)
            
            logger.log(result, 'INFO')
            sys.exit(0 if result.success else 1)
        if args.command == 'clean':
            result = cmake.clean()
            
            logger.log(result, 'INFO')
            sys.exit(0)
    except Exception as e:
        logging.error(f'Error: {e}')
        sys.exit(1)