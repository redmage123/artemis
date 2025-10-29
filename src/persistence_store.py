from artemis_logger import get_logger
logger = get_logger('persistence_store')
'\nPersistence Store - Backward Compatibility Wrapper\n\nWHY: Provides backward compatibility with original persistence_store.py.\n     Allows existing code to work without modification while using modular implementation.\n\nRESPONSIBILITY: Re-exports all components from modularized persistence package.\n                Maintains original API surface for seamless migration.\n\nPATTERNS:\n- Facade Pattern: Simplified interface to modular implementation\n- Proxy Pattern: Delegates to modular components\n- Open/Closed Principle: Original API preserved, implementation replaced\n\nMIGRATION PATH:\nOld: from persistence_store import PipelineState, SQLitePersistenceStore\nNew: from persistence import PipelineState, SQLitePersistenceStore\nBoth work identically - this wrapper ensures compatibility.\n\nOriginal file: 766 lines (monolithic)\nRefactored to: 9 focused modules in persistence/ package\nThis wrapper: Re-exports for compatibility\n'
from persistence import PipelineState, StageCheckpoint, PersistenceStoreInterface, SQLitePersistenceStore, JSONFilePersistenceStore, PersistenceStoreFactory, PersistenceQueryInterface, CheckpointManager, StateRestorationManager, serialize_pipeline_state, deserialize_pipeline_state, serialize_stage_checkpoint, deserialize_stage_checkpoint
__all__ = ['PipelineState', 'StageCheckpoint', 'PersistenceStoreInterface', 'SQLitePersistenceStore', 'JSONFilePersistenceStore', 'PersistenceStoreFactory', 'PersistenceQueryInterface', 'CheckpointManager', 'StateRestorationManager', 'serialize_pipeline_state', 'deserialize_pipeline_state', 'serialize_stage_checkpoint', 'deserialize_stage_checkpoint']
if __name__ == '__main__':
    'Example usage - identical to original implementation'
    from datetime import datetime
    
    logger.log('Persistence Store - Example Usage (Backward Compatible)', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    store = PersistenceStoreFactory.create('sqlite', db_path='/tmp/test_persistence.db')
    state = PipelineState(card_id='test-card-001', status='running', current_stage='development', stages_completed=['project_analysis', 'architecture'], stage_results={'architecture': {'adr': 'ADR-001.md'}}, developer_results=[], metrics={'stages_completed': 2}, created_at=datetime.utcnow().isoformat() + 'Z', updated_at=datetime.utcnow().isoformat() + 'Z')
    store.save_pipeline_state(state)
    
    logger.log(f'Saved pipeline state: {state.card_id}', 'INFO')
    checkpoint = StageCheckpoint(card_id='test-card-001', stage_name='architecture', status='completed', started_at=datetime.utcnow().isoformat() + 'Z', completed_at=datetime.utcnow().isoformat() + 'Z', result={'adr_file': 'ADR-001.md'})
    store.save_stage_checkpoint(checkpoint)
    
    logger.log(f'Saved stage checkpoint: {checkpoint.stage_name}', 'INFO')
    loaded_state = store.load_pipeline_state('test-card-001')
    
    logger.log(f'Loaded pipeline state: status={loaded_state.status}', 'INFO')
    resumable = store.get_resumable_pipelines()
    
    logger.log(f'Resumable pipelines: {resumable}', 'INFO')
    stats = store.get_statistics()
    
    logger.log(f'Database statistics:', 'INFO')
    
    logger.log(f"   Total pipelines: {stats['total_pipelines']}", 'INFO')
    
    logger.log(f"   By status: {stats['by_status']}", 'INFO')
    
    logger.log(f"   Total checkpoints: {stats['total_checkpoints']}", 'INFO')
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('Persistence store working correctly (modular implementation)!', 'INFO')