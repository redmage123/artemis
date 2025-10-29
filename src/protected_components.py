"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in protected/.

All functionality has been refactored into:
- protected/base.py - BaseProtectedComponent (common circuit breaker logic)
- protected/rag.py - ProtectedRAGAgent
- protected/llm.py - ProtectedLLMClient
- protected/knowledge_graph.py - ProtectedKnowledgeGraph
- protected/health.py - Health check utilities

To migrate your code:
    OLD: from protected_components import ProtectedRAGAgent, ProtectedLLMClient
    NEW: from protected import ProtectedRAGAgent, ProtectedLLMClient

No breaking changes - all imports remain identical.
"""
from protected import ProtectedRAGAgent, ProtectedLLMClient, ProtectedKnowledgeGraph, check_all_protected_components, reset_all_circuit_breakers
__all__ = ['ProtectedRAGAgent', 'ProtectedLLMClient', 'ProtectedKnowledgeGraph', 'check_all_protected_components', 'reset_all_circuit_breakers']
if __name__ == '__main__':
    import argparse
    import logging
    import json
    import sys
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser(description='Protected Components Status')
    parser.add_argument('--status', action='store_true', help='Show all circuit breaker statuses')
    parser.add_argument('--reset', action='store_true', help='Reset all circuit breakers')
    parser.add_argument('--test-rag', action='store_true', help='Test RAG with protection')
    parser.add_argument('--test-llm', action='store_true', help='Test LLM with protection')
    args = parser.parse_args()
    if args.status:
        statuses = check_all_protected_components()
        
        logger.log(json.dumps(statuses, indent=2), 'INFO')
        sys.exit(0)
    if args.reset:
        reset_all_circuit_breakers()
        
        logger.log('✅ All circuit breakers reset', 'INFO')
        sys.exit(0)
    if args.test_rag:
        
        logger.log('Testing RAG with circuit breaker protection...', 'INFO')
        rag = ProtectedRAGAgent(db_path='db', verbose=False)
        try:
            result = rag.query_similar('test query', top_k=1)
            
            logger.log(f'✅ RAG query successful: {(len(result) if result else 0)} results', 'INFO')
        except Exception as e:
            
            logger.log(f'❌ RAG query failed: {e}', 'INFO')
        
        logger.log(f'\nCircuit breaker status:', 'INFO')
        
        logger.log(json.dumps(rag.get_circuit_status(), indent=2), 'INFO')
        sys.exit(0)
    if args.test_llm:
        from llm_client import LLMMessage
        
        logger.log('Testing LLM with circuit breaker protection...', 'INFO')
        llm = ProtectedLLMClient('openai')
        try:
            response = llm.complete(messages=[LLMMessage(role='user', content="Say 'test'")], max_tokens=10)
            
            logger.log(f'✅ LLM call successful: {response.content[:50]}', 'INFO')
        except Exception as e:
            
            logger.log(f'❌ LLM call failed: {e}', 'INFO')
        
        logger.log(f'\nCircuit breaker status:', 'INFO')
        
        logger.log(json.dumps(llm.get_circuit_status(), indent=2), 'INFO')
        sys.exit(0)
    parser.print_help()