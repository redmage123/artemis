from artemis_logger import get_logger
logger = get_logger('redis_metrics')
'\nRedis-based Metrics Tracking for Artemis\n\nSingle Responsibility: Track and aggregate pipeline metrics\nStores time-series data for analytics and monitoring\n'
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from redis_client import RedisClient, get_redis_client, is_redis_available

class RedisMetrics:
    """
    Metrics tracker using Redis

    Features:
    - Time-series data storage
    - Aggregate statistics (counters, averages)
    - Cost tracking
    - Performance monitoring
    """

    def __init__(self, redis_client: Optional[RedisClient]=None, key_prefix: str='artemis:metrics'):
        """
        Initialize metrics tracker

        Args:
            redis_client: Redis client (uses default if not provided)
            key_prefix: Redis key prefix for namespacing
        """
        if redis_client:
            self.redis = redis_client
        else:
            self.redis = get_redis_client(raise_on_error=False)
        self.key_prefix = key_prefix
        self.enabled = self.redis is not None
        if not self.enabled:
            
            logger.log('⚠️  Redis not available - Metrics tracking disabled', 'INFO')

    def track_pipeline_completion(self, card_id: str, duration_seconds: float, status: str, total_cost: float=0.0, metadata: Optional[Dict[str, Any]]=None) -> bool:
        """
        Track pipeline completion

        Args:
            card_id: Card ID
            duration_seconds: Pipeline duration
            status: Final status (COMPLETED, FAILED, etc.)
            total_cost: Total LLM API cost
            metadata: Additional metadata

        Returns:
            True if tracked successfully
        """
        if not self.enabled:
            return False
        try:
            timestamp = time.time()
            date_key = datetime.now().strftime('%Y-%m-%d')
            ts_key = f'{self.key_prefix}:timeseries:pipelines'
            pipeline_data = {'card_id': card_id, 'duration_seconds': duration_seconds, 'status': status, 'cost': total_cost, 'timestamp': datetime.now().isoformat(), 'metadata': metadata or {}}
            self.redis.client.zadd(ts_key, {json.dumps(pipeline_data): timestamp})
            self.redis.client.hincrby(f'{self.key_prefix}:total', 'pipelines_completed', 1)
            self.redis.client.hincrbyfloat(f'{self.key_prefix}:total', 'total_cost', total_cost)
            self.redis.client.hincrbyfloat(f'{self.key_prefix}:total', 'total_duration', duration_seconds)
            day_key = f'{self.key_prefix}:daily:{date_key}'
            self.redis.client.hincrby(day_key, 'completions', 1)
            self.redis.client.hincrbyfloat(day_key, 'cost', total_cost)
            self.redis.client.hincrbyfloat(day_key, 'duration', duration_seconds)
            self.redis.expire(day_key, 2592000)
            status_key = f'{self.key_prefix}:status:{status.lower()}'
            self.redis.incr(status_key)
            return True
        except Exception as e:
            
            logger.log(f'⚠️  Failed to track pipeline completion: {e}', 'INFO')
            return False

    def track_llm_request(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int, cost: float, cache_hit: bool=False) -> bool:
        """
        Track LLM API request

        Args:
            provider: LLM provider (openai, anthropic)
            model: Model name
            prompt_tokens: Prompt tokens used
            completion_tokens: Completion tokens used
            cost: Request cost
            cache_hit: Whether response was cached

        Returns:
            True if tracked successfully
        """
        if not self.enabled:
            return False
        try:
            self.redis.client.hincrby(f'{self.key_prefix}:llm', 'total_requests', 1)
            self.redis.client.hincrby(f'{self.key_prefix}:llm', 'prompt_tokens', prompt_tokens)
            self.redis.client.hincrby(f'{self.key_prefix}:llm', 'completion_tokens', completion_tokens)
            self.redis.client.hincrbyfloat(f'{self.key_prefix}:llm', 'total_cost', cost)
            if cache_hit:
                self.redis.client.hincrby(f'{self.key_prefix}:llm', 'cache_hits', 1)
            else:
                self.redis.client.hincrby(f'{self.key_prefix}:llm', 'cache_misses', 1)
            provider_key = f'{self.key_prefix}:llm:{provider}'
            self.redis.client.hincrby(provider_key, 'requests', 1)
            self.redis.client.hincrbyfloat(provider_key, 'cost', cost)
            model_key = f'{self.key_prefix}:llm:model:{model}'
            self.redis.client.hincrby(model_key, 'requests', 1)
            self.redis.client.hincrbyfloat(model_key, 'cost', cost)
            return True
        except Exception as e:
            
            logger.log(f'⚠️  Failed to track LLM request: {e}', 'INFO')
            return False

    def track_code_review(self, developer: str, overall_score: int, critical_issues: int, high_issues: int, status: str) -> bool:
        """
        Track code review results

        Args:
            developer: Developer name (developer-a, developer-b)
            overall_score: Overall score (0-100)
            critical_issues: Number of critical issues
            high_issues: Number of high issues
            status: Review status (PASS, FAIL, etc.)

        Returns:
            True if tracked successfully
        """
        if not self.enabled:
            return False
        try:
            dev_key = f'{self.key_prefix}:code_review:{developer}'
            self.redis.client.hincrby(dev_key, 'total_reviews', 1)
            self.redis.client.hincrby(dev_key, 'total_score', overall_score)
            self.redis.client.hincrby(dev_key, 'critical_issues', critical_issues)
            self.redis.client.hincrby(dev_key, 'high_issues', high_issues)
            status_key = f'{self.key_prefix}:code_review:status:{status.lower()}'
            self.redis.incr(status_key)
            return True
        except Exception as e:

            logger.log(f'⚠️  Failed to track code review: {e}', 'INFO')
            return False

    def track_pipeline_selection(self, metric: Dict[str, Any]) -> bool:
        """
        Track adaptive pipeline selection decision

        Args:
            metric: Pipeline selection metric containing:
                - card_id: Card ID
                - title: Task title
                - complexity: Detected complexity (simple/medium/complex)
                - path: Selected path (fast/medium/full)
                - estimated_duration_minutes: Estimated duration
                - num_stages: Number of stages
                - reasoning: Selection reasoning
                - timestamp: ISO timestamp

        Returns:
            True if tracked successfully
        """
        if not self.enabled:
            return False
        try:
            timestamp = time.time()

            # Store in time-series for historical analysis
            ts_key = f'{self.key_prefix}:timeseries:adaptive_selections'
            self.redis.client.zadd(ts_key, {json.dumps(metric): timestamp})

            # Track totals by path
            path = metric['path']
            path_key = f'{self.key_prefix}:adaptive:path:{path}'
            self.redis.client.hincrby(path_key, 'count', 1)
            self.redis.client.hincrbyfloat(path_key, 'total_estimated_duration', metric['estimated_duration_minutes'])
            self.redis.client.hincrby(path_key, 'total_stages', metric['num_stages'])

            # Track by complexity
            complexity = metric['complexity']
            complexity_key = f'{self.key_prefix}:adaptive:complexity:{complexity}'
            self.redis.client.hincrby(complexity_key, 'count', 1)

            # Track complexity-to-path mapping
            mapping_key = f'{self.key_prefix}:adaptive:mapping:{complexity}:{path}'
            self.redis.client.incr(mapping_key)

            # Overall adaptive selections count
            self.redis.client.hincrby(f'{self.key_prefix}:adaptive:total', 'selections', 1)
            self.redis.client.hincrbyfloat(f'{self.key_prefix}:adaptive:total', 'total_estimated_duration', metric['estimated_duration_minutes'])

            return True
        except Exception as e:

            logger.log(f'⚠️  Failed to track pipeline selection: {e}', 'INFO')
            return False

    def get_adaptive_metrics(self) -> Dict[str, Any]:
        """
        Get adaptive pipeline selection metrics

        Returns:
            Dictionary with adaptive selection statistics
        """
        if not self.enabled:
            return {'enabled': False}
        try:
            # Get total selections
            totals = self.redis.hgetall(f'{self.key_prefix}:adaptive:total')
            total_selections = int(totals.get('selections', 0))
            total_estimated_duration = float(totals.get('total_estimated_duration', 0))

            # Get path distribution
            paths = {}
            for path in ['fast', 'medium', 'full']:
                path_key = f'{self.key_prefix}:adaptive:path:{path}'
                path_data = self.redis.hgetall(path_key)
                count = int(path_data.get('count', 0))
                if count > 0:
                    total_duration = float(path_data.get('total_estimated_duration', 0))
                    total_stages = int(path_data.get('total_stages', 0))
                    paths[path] = {
                        'count': count,
                        'percentage': round(count / total_selections * 100, 1) if total_selections > 0 else 0,
                        'avg_estimated_duration': round(total_duration / count, 1),
                        'avg_stages': round(total_stages / count, 1)
                    }

            # Get complexity distribution
            complexities = {}
            for complexity in ['simple', 'medium', 'complex']:
                complexity_key = f'{self.key_prefix}:adaptive:complexity:{complexity}'
                count = int(self.redis.hget(complexity_key, 'count') or 0)
                if count > 0:
                    complexities[complexity] = {
                        'count': count,
                        'percentage': round(count / total_selections * 100, 1) if total_selections > 0 else 0
                    }

            # Calculate time savings (compare fast/medium selections to if they used full)
            baseline_full_duration = 90  # Full path baseline
            time_saved = 0
            for path, data in paths.items():
                if path in ['fast', 'medium']:
                    avg_duration = data['avg_estimated_duration']
                    savings_per_task = baseline_full_duration - avg_duration
                    time_saved += savings_per_task * data['count']

            return {
                'enabled': True,
                'total_selections': total_selections,
                'total_estimated_duration_minutes': round(total_estimated_duration, 1),
                'avg_estimated_duration_minutes': round(total_estimated_duration / total_selections, 1) if total_selections > 0 else 0,
                'paths': paths,
                'complexities': complexities,
                'time_saved_minutes': round(time_saved, 1),
                'time_saved_hours': round(time_saved / 60, 1)
            }
        except Exception as e:

            logger.log(f'⚠️  Failed to get adaptive metrics: {e}', 'INFO')
            return {'enabled': True, 'error': str(e)}

    def get_recent_selections(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent adaptive pipeline selections

        Args:
            limit: Max number of selections to return

        Returns:
            List of recent selection metrics
        """
        if not self.enabled:
            return []
        try:
            ts_key = f'{self.key_prefix}:timeseries:adaptive_selections'
            recent = self.redis.client.zrevrange(ts_key, 0, limit - 1)
            selections = []
            for item in recent:
                try:
                    selection_data = json.loads(item)
                    selections.append(selection_data)
                except json.JSONDecodeError:
                    continue
            return selections
        except Exception as e:

            logger.log(f'⚠️  Failed to get recent selections: {e}', 'INFO')
            return []

    def get_total_metrics(self) -> Dict[str, Any]:
        """
        Get total aggregate metrics

        Returns:
            Dictionary with total metrics
        """
        if not self.enabled:
            return {'enabled': False}
        try:
            pipeline_metrics = self.redis.hgetall(f'{self.key_prefix}:total')
            llm_metrics = self.redis.hgetall(f'{self.key_prefix}:llm')
            pipelines = int(pipeline_metrics.get('pipelines_completed', 0))
            avg_duration = 0.0
            avg_cost = 0.0
            if pipelines > 0:
                total_duration = float(pipeline_metrics.get('total_duration', 0))
                total_cost = float(pipeline_metrics.get('total_cost', 0))
                avg_duration = total_duration / pipelines
                avg_cost = total_cost / pipelines
            cache_hits = int(llm_metrics.get('cache_hits', 0))
            cache_misses = int(llm_metrics.get('cache_misses', 0))
            total_llm_requests = cache_hits + cache_misses
            cache_hit_rate = cache_hits / total_llm_requests * 100 if total_llm_requests > 0 else 0
            return {'enabled': True, 'pipelines': {'total_completed': pipelines, 'total_duration_seconds': float(pipeline_metrics.get('total_duration', 0)), 'average_duration_seconds': round(avg_duration, 2), 'total_cost': float(pipeline_metrics.get('total_cost', 0)), 'average_cost': round(avg_cost, 4)}, 'llm': {'total_requests': int(llm_metrics.get('total_requests', 0)), 'cache_hits': cache_hits, 'cache_misses': cache_misses, 'cache_hit_rate_percent': round(cache_hit_rate, 2), 'total_cost': float(llm_metrics.get('total_cost', 0)), 'prompt_tokens': int(llm_metrics.get('prompt_tokens', 0)), 'completion_tokens': int(llm_metrics.get('completion_tokens', 0))}}
        except Exception as e:
            
            logger.log(f'⚠️  Failed to get total metrics: {e}', 'INFO')
            return {'enabled': True, 'error': str(e)}

    def get_daily_metrics(self, date: Optional[datetime]=None) -> Dict[str, Any]:
        """
        Get metrics for a specific day

        Args:
            date: Date to get metrics for (default: today)

        Returns:
            Dictionary with daily metrics
        """
        if not self.enabled:
            return {'enabled': False}
        try:
            if date is None:
                date = datetime.now()
            date_key = date.strftime('%Y-%m-%d')
            day_key = f'{self.key_prefix}:daily:{date_key}'
            metrics = self.redis.hgetall(day_key)
            completions = int(metrics.get('completions', 0))
            return {'enabled': True, 'date': date_key, 'completions': completions, 'total_cost': float(metrics.get('cost', 0)), 'total_duration': float(metrics.get('duration', 0))}
        except Exception as e:
            
            logger.log(f'⚠️  Failed to get daily metrics: {e}', 'INFO')
            return {'enabled': True, 'error': str(e)}

    def get_recent_pipelines(self, limit: int=10) -> List[Dict[str, Any]]:
        """
        Get recent pipeline executions

        Args:
            limit: Max number of pipelines to return

        Returns:
            List of recent pipeline data
        """
        if not self.enabled:
            return []
        try:
            ts_key = f'{self.key_prefix}:timeseries:pipelines'
            recent = self.redis.client.zrevrange(ts_key, 0, limit - 1)
            pipelines = []
            for item in recent:
                try:
                    pipeline_data = json.loads(item)
                    pipelines.append(pipeline_data)
                except json.JSONDecodeError:
                    continue
            return pipelines
        except Exception as e:
            
            logger.log(f'⚠️  Failed to get recent pipelines: {e}', 'INFO')
            return []


# Convenience functions for module-level usage
_default_metrics_instance = None


def get_metrics_instance() -> RedisMetrics:
    """Get or create default metrics instance."""
    global _default_metrics_instance
    if _default_metrics_instance is None:
        _default_metrics_instance = RedisMetrics()
    return _default_metrics_instance


def track_pipeline_selection(metric: Dict[str, Any]) -> bool:
    """
    Convenience function to track adaptive pipeline selection.

    Args:
        metric: Pipeline selection metric

    Returns:
        True if tracked successfully
    """
    metrics = get_metrics_instance()
    return metrics.track_pipeline_selection(metric)


def get_adaptive_metrics() -> Dict[str, Any]:
    """
    Convenience function to get adaptive metrics.

    Returns:
        Adaptive metrics dictionary
    """
    metrics = get_metrics_instance()
    return metrics.get_adaptive_metrics()


def get_recent_selections(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function to get recent selections.

    Args:
        limit: Max number of selections to return

    Returns:
        List of recent selections
    """
    metrics = get_metrics_instance()
    return metrics.get_recent_selections(limit)


if __name__ == '__main__':
    
    logger.log('Testing Redis metrics...', 'INFO')
    try:
        metrics = RedisMetrics()
        if not metrics.enabled:
            
            logger.log('❌ Redis not available. Start Redis with:', 'INFO')
            
            logger.log('   docker run -d -p 6379:6379 redis', 'INFO')
            exit(1)
        
        logger.log('\n1. Tracking sample pipeline completions...', 'INFO')
        for i in range(5):
            metrics.track_pipeline_completion(card_id=f'test-card-{i}', duration_seconds=120.5 + i * 10, status='COMPLETED', total_cost=0.15 + i * 0.05, metadata={'test': True})
        
        logger.log('\n2. Tracking sample LLM requests...', 'INFO')
        for i in range(10):
            metrics.track_llm_request(provider='openai', model='gpt-4o', prompt_tokens=1000, completion_tokens=500, cost=0.05, cache_hit=i % 2 == 0)
        
        logger.log('\n3. Getting total metrics...', 'INFO')
        total = metrics.get_total_metrics()
        
        logger.log(f"   Pipelines: {total['pipelines']['total_completed']}", 'INFO')
        
        logger.log(f"   Avg Duration: {total['pipelines']['average_duration_seconds']}s", 'INFO')
        
        logger.log(f"   Total Cost: ${total['pipelines']['total_cost']:.2f}", 'INFO')
        
        logger.log(f"   LLM Requests: {total['llm']['total_requests']}", 'INFO')
        
        logger.log(f"   Cache Hit Rate: {total['llm']['cache_hit_rate_percent']}%", 'INFO')
        
        logger.log('\n4. Getting recent pipelines...', 'INFO')
        recent = metrics.get_recent_pipelines(limit=3)
        for pipeline in recent:
            
            logger.log(f"   {pipeline['card_id']}: {pipeline['status']} in {pipeline['duration_seconds']}s", 'INFO')
        
        logger.log('\n✅ All metrics tests passed!', 'INFO')
    except Exception as e:
        
        logger.log(f'❌ Error: {e}', 'INFO')
        import traceback
        traceback.print_exc()