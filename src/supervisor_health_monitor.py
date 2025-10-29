from artemis_logger import get_logger
logger = get_logger('supervisor_health_monitor')
'\nBACKWARD COMPATIBILITY WRAPPER\n\nWHY: Maintain compatibility with existing code using supervisor_health_monitor\nRESPONSIBILITY: Re-export all components from new modular structure\nPATTERNS: Facade (backward compatibility), Deprecation wrapper\n\nDEPRECATED: This module is provided for backward compatibility only.\nNew code should import from: supervisor.health\n\nMigration examples:\n    OLD: from supervisor_health_monitor import HealthMonitor, AgentHealthEvent\n    NEW: from supervisor.health import HealthMonitor, AgentHealthEvent\n\n    OLD: from supervisor_health_monitor import ProcessHealth, HealthStatus\n    NEW: from supervisor.health import ProcessHealth, HealthStatus\n\nPackage structure:\n    supervisor/health/\n    ├── __init__.py              # Package exports\n    ├── event_types.py           # AgentHealthEvent, HealthStatus, ProcessHealth (71 lines)\n    ├── agent_registry.py        # AgentRegistry (147 lines)\n    ├── process_monitor.py       # ProcessMonitor (187 lines)\n    ├── crash_detector.py        # CrashDetector (109 lines)\n    ├── progress_tracker.py      # ProgressTracker (169 lines)\n    ├── health_calculator.py     # HealthCalculator (95 lines)\n    ├── event_observer.py        # EventObserver (119 lines)\n    ├── watchdog.py              # Watchdog (182 lines)\n    └── health_monitor.py        # HealthMonitor (394 lines)\n\nTotal: ~1,473 lines (modular) vs 927 lines (original)\nModularization adds documentation and separation but reduces complexity per file.\n'
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from supervisor.health import AgentHealthEvent, AgentRegistry, CrashDetector, CrashInfo, EventObserver, HealthCalculator, HealthEventData, HealthMonitor, HealthStatus, ProcessHealth, ProcessMonitor, ProgressTracker, Watchdog
__all__ = ['HealthMonitor', 'AgentHealthEvent', 'HealthStatus', 'ProcessHealth', 'CrashInfo', 'HealthEventData', 'AgentRegistry', 'ProcessMonitor', 'CrashDetector', 'ProgressTracker', 'HealthCalculator', 'EventObserver', 'Watchdog']

def _run_demo() -> None:
    """Run health monitor demo"""
    
    logger.log('=' * 70, 'INFO')
    
    logger.log('HEALTH MONITOR DEMO', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    monitor = HealthMonitor(verbose=True)
    
    logger.log('\n--- Registering agents ---', 'INFO')
    monitor.register_agent('agent1', 'stage', heartbeat_interval=10.0)
    monitor.register_agent('agent2', 'worker', heartbeat_interval=15.0)
    
    logger.log('\n--- Simulating heartbeats ---', 'INFO')
    monitor.agent_heartbeat('agent1', {'progress': 50})
    monitor.agent_heartbeat('agent2', {'progress': 75})
    
    logger.log('\n--- Health Status ---', 'INFO')
    status = monitor.get_health_status()
    
    logger.log(f'Overall Health: {status.value}', 'INFO')
    
    logger.log('\n--- Statistics ---', 'INFO')
    stats = monitor.get_statistics()
    
    logger.log(json.dumps(stats, indent=2), 'INFO')
    
    logger.log('\n--- Unregistering agents ---', 'INFO')
    monitor.unregister_agent('agent1')
    monitor.unregister_agent('agent2')

def _show_stats() -> None:
    """Show health monitor statistics"""
    monitor = HealthMonitor(verbose=False)
    stats = monitor.get_statistics()
    
    logger.log(json.dumps(stats, indent=2), 'INFO')

def _main() -> None:
    """Main entry point for CLI"""
    import argparse
    parser = argparse.ArgumentParser(description='Health Monitor Demo')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    args = parser.parse_args()
    if args.demo:
        _run_demo()
        return
    if args.stats:
        _show_stats()
        return
    parser.print_help()
if __name__ == '__main__':
    _main()