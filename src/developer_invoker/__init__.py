#!/usr/bin/env python3
"""
WHY: Provide public API for invoking developer agents in parallel or sequential mode
RESPONSIBILITY: Export DeveloperInvoker class for external use
PATTERNS: Facade (simplified API), Strategy (execution modes)

This package handles developer agent invocation with:
- Parallel or sequential execution
- Validation pipeline integration (Layer 3)
- RAG-enhanced validation (Layer 3.5)
- Event notification
- Requirements parsing

Example:
    from developer_invoker import DeveloperInvoker

    invoker = DeveloperInvoker(logger, observable)
    results = invoker.invoke_parallel_developers(
        num_developers=2,
        card=card,
        adr_content=adr,
        adr_file=adr_path,
        rag_agent=rag,
        parallel_execution=True
    )
"""

from developer_invoker.invoker import DeveloperInvoker

__all__ = ['DeveloperInvoker']
