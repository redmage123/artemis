"""
Module: core.resilience.cli_demo

WHY: Provides CLI interface and demo for circuit breaker
RESPONSIBILITY: Command-line tools, interactive demos, status reporting
PATTERNS: Command Pattern, Factory Pattern

Architecture:
    - Demo mode: Interactive circuit breaker demonstration
    - Status mode: Report all circuit breaker statuses
    - Dispatch table for command routing

Design Decisions:
    - Extracted from main circuit_breaker.py for SRP
    - Guard clauses for command handling
    - Clean separation of concerns
"""
import sys
import time
import json
import logging
import argparse
from typing import Callable, Dict
from core.resilience import CircuitBreaker, CircuitBreakerConfig, CircuitBreakerOpenError, get_all_circuit_breaker_statuses

def create_unreliable_service(breaker: CircuitBreaker, service_state: dict) -> Callable:
    """
    Create unreliable service for demo.

    WHY: Factory function for demo service

    Args:
        breaker: Circuit breaker instance
        service_state: Dictionary to track call count

    Returns:
        Protected service function
    """

    @breaker.protect
    def unreliable_service():
        service_state['call_count'] += 1
        if service_state['call_count'] <= 3:
            raise Exception(f"Service failed (call {service_state['call_count']})")
        return f"Success (call {service_state['call_count']})"
    return unreliable_service

def run_demo():
    """
    Run circuit breaker demo.

    WHY: Interactive demonstration of circuit breaker behavior
    """
    
    logger.log('=' * 80, 'INFO')
    
    logger.log('CIRCUIT BREAKER DEMO', 'INFO')
    
    logger.log('=' * 80, 'INFO')
    config = CircuitBreakerConfig(failure_threshold=3, timeout_seconds=5)
    breaker = CircuitBreaker('demo_service', config)
    service_state = {'call_count': 0}
    unreliable_service = create_unreliable_service(breaker, service_state)
    for i in range(10):
        try:
            result = unreliable_service()
            
            logger.log(f'✅ Call {i + 1}: {result}', 'INFO')
        except CircuitBreakerOpenError as e:
            
            logger.log(f'⛔ Call {i + 1}: Circuit breaker OPEN - {e}', 'INFO')
        except Exception as e:
            
            logger.log(f'❌ Call {i + 1}: Failed - {e}', 'INFO')
        time.sleep(0.5)
    
    logger.log('\n' + '=' * 80, 'INFO')
    
    logger.log('STATUS:', 'INFO')
    
    logger.log('=' * 80, 'INFO')
    
    logger.log(json.dumps(breaker.get_status(), indent=2), 'INFO')

def show_status():
    """
    Show circuit breaker statuses.

    WHY: Reports status of all registered circuit breakers
    """
    statuses = get_all_circuit_breaker_statuses()
    if not statuses:
        
        logger.log('No circuit breakers registered', 'INFO')
        sys.exit(0)
    
    logger.log(json.dumps(statuses, indent=2), 'INFO')

def main():
    """
    Main CLI entry point.

    WHY: Dispatch table for command routing (no elif chains)
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser(description='Circuit Breaker Demo')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--status', action='store_true', help='Show circuit breaker statuses')
    args = parser.parse_args()
    commands: Dict[str, Callable] = {'demo': run_demo, 'status': show_status}
    for arg_name, handler in commands.items():
        if getattr(args, arg_name):
            handler()
            sys.exit(0)
    parser.print_help()
if __name__ == '__main__':
    main()