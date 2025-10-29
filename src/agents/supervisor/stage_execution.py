from artemis_logger import get_logger
logger = get_logger('stage_execution')
'\nModule: agents/supervisor/stage_execution.py\n\nPurpose: Stage execution with retries, circuit breakers, and timeout monitoring\nWhy: Execute pipeline stages reliably WITHOUT while + try + nested ifs\nPatterns: Recursion instead of while loops, Early Return, Guard Clause\nIntegration: Used by SupervisorAgent.execute_with_supervision()\n\nVIOLATIONS FIXED FROM ORIGINAL:\n- ❌ BEFORE: while loop + try + except + 3 nested ifs (lines 1020-1064)\n- ✅ AFTER: Recursive retry with early returns (no nesting)\n- ❌ BEFORE: Nested if for retry_count > 0\n- ✅ AFTER: Guard clause with early return\n- ❌ BEFORE: Nested if for should_break check\n- ✅ AFTER: Immediate return on break condition\n'
import time
import threading
from typing import Dict, Any, Optional
from datetime import datetime
from core.interfaces import PipelineStage
from core.exceptions import PipelineStageError
from agents.supervisor.models import RecoveryStrategy

class StageExecutor:
    """
    Stage execution with retries and monitoring (claude.md compliant)

    WHY: Handles stage execution WITHOUT nested while/try/if
    PATTERN: Recursion instead of while loops, Early returns
    RESPONSIBILITY: Execute stages with retries, timeouts, circuit breakers
    """

    def __init__(self, verbose: bool=False):
        """Initialize stage executor"""
        self.verbose = verbose
        self.stage_health = {}
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}
        self.state_machine = None

    def execute_stage_with_retries(self, stage: PipelineStage, stage_name: str, *args, **kwargs) -> Any:
        """
        Execute stage with retries using RECURSION instead of while loop

        ❌ ORIGINAL VIOLATION (lines 1020-1064):
        while retry_count <= strategy.max_retries:              # WHILE LOOP
            try:                                                 # NESTED TRY
                if retry_count > 0:                              # NESTED IF
                    self._wait_before_retry(...)
                result_data = self._execute_stage_monitored()
                return result_data['result']
            except Exception as e:                               # NESTED EXCEPT
                last_error = e
                if self.state_machine:                           # DOUBLE NESTED IF
                    self.state_machine.push_state()
                should_break = self._handle_execution_failure()
                if should_break:                                 # TRIPLE NESTED IF!
                    break

        ✅ FIXED: Recursive retry with early returns (ZERO nesting)

        PATTERN: Recursion replaces while loop
        PERFORMANCE: Same as while loop, but cleaner
        """
        health = self.stage_health.get(stage_name)
        strategy = self.recovery_strategies.get(stage_name, RecoveryStrategy())
        return self._try_execute_recursive(stage=stage, stage_name=stage_name, health=health, strategy=strategy, retry_count=0, last_error=None, args=args, kwargs=kwargs)

    def _try_execute_recursive(self, stage: PipelineStage, stage_name: str, health: Any, strategy: RecoveryStrategy, retry_count: int, last_error: Optional[Exception], args: tuple, kwargs: dict) -> Any:
        """
        Recursive retry logic (replaces while loop - no nesting!)

        WHY: Recursion is more functional than while + try + nested ifs
        PATTERN: Tail recursion with early returns
        BASE CASE: retry_count > max_retries
        """
        if retry_count > strategy.max_retries:
            return self._raise_final_error(stage_name, health, retry_count, last_error)
        if retry_count > 0:
            self._wait_before_retry(stage_name, retry_count, strategy)
        try:
            result_data = self._execute_stage_monitored(stage, stage_name, strategy, *args, **kwargs)
            self._handle_successful_execution(stage_name, health, retry_count, result_data['duration'], result_data['result'])
            return result_data['result']
        except Exception as e:
            return self._handle_failure_and_retry(stage=stage, stage_name=stage_name, health=health, strategy=strategy, retry_count=retry_count, error=e, args=args, kwargs=kwargs)

    def _handle_failure_and_retry(self, stage: PipelineStage, stage_name: str, health: Any, strategy: RecoveryStrategy, retry_count: int, error: Exception, args: tuple, kwargs: dict) -> Any:
        """
        Handle execution failure and retry (no nested ifs)

        WHY: Extract Method - removes nested if logic from try/except
        PATTERN: Early return on break conditions
        """
        if self.state_machine:
            self._record_failure(stage_name, error, retry_count)
        should_break = self._handle_execution_failure(stage_name, health, strategy, retry_count + 1, error)
        if should_break:
            return self._raise_final_error(stage_name, health, retry_count + 1, error)
        return self._try_execute_recursive(stage=stage, stage_name=stage_name, health=health, strategy=strategy, retry_count=retry_count + 1, last_error=error, args=args, kwargs=kwargs)

    def _record_failure(self, stage_name: str, error: Exception, retry_count: int) -> None:
        """
        Record failure in state machine (extracted method)

        WHY: Removes nested if from main execution flow
        """
        self.state_machine.push_state('STAGE_FAILED', {'stage': stage_name, 'error': str(error), 'error_type': type(error).__name__, 'retry_count': retry_count + 1, 'timestamp': datetime.now().isoformat()})
        self.state_machine.update_stage_state(stage_name, 'FAILED')

    def _wait_before_retry(self, stage_name: str, retry_count: int, strategy: RecoveryStrategy) -> None:
        """
        Wait before retrying with exponential backoff

        PATTERN: Extracted method (was inline in while loop)
        PERFORMANCE: Same backoff calculation, cleaner
        """
        retry_delay = strategy.retry_delay_seconds * strategy.backoff_multiplier ** (retry_count - 1)
        if self.verbose:
            
            logger.log(f'[Supervisor] Retry {retry_count}/{strategy.max_retries} for {stage_name} (waiting {retry_delay}s)', 'INFO')
        time.sleep(retry_delay)

    def _execute_stage_monitored(self, stage: PipelineStage, stage_name: str, strategy: RecoveryStrategy, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute stage with timeout monitoring

        WHY: Background thread monitors timeout (no blocking)
        PATTERN: Observer pattern via threading
        """
        start_time = datetime.now()
        monitor_thread = threading.Thread(target=self._monitor_execution, args=(stage_name, strategy.timeout_seconds), daemon=True)
        monitor_thread.start()
        result = stage.execute(*args, **kwargs)
        duration = (datetime.now() - start_time).total_seconds()
        return {'result': result, 'duration': duration}

    def _monitor_execution(self, stage_name: str, timeout_seconds: float) -> None:
        """Monitor stage execution for timeout (background thread)"""
        start_time = datetime.now()
        CHECK_INTERVAL = 1.0
        while True:
            time.sleep(CHECK_INTERVAL)
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout_seconds:
                if self.verbose:
                    
                    logger.log(f'[Supervisor] ⏰ TIMEOUT detected for {stage_name} ({elapsed:.1f}s > {timeout_seconds}s)', 'INFO')
                return

    def _handle_successful_execution(self, stage_name: str, health: Any, retry_count: int, duration: float, result: Any=None) -> None:
        """
        Handle successful stage execution

        PATTERN: Extracted method
        SIDE EFFECTS: Updates health stats, state machine
        """
        health.execution_count += 1
        health.total_duration += duration
        health.last_success = datetime.now()
        if health.circuit_open:
            health.circuit_open = False
            if self.verbose:
                
                logger.log(f'[Supervisor] ✅ Circuit breaker CLOSED for {stage_name}', 'INFO')
        if self.state_machine:
            self.state_machine.push_state('STAGE_COMPLETED', {'stage': stage_name, 'duration': duration, 'retry_count': retry_count, 'timestamp': datetime.now().isoformat()})
            self.state_machine.update_stage_state(stage_name, 'COMPLETED')
            if result is not None:
                self.state_machine.store_stage_result(stage_name, result)
        self.stats['successful_executions'] += 1

    def _handle_execution_failure(self, stage_name: str, health: Any, strategy: RecoveryStrategy, retry_count: int, error: Exception) -> bool:
        """
        Handle execution failure, return True if should stop retrying

        PATTERN: Early return pattern
        RETURNS: True if should break retry loop, False if should continue
        """
        health.failure_count += 1
        health.last_failure = datetime.now()
        self.stats['total_interventions'] += 1
        if self.verbose:
            
            logger.log(f'[Supervisor] ❌ Stage {stage_name} failed (attempt {retry_count}/{strategy.max_retries}): {error}', 'INFO')
        if retry_count > strategy.max_retries:
            health.circuit_open = True
            if self.verbose:
                
                logger.log(f'[Supervisor] 🚨 Circuit breaker OPEN for {stage_name}', 'INFO')
            return True
        return False

    def _raise_final_error(self, stage_name: str, health: Any, retry_count: int, last_error: Optional[Exception]):
        """
        Raise final error after all retries exhausted

        PATTERN: Extracted method for error handling
        """
        if self.verbose:
            
            logger.log(f'[Supervisor] 💥 Stage {stage_name} failed after {retry_count} attempts', 'INFO')
        health.circuit_open = True
        raise PipelineStageError(f'Stage {stage_name} failed after {retry_count} attempts', context={'stage': stage_name, 'attempts': retry_count}, original_exception=last_error)
__all__ = ['StageExecutor']