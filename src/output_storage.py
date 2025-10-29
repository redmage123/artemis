from artemis_logger import get_logger
logger = get_logger('output_storage')
'\nBACKWARD COMPATIBILITY WRAPPER\n\nThis module maintains backward compatibility while the codebase migrates\nto the new modular structure in output_storage/.\n\nAll functionality has been refactored into:\n- output_storage/backends/base.py - StorageBackend ABC\n- output_storage/backends/local.py - LocalStorageBackend\n- output_storage/backends/s3.py - S3StorageBackend\n- output_storage/backends/gcs.py - GCSStorageBackend\n- output_storage/factory.py - Backend factory\n- output_storage/manager.py - OutputStorageManager\n- output_storage/singleton.py - Global instance\n\nTo migrate your code:\n    OLD: from output_storage import OutputStorageManager, get_storage\n    NEW: from output_storage import OutputStorageManager, get_storage  # Same import works!\n\nNo breaking changes - all imports remain identical.\n'
from output_storage import OutputStorageManager, get_storage
from output_storage.backends import StorageBackend, LocalStorageBackend, S3StorageBackend, GCSStorageBackend
__all__ = ['OutputStorageManager', 'get_storage', 'StorageBackend', 'LocalStorageBackend', 'S3StorageBackend', 'GCSStorageBackend']
if __name__ == '__main__':
    storage = OutputStorageManager()
    
    logger.log('Storage Info:', 'INFO')
    
    logger.log(storage.get_storage_info(), 'INFO')
    test_path = storage.write_adr('test-card-001', '001', '# Test ADR\n\nThis is a test ADR.')
    
    logger.log(f'\nWrote test file: {test_path}', 'INFO')
    content = storage.read_file('adrs/test-card-001/ADR-001.md')
    
    logger.log(f'\nRead content: {content[:50]}...', 'INFO')
    outputs = storage.list_card_outputs('test-card-001')
    
    logger.log(f'\nCard outputs: {outputs}', 'INFO')