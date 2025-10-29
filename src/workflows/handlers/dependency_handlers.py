from artemis_logger import get_logger
logger = get_logger('dependency_handlers')
'\nDependency Management Workflow Handlers\n\nWHY:\nHandles package dependency issues including missing packages,\nversion conflicts, and import errors.\n\nRESPONSIBILITY:\n- Install missing dependencies\n- Resolve version conflicts\n- Fix import errors\n- Manage package installations\n\nPATTERNS:\n- Strategy Pattern: Different dependency resolution strategies\n- Guard Clauses: Validate package names before installation\n- Command Builder: Construct pip install commands dynamically\n\nINTEGRATION:\n- Extends: WorkflowHandler base class\n- Used by: WorkflowHandlerFactory for dependency actions\n- Executes: pip for package management\n'
import subprocess
from typing import Dict, Any, List
from workflows.handlers.base_handler import WorkflowHandler

class InstallMissingDependencyHandler(WorkflowHandler):
    """
    Install missing dependency

    WHY: Recover from missing package errors automatically
    RESPONSIBILITY: Install specified package using pip
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        package = context.get('package')
        if not package:
            return False
        try:
            subprocess.run(['pip', 'install', package], check=True, capture_output=True, timeout=300)
            
            logger.log(f'[Workflow] Installed dependency: {package}', 'INFO')
            return True
        except Exception as e:
            
            logger.log(f'[Workflow] Failed to install {package}: {e}', 'INFO')
            return False

class ResolveVersionConflictHandler(WorkflowHandler):
    """
    Resolve package version conflict

    WHY: Handle incompatible package versions automatically
    RESPONSIBILITY: Install specific version or upgrade to latest
    PATTERNS: Command builder for version-specific installation
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        package = context.get('package')
        version = context.get('version')
        return self._install_package_version(package, version)

    def _install_package_version(self, package: str, version: str) -> bool:
        try:
            install_cmd = self._build_install_command(package, version)
            subprocess.run(install_cmd, check=True, capture_output=True, timeout=300)
            
            logger.log(f'[Workflow] Resolved version conflict for {package}', 'INFO')
            return True
        except Exception as e:
            
            logger.log(f'[Workflow] Failed to resolve version conflict: {e}', 'INFO')
            return False

    def _build_install_command(self, package: str, version: str) -> List[str]:
        if version:
            return ['pip', 'install', f'{package}=={version}']
        return ['pip', 'install', '--upgrade', package]

class FixImportErrorHandler(WorkflowHandler):
    """
    Fix import error

    WHY: Resolve import errors by installing missing modules
    RESPONSIBILITY: Install module that failed to import
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        module_name = context.get('module')
        try:
            subprocess.run(['pip', 'install', module_name], check=True, capture_output=True, timeout=300)
            
            logger.log(f'[Workflow] Fixed import error for {module_name}', 'INFO')
            return True
        except Exception as e:
            
            logger.log(f'[Workflow] Failed to fix import error: {e}', 'INFO')
            return False