from artemis_logger import get_logger
logger = get_logger('detector_core')
'\nPlatform Detector Core\n\nWHY: Orchestrates platform detection and resource allocation calculation.\nRESPONSIBILITY: Coordinate detection modules and provide unified platform detection API.\nPATTERNS: Facade pattern - provides simple interface to complex subsystems.\n\nThis module provides:\n- PlatformDetector: Main platform detection coordinator\n- Resource allocation calculation\n- Platform hash calculation\n- Platform comparison\n'
import hashlib
from typing import Any, Optional, Tuple, List
from platform_pkg.models import PlatformInfo, ResourceAllocation
from platform_pkg.os_detector import OSDetector
from platform_pkg.arch_detector import ArchDetector, MemoryDetector
from platform_pkg.env_detector import DiskDetector, PythonDetector, HostnameDetector

class PlatformDetector:
    """
    Detects platform information and provides resource allocation recommendations.

    WHY: Provides unified interface for platform detection and resource calculation.
    RESPONSIBILITY: Orchestrate detection modules and calculate resource allocation.
    PATTERNS: Facade pattern - coordinates multiple detection subsystems.
    """

    def __init__(self, logger: Optional[Any]=None):
        """
        Initialize platform detector.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger
        self._os_detector = OSDetector()
        self._arch_detector = ArchDetector()
        self._memory_detector = MemoryDetector()
        self._disk_detector = DiskDetector()
        self._python_detector = PythonDetector()
        self._hostname_detector = HostnameDetector()

    def detect_platform(self) -> PlatformInfo:
        """
        Detect current platform information.

        WHY: Provides complete platform profile for resource allocation.
        PERFORMANCE: Delegates to specialized detectors.

        Returns:
            Complete platform information
        """
        os_info = self._os_detector.detect_os_info()
        cpu_info = self._arch_detector.detect_all()
        memory_info = self._memory_detector.detect_all()
        disk_info = self._disk_detector.detect_all()
        python_info = self._python_detector.detect_all()
        hostname = self._hostname_detector.detect_hostname()
        info = PlatformInfo(os_type=os_info['os_type'], os_name=os_info['os_name'], os_version=os_info['os_version'], os_release=os_info['os_release'], cpu_count_physical=cpu_info['cpu_count_physical'], cpu_count_logical=cpu_info['cpu_count_logical'], cpu_frequency_mhz=cpu_info['cpu_frequency_mhz'], cpu_architecture=cpu_info['cpu_architecture'], total_memory_gb=memory_info['total_memory_gb'], available_memory_gb=memory_info['available_memory_gb'], total_disk_gb=disk_info['total_disk_gb'], available_disk_gb=disk_info['available_disk_gb'], disk_type=disk_info['disk_type'], python_version=python_info['python_version'], python_implementation=python_info['python_implementation'], hostname=hostname, platform_hash='')
        info.platform_hash = self._calculate_platform_hash(info)
        return info

    def calculate_resource_allocation(self, platform_info: PlatformInfo) -> ResourceAllocation:
        """
        Calculate optimal resource allocation based on platform.

        WHY: Provides resource limits tailored to platform capabilities.
        RESPONSIBILITY: Calculate parallel limits, memory allocation, and performance tuning.

        Args:
            platform_info: Detected platform information

        Returns:
            Resource allocation recommendations
        """
        reasoning_parts = []
        max_developers = self._calculate_max_developers(platform_info, reasoning_parts)
        max_tests = self._calculate_max_tests(platform_info, reasoning_parts)
        max_stages = self._calculate_max_stages(reasoning_parts)
        max_memory_per_agent = self._calculate_memory_per_agent(platform_info, max_developers, max_tests, reasoning_parts)
        batch_size = self._calculate_batch_size(platform_info, reasoning_parts)
        use_async = self._should_use_async_io(platform_info, reasoning_parts)
        enable_caching = self._should_enable_caching(platform_info, reasoning_parts)
        thread_pool_size = self._calculate_thread_pool_size(platform_info, reasoning_parts)
        return ResourceAllocation(max_parallel_developers=max_developers, max_parallel_tests=max_tests, max_parallel_stages=max_stages, max_memory_per_agent_gb=max_memory_per_agent, recommended_batch_size=batch_size, use_async_io=use_async, enable_caching=enable_caching, thread_pool_size=thread_pool_size, reasoning=' | '.join(reasoning_parts))

    def platforms_match(self, info1: PlatformInfo, info2: PlatformInfo) -> bool:
        """
        Check if two platform infos represent the same platform.

        WHY: Enables platform change detection for configuration updates.

        Args:
            info1: First platform info
            info2: Second platform info

        Returns:
            True if platforms match
        """
        return info1.platform_hash == info2.platform_hash

    def log(self, message: str, level: str='INFO'):
        """
        Log a message with fallback to print.

        WHY: Provides logging even when logger is not configured.
        PERFORMANCE: Early return avoids unnecessary print() call.

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)
        """
        if self.logger:
            self.logger.log(message, level)
            return
        
        logger.log(f'[{level}] {message}', 'INFO')

    def _calculate_max_developers(self, platform_info: PlatformInfo, reasoning_parts: List[str]) -> int:
        """
        Calculate maximum parallel developers.

        WHY: Use 1 developer per 2 cores, capped at 4 for safety.

        Args:
            platform_info: Platform information
            reasoning_parts: List to append reasoning to

        Returns:
            Maximum parallel developers
        """
        max_developers = min(max(1, platform_info.cpu_count_logical // 2), 4)
        reasoning_parts.append(f'Developers: {max_developers} (CPU cores: {platform_info.cpu_count_logical})')
        return max_developers

    def _calculate_max_tests(self, platform_info: PlatformInfo, reasoning_parts: List[str]) -> int:
        """
        Calculate maximum parallel test runners.

        WHY: Tests can be more parallel - use 1 test runner per core, up to 8.

        Args:
            platform_info: Platform information
            reasoning_parts: List to append reasoning to

        Returns:
            Maximum parallel test runners
        """
        max_tests = min(platform_info.cpu_count_logical, 8)
        reasoning_parts.append(f'Test runners: {max_tests} (CPU cores: {platform_info.cpu_count_logical})')
        return max_tests

    def _calculate_max_stages(self, reasoning_parts: List[str]) -> int:
        """
        Calculate maximum parallel stages.

        WHY: Conservative - only 2 stages in parallel to avoid resource contention.

        Args:
            reasoning_parts: List to append reasoning to

        Returns:
            Maximum parallel stages
        """
        max_stages = 2
        reasoning_parts.append(f'Parallel stages: {max_stages}')
        return max_stages

    def _calculate_memory_per_agent(self, platform_info: PlatformInfo, max_developers: int, max_tests: int, reasoning_parts: List[str]) -> float:
        """
        Calculate memory allocation per agent.

        WHY: Reserve 2GB for system, divide rest by max parallel agents.

        Args:
            platform_info: Platform information
            max_developers: Maximum parallel developers
            max_tests: Maximum parallel tests
            reasoning_parts: List to append reasoning to

        Returns:
            Memory per agent in GB
        """
        reserved_memory = 2.0
        total_agents = max_developers + max_tests
        max_memory_per_agent = max(1.0, (platform_info.available_memory_gb - reserved_memory) / total_agents)
        reasoning_parts.append(f'Memory per agent: {max_memory_per_agent:.1f}GB (Available: {platform_info.available_memory_gb:.1f}GB)')
        return max_memory_per_agent

    def _calculate_batch_size(self, platform_info: PlatformInfo, reasoning_parts: List[str]) -> int:
        """
        Calculate batch size based on available memory.

        WHY: Larger batches for more memory improve throughput.
        PATTERNS: Dispatch table instead of if/elif chain.

        Args:
            platform_info: Platform information
            reasoning_parts: List to append reasoning to

        Returns:
            Recommended batch size
        """
        memory_to_batch_size: List[Tuple[float, int]] = [(16, 100), (8, 50), (0, 25)]
        batch_size = next((size for threshold, size in memory_to_batch_size if platform_info.total_memory_gb >= threshold), 25)
        reasoning_parts.append(f'Batch size: {batch_size}')
        return batch_size

    def _should_use_async_io(self, platform_info: PlatformInfo, reasoning_parts: List[str]) -> bool:
        """
        Determine if async I/O should be enabled.

        WHY: Async I/O works best on Linux/macOS, optional on Windows.

        Args:
            platform_info: Platform information
            reasoning_parts: List to append reasoning to

        Returns:
            True if async I/O should be enabled
        """
        use_async = platform_info.os_type in ['linux', 'darwin']
        reasoning_parts.append(f'Async I/O: {use_async}')
        return use_async

    def _should_enable_caching(self, platform_info: PlatformInfo, reasoning_parts: List[str]) -> bool:
        """
        Determine if caching should be enabled.

        WHY: Enable caching if we have enough memory (>= 4GB available).

        Args:
            platform_info: Platform information
            reasoning_parts: List to append reasoning to

        Returns:
            True if caching should be enabled
        """
        enable_caching = platform_info.available_memory_gb >= 4.0
        reasoning_parts.append(f'Caching: {enable_caching}')
        return enable_caching

    def _calculate_thread_pool_size(self, platform_info: PlatformInfo, reasoning_parts: List[str]) -> int:
        """
        Calculate thread pool size for I/O operations.

        WHY: Thread pool size of 2x CPU cores, capped at 16.

        Args:
            platform_info: Platform information
            reasoning_parts: List to append reasoning to

        Returns:
            Thread pool size
        """
        thread_pool_size = min(platform_info.cpu_count_logical * 2, 16)
        reasoning_parts.append(f'Thread pool: {thread_pool_size}')
        return thread_pool_size

    def _calculate_platform_hash(self, info: PlatformInfo) -> str:
        """
        Calculate a hash of platform characteristics.

        WHY: Helps detect if the platform has changed significantly.

        Args:
            info: Platform information

        Returns:
            SHA256 hash of key platform characteristics
        """
        key_data = f'{info.os_type}|{info.os_name}|{info.cpu_count_physical}|{info.cpu_count_logical}|{info.cpu_architecture}|{info.total_memory_gb:.0f}|{info.hostname}'
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]

def get_platform_summary(info: PlatformInfo, allocation: ResourceAllocation) -> str:
    """
    Generate a human-readable platform summary.

    WHY: Provides formatted output for platform detection results.

    Args:
        info: Platform information
        allocation: Resource allocation

    Returns:
        Formatted summary string
    """
    return f"\n======================================================================\nARTEMIS PLATFORM DETECTION\n======================================================================\n\nOperating System:\n  Type:         {info.os_type}\n  Name:         {info.os_name}\n  Version:      {info.os_version}\n  Release:      {info.os_release}\n  Architecture: {info.cpu_architecture}\n\nHardware:\n  CPU Cores:    {info.cpu_count_physical} physical, {info.cpu_count_logical} logical\n  CPU Speed:    {info.cpu_frequency_mhz:.0f} MHz\n  Total Memory: {info.total_memory_gb:.1f} GB\n  Free Memory:  {info.available_memory_gb:.1f} GB\n  Disk Space:   {info.available_disk_gb:.1f} GB / {info.total_disk_gb:.1f} GB\n  Disk Type:    {info.disk_type}\n\nPython:\n  Version:      {info.python_version}\n  Implementation: {info.python_implementation}\n\nResource Allocation:\n  Max Parallel Developers: {allocation.max_parallel_developers}\n  Max Parallel Tests:      {allocation.max_parallel_tests}\n  Max Parallel Stages:     {allocation.max_parallel_stages}\n  Memory per Agent:        {allocation.max_memory_per_agent_gb:.1f} GB\n  Batch Size:              {allocation.recommended_batch_size}\n  Async I/O:               {('Enabled' if allocation.use_async_io else 'Disabled')}\n  Caching:                 {('Enabled' if allocation.enable_caching else 'Disabled')}\n  Thread Pool Size:        {allocation.thread_pool_size}\n\nReasoning: {allocation.reasoning}\n\nPlatform Hash: {info.platform_hash}\n\n======================================================================\n"