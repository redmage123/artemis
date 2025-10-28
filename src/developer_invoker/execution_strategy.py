#!/usr/bin/env python3
"""
WHY: Execute developers in parallel or sequential mode based on configuration
RESPONSIBILITY: Provide execution strategies for developer invocation
PATTERNS: Strategy (execution mode), Template Method (execution flow)

Execution strategies provide:
- Sequential execution (one developer at a time)
- Parallel execution (ThreadPoolExecutor for concurrent execution)
- Error handling and result collection
- Progress logging
"""

from typing import List, Dict, Callable
import concurrent.futures
from artemis_stage_interface import LoggerInterface
from path_config_service import get_path_config


class SequentialExecutionStrategy:
    """
    Execute developers sequentially (one at a time)

    Benefits:
    - Predictable execution order
    - Lower resource usage
    - Easier debugging
    - Simpler error tracking
    """

    def __init__(self, logger: LoggerInterface):
        """
        Initialize sequential execution strategy

        Args:
            logger: Logger for progress tracking
        """
        self.logger = logger

    def execute(
        self,
        dev_configs: List[Dict],
        invoke_func: Callable[[Dict], Dict]
    ) -> List[Dict]:
        """
        Execute developers sequentially

        Args:
            dev_configs: List of developer configurations
            invoke_func: Function to invoke developer (takes config dict)

        Returns:
            List of developer results
        """
        developers = []

        for config in dev_configs:
            result = invoke_func(**config)
            developers.append(result)

        return developers


class ParallelExecutionStrategy:
    """
    Execute developers in parallel using ThreadPoolExecutor

    Benefits:
    - Faster execution (concurrent processing)
    - Better resource utilization
    - Reduced wall-clock time
    """

    def __init__(self, logger: LoggerInterface):
        """
        Initialize parallel execution strategy

        Args:
            logger: Logger for progress tracking
        """
        self.logger = logger

    def execute(
        self,
        dev_configs: List[Dict],
        invoke_func: Callable[[Dict], Dict]
    ) -> List[Dict]:
        """
        Execute developers in parallel using threads

        Args:
            dev_configs: List of developer configurations
            invoke_func: Function to invoke developer (takes config dict)

        Returns:
            List of developer results
        """
        self.logger.log(f"Starting {len(dev_configs)} developers in parallel threads", "INFO")

        developers = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(dev_configs)) as executor:
            # Submit all developer tasks
            future_to_dev = {
                executor.submit(invoke_func, **config): config['developer_name']
                for config in dev_configs
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_dev):
                dev_name = future_to_dev[future]

                try:
                    result = future.result()
                    developers.append(result)
                    self.logger.log(f"✅ {dev_name} completed (parallel)", "SUCCESS")

                except Exception as e:
                    self.logger.log(f"❌ {dev_name} failed with exception: {e}", "ERROR")

                    # Create failure result
                    developers.append({
                        "developer": dev_name,
                        "success": False,
                        "error": str(e),
                        "files": [],
                        "output_dir": str(get_path_config().get_developer_dir(dev_name))
                    })

        self.logger.log(f"All {len(dev_configs)} developers completed", "INFO")

        return developers


class ExecutionStrategyFactory:
    """
    Factory for creating execution strategies

    Uses dispatch table for O(1) strategy selection.
    """

    # Dispatch table: parallel flag -> strategy class
    _STRATEGY_MAP = {
        True: ParallelExecutionStrategy,
        False: SequentialExecutionStrategy
    }

    @classmethod
    def create_strategy(
        cls,
        parallel: bool,
        logger: LoggerInterface
    ):
        """
        Create execution strategy based on parallel flag

        Args:
            parallel: True for parallel execution, False for sequential
            logger: Logger for progress tracking

        Returns:
            ExecutionStrategy instance (Sequential or Parallel)
        """
        # Dispatch table lookup - O(1)
        strategy_class = cls._STRATEGY_MAP[parallel]
        return strategy_class(logger)
