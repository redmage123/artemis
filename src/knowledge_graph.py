from artemis_logger import get_logger
logger = get_logger('knowledge_graph')
'\nBACKWARD COMPATIBILITY WRAPPER\n\nWHY: Maintain existing imports while code transitions to new package\nRESPONSIBILITY: Re-export all public APIs from knowledge_graph_pkg\nPATTERNS: Facade pattern - transparent delegation to new package\n\nThis file maintains backward compatibility with existing code.\nAll functionality has been moved to knowledge_graph_pkg/.\n\nOriginal file was 968 lines. Now refactored into modular package:\n- models.py (101 lines) - Data models\n- graph_operations.py (421 lines) - Node creation operations\n- query_operations.py (185 lines) - Query operations\n- relationship_operations.py (174 lines) - Relationship operations\n- storage_operations.py (89 lines) - Storage/persistence operations\n- query_builder.py (226 lines) - Query builders\n- knowledge_graph.py (270 lines) - Main orchestrator\n- __init__.py (54 lines) - Package exports\n\nTotal: ~1,520 lines (with documentation and proper separation)\nReduction: 968 lines -> package structure with clear responsibilities\n\nUsage (backward compatible):\n    from knowledge_graph import KnowledgeGraph, CodeFile, ADR\n    graph = KnowledgeGraph()\n    graph.add_file("auth.py", language="python")\n\nNew usage (recommended):\n    from knowledge_graph_pkg import KnowledgeGraph, CodeFile, ADR\n    graph = KnowledgeGraph()\n    graph.add_file("auth.py", language="python")\n'
from knowledge_graph_pkg import *
from knowledge_graph_pkg import KnowledgeGraph, MEMGRAPH_AVAILABLE, CodeFile, CodeClass, CodeFunction, ADR, Requirement, Task, CodeReview, GraphOperations, QueryOperations, RelationshipOperations, StorageOperations, QueryBuilder, CypherQueryTemplates
__all__ = ['KnowledgeGraph', 'MEMGRAPH_AVAILABLE', 'CodeFile', 'CodeClass', 'CodeFunction', 'ADR', 'Requirement', 'Task', 'CodeReview', 'GraphOperations', 'QueryOperations', 'RelationshipOperations', 'StorageOperations', 'QueryBuilder', 'CypherQueryTemplates']
if __name__ == '__main__':
    graph = KnowledgeGraph(host='localhost', port=7687)
    
    logger.log('🔧 Testing Knowledge Graph with GraphQL-style operations\n', 'INFO')
    
    logger.log('Adding files...', 'INFO')
    graph.add_file('auth.py', 'python', lines=250, module='api')
    graph.add_file('database.py', 'python', lines=180, module='data')
    graph.add_file('api.py', 'python', lines=320, module='api')
    
    logger.log('Adding dependencies...', 'INFO')
    graph.add_dependency('api.py', 'auth.py', 'IMPORTS')
    graph.add_dependency('api.py', 'database.py', 'IMPORTS')
    graph.add_dependency('auth.py', 'database.py', 'IMPORTS')
    
    logger.log('Adding classes and functions...', 'INFO')
    graph.add_class('UserService', 'auth.py', public=True, lines=80)
    graph.add_function('login', 'auth.py', class_name='UserService', params=['username', 'password'], returns='Token')
    
    logger.log('\n📊 Impact Analysis for database.py:', 'INFO')
    impacts = graph.get_impact_analysis('database.py', depth=2)
    for impact in impacts:
        
        logger.log(f"  - {impact['dependent_path']} (distance: {impact['distance']})", 'INFO')
    
    logger.log('\n🔗 Dependencies for api.py:', 'INFO')
    deps = graph.get_file_dependencies('api.py')
    
    logger.log(f"  Imports: {deps['imports']}", 'INFO')
    
    logger.log(f"  Imported by: {deps['imported_by']}", 'INFO')
    
    logger.log('\n📈 Graph Statistics:', 'INFO')
    stats = graph.get_graph_stats()
    for key, value in stats.items():
        
        logger.log(f'  {key}: {value}', 'INFO')
    
    logger.log('\n✅ Knowledge Graph test complete!', 'INFO')