from artemis_logger import get_logger
logger = get_logger('redis_pipeline_tracker')
'\nBACKWARD COMPATIBILITY WRAPPER\n\nThis module maintains backward compatibility while the codebase migrates\nto the new modular structure in redis/.\n\nAll functionality has been refactored into:\n- redis/models.py - StageStatus, PipelineStatus enums\n- redis/tracker.py - RedisPipelineTracker class\n\nTo migrate your code:\n    OLD: from redis_pipeline_tracker import RedisPipelineTracker\n    NEW: from redis import RedisPipelineTracker\n\nNo breaking changes - all imports remain identical.\n'
from redis import StageStatus, PipelineStatus, RedisPipelineTracker
__all__ = ['StageStatus', 'PipelineStatus', 'RedisPipelineTracker']
if __name__ == '__main__':
    import time
    
    logger.log('Testing Redis pipeline tracker...', 'INFO')
    try:
        tracker = RedisPipelineTracker()
        if not tracker.enabled:
            
            logger.log('❌ Redis not available. Start Redis with:', 'INFO')
            
            logger.log('   docker run -d -p 6379:6379 redis', 'INFO')
            exit(1)
        card_id = 'test-card-001'
        
        logger.log(f'\n1. Starting pipeline {card_id}...', 'INFO')
        tracker.start_pipeline(card_id, total_stages=3, metadata={'title': 'Test Pipeline', 'priority': 'high'})
        
        logger.log('\n2. Updating stage 1...', 'INFO')
        tracker.update_stage_status(card_id, 'stage_1', StageStatus.RUNNING, progress_percent=50, message='Processing data...')
        time.sleep(1)
        tracker.update_stage_status(card_id, 'stage_1', StageStatus.COMPLETED, progress_percent=100, message='Stage 1 complete')
        
        logger.log('\n3. Updating stage 2...', 'INFO')
        tracker.update_stage_status(card_id, 'stage_2', StageStatus.RUNNING, progress_percent=30, message='Running tests...')
        
        logger.log('\n4. Getting pipeline status...', 'INFO')
        status = tracker.get_pipeline_status(card_id)
        
        logger.log(f"   Status: {status['status']}", 'INFO')
        
        logger.log(f"   Completed: {status['completed_stages']}/{status['total_stages']}", 'INFO')
        
        logger.log(f"   Current: {status['current_stage']}", 'INFO')
        
        logger.log('\n5. Completing pipeline...', 'INFO')
        tracker.complete_pipeline(card_id, PipelineStatus.COMPLETED, 'All stages complete')
        final_status = tracker.get_pipeline_status(card_id)
        
        logger.log(f"   Final status: {final_status['status']}", 'INFO')
        
        logger.log(f"   Duration: {final_status['duration_seconds']:.2f} seconds", 'INFO')
        
        logger.log('\n6. Getting all stage statuses...', 'INFO')
        all_stages = tracker.get_all_stage_statuses(card_id)
        for stage in all_stages:
            
            logger.log(f"   {stage['stage_name']}: {stage['status']}", 'INFO')
        
        logger.log('\n✅ All pipeline tracker tests passed!', 'INFO')
    except Exception as e:
        
        logger.log(f'❌ Error: {e}', 'INFO')
        import traceback
        traceback.print_exc()