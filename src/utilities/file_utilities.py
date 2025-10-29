from artemis_logger import get_logger
logger = get_logger('file_utilities')
'\nModule: utilities/file_utilities.py\n\nWHY: Provides convenience wrappers for file operations with safety checks.\n     Eliminates 58+ duplicate file operation patterns across the codebase,\n     ensuring consistent error handling and existence checks.\n\nRESPONSIBILITY:\n- Safely read JSON files with existence checks\n- Safely write JSON files with error handling\n- Safely read text files with existence checks\n- Ensure directories exist, create if needed\n- Provide default values for missing files\n- Log file operation errors consistently\n\nPATTERNS:\n- Adapter Pattern: Wraps FileManager with existence checks and error handling\n- Null Object Pattern: Returns default values instead of raising on missing files\n- Guard Clause Pattern: Check file exists before attempting read\n- Facade Pattern: Simplifies file operations by hiding Path/existence complexity\n\nBenefits:\n- Consistent file operation patterns across entire codebase\n- Eliminates duplicate existence checks\n- Provides sensible defaults for missing files\n- Single point to enhance file operations (caching, metrics, etc)\n\nIntegration: Used by all pipeline stages, agents, and orchestrator components\n             for consistent file I/O with error handling.\n'
from typing import Dict, Optional, Union
from pathlib import Path
from artemis_services import FileManager

class FileOperations:
    """
    Convenience wrappers for file operations

    WHY: Eliminates 58+ duplicate file operation patterns.
         Before this class, every file read/write had custom existence checks
         and error handling, leading to inconsistent behavior.

    RESPONSIBILITY:
    - Safely read/write JSON files
    - Safely read text files
    - Ensure directories exist
    - Provide default values for missing files
    """

    @staticmethod
    def safe_read_json(file_path: Union[str, Path], default: Optional[Dict]=None, verbose: bool=True) -> Optional[Dict]:
        """
        Safely read JSON file with existence check

        WHY: Common pattern - read JSON config/state file, use default if missing.
             Guard clause pattern prevents exceptions for missing files.

        Args:
            file_path: Path to JSON file
            default: Default value if file doesn't exist
            verbose: Whether to log messages

        Returns:
            JSON data or default
        """
        path = Path(file_path)
        if not path.exists():
            if verbose:
                
                logger.log(f'[FileOps] File not found: {file_path}', 'INFO')
            return default
        try:
            return FileManager.read_json(str(file_path))
        except Exception as e:
            if verbose:
                
                logger.log(f'[FileOps] Failed to read JSON from {file_path}: {e}', 'INFO')
            return default

    @staticmethod
    def safe_write_json(file_path: Union[str, Path], data: Dict, verbose: bool=True) -> bool:
        """
        Safely write JSON file with error handling

        WHY: Common pattern - write JSON, return bool success indicator
             instead of raising exceptions.

        Args:
            file_path: Path to write to
            data: Data to write
            verbose: Whether to log messages

        Returns:
            True if succeeded, False otherwise
        """
        try:
            FileManager.write_json(str(file_path), data)
            return True
        except Exception as e:
            if verbose:
                
                logger.log(f'[FileOps] Failed to write JSON to {file_path}: {e}', 'INFO')
            return False

    @staticmethod
    def safe_read_text(file_path: Union[str, Path], default: Optional[str]=None, verbose: bool=True) -> Optional[str]:
        """
        Safely read text file with existence check

        WHY: Common pattern - read text file, use default if missing.
             Guard clause pattern prevents exceptions for missing files.

        Args:
            file_path: Path to text file
            default: Default value if file doesn't exist
            verbose: Whether to log messages

        Returns:
            File contents or default
        """
        path = Path(file_path)
        if not path.exists():
            if verbose:
                
                logger.log(f'[FileOps] File not found: {file_path}', 'INFO')
            return default
        try:
            return FileManager.read_text(str(file_path))
        except Exception as e:
            if verbose:
                
                logger.log(f'[FileOps] Failed to read text from {file_path}: {e}', 'INFO')
            return default

    @staticmethod
    def ensure_directory(dir_path: Union[str, Path], verbose: bool=False) -> bool:
        """
        Ensure directory exists, create if needed

        WHY: Common pattern - create output directory before writing files.
             Idempotent operation (safe to call multiple times).

        Args:
            dir_path: Directory path
            verbose: Whether to log messages

        Returns:
            True if directory exists or was created
        """
        path = Path(dir_path)
        if path.exists():
            return True
        try:
            path.mkdir(parents=True, exist_ok=True)
            if verbose:
                
                logger.log(f'[FileOps] Created directory: {dir_path}', 'INFO')
            return True
        except Exception as e:
            if verbose:
                
                logger.log(f'[FileOps] Failed to create directory {dir_path}: {e}', 'INFO')
            return False