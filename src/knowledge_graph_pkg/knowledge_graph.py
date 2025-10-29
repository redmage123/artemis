from artemis_logger import get_logger
logger = get_logger('knowledge_graph')
'\nWHY: Main orchestrator for knowledge graph operations\nRESPONSIBILITY: Coordinate all graph operations through delegation\nPATTERNS: Facade pattern - provide simple interface to complex subsystems\n\nThis is the main entry point for knowledge graph functionality.\nIt delegates to specialized operation classes.\n'
from typing import Dict, List, Optional, Any
try:
    from gqlalchemy import Memgraph
    MEMGRAPH_AVAILABLE = True
except ImportError:
    MEMGRAPH_AVAILABLE = False
    
    logger.log('ℹ️  Info: Memgraph knowledge graph features disabled (gqlalchemy library not available)', 'INFO')
from .graph_operations import GraphOperations
from .query_operations import QueryOperations
from .relationship_operations import RelationshipOperations
from .storage_operations import StorageOperations
from .query_builder import QueryBuilder, CypherQueryTemplates

class KnowledgeGraph:
    """
    WHY: Provide unified interface to knowledge graph functionality
    RESPONSIBILITY: Orchestrate operations across specialized modules
    PATTERNS: Facade pattern - delegates to operation classes

    Main orchestrator that provides:
    - Dependency tracking
    - Impact analysis
    - Architectural validation
    - Decision lineage
    - Multi-hop queries
    """

    def __init__(self, host: str='localhost', port: int=7687):
        """
        Initialize connection to Memgraph

        WHY: Centralize connection management and setup

        Args:
            host: Memgraph host
            port: Memgraph port (default: 7687)

        Raises:
            ImportError: If gqlalchemy not installed
        """
        if not MEMGRAPH_AVAILABLE:
            raise ImportError('gqlalchemy not installed. Run: pip install gqlalchemy')
        self.db = Memgraph(host=host, port=port)
        self._connected = False
        try:
            self._storage_ops = StorageOperations(self.db)
            self._storage_ops.create_indexes()
            self._graph_ops = GraphOperations(self.db)
            self._query_ops = QueryOperations(self.db)
            self._rel_ops = RelationshipOperations(self.db)
            self._connected = True
        except Exception:
            pass

    def query(self, cypher_query: str, params: Optional[Dict]=None) -> List[Dict]:
        """
        Execute a Cypher query and return results

        WHY: Allow custom queries for advanced use cases

        Args:
            cypher_query: Cypher query string
            params: Optional query parameters

        Returns:
            Query results from execute_and_fetch, or empty list if not connected
        """
        if not self._connected:
            return []
        try:
            results = list(self.db.execute_and_fetch(cypher_query, params or {}))
            return results
        except Exception:
            self._connected = False
            return []

    def add_file(self, path: str, language: str, lines: int=0, module: Optional[str]=None) -> str:
        """Add a code file to the graph. See GraphOperations.add_file for details."""
        return self._graph_ops.add_file(path, language, lines, module)

    def add_class(self, name: str, file_path: str, public: bool=True, abstract: bool=False, lines: int=0) -> str:
        """Add a class to the graph. See GraphOperations.add_class for details."""
        return self._graph_ops.add_class(name, file_path, public, abstract, lines)

    def add_function(self, name: str, file_path: str, class_name: Optional[str]=None, params: Optional[List[str]]=None, returns: Optional[str]=None, public: bool=True, complexity: int=1) -> str:
        """Add a function to the graph. See GraphOperations.add_function for details."""
        return self._graph_ops.add_function(name, file_path, class_name, params, returns, public, complexity)

    def add_adr(self, adr_id: str, title: str, status: str, rationale: Optional[str]=None, impacts: Optional[List[str]]=None) -> str:
        """Add an ADR to the graph. See GraphOperations.add_adr for details."""
        return self._graph_ops.add_adr(adr_id, title, status, rationale, impacts)

    def add_requirement(self, req_id: str, title: str, type: str, priority: str, status: str='active') -> str:
        """Add a requirement to the graph. See GraphOperations.add_requirement for details."""
        return self._graph_ops.add_requirement(req_id, title, type, priority, status)

    def add_task(self, card_id: str, title: str, priority: str, status: str, assigned_agents: Optional[List[str]]=None) -> str:
        """Add a task to the graph. See GraphOperations.add_task for details."""
        return self._graph_ops.add_task(card_id, title, priority, status, assigned_agents)

    def add_code_review(self, review_id: str, card_id: str, status: str, score: int, critical_issues: int=0, high_issues: int=0) -> str:
        """Add a code review to the graph. See GraphOperations.add_code_review for details."""
        return self._graph_ops.add_code_review(review_id, card_id, status, score, critical_issues, high_issues)

    def update_file_metrics(self, file_path: str, lines: int, complexity: Optional[int]=None) -> bool:
        """Update file metrics. See GraphOperations.update_file_metrics for details."""
        return self._graph_ops.update_file_metrics(file_path, lines, complexity)

    def delete_file(self, file_path: str) -> bool:
        """Delete a file. See GraphOperations.delete_file for details."""
        return self._graph_ops.delete_file(file_path)

    def add_dependency(self, from_file: str, to_file: str, relationship: str='IMPORTS') -> None:
        """Add a dependency. See RelationshipOperations.add_dependency for details."""
        self._rel_ops.add_dependency(from_file, to_file, relationship)

    def add_function_call(self, caller: str, callee: str, caller_file: str, callee_file: str) -> None:
        """Add a function call. See RelationshipOperations.add_function_call for details."""
        self._rel_ops.add_function_call(caller, callee, caller_file, callee_file)

    def link_requirement_to_adr(self, req_id: str, adr_id: str) -> None:
        """Link requirement to ADR. See RelationshipOperations.link_requirement_to_adr for details."""
        self._rel_ops.link_requirement_to_adr(req_id, adr_id)

    def link_requirement_to_task(self, req_id: str, card_id: str) -> None:
        """Link requirement to task. See RelationshipOperations.link_requirement_to_task for details."""
        self._rel_ops.link_requirement_to_task(req_id, card_id)

    def link_adr_to_file(self, adr_id: str, file_path: str, relationship: str='IMPLEMENTED_BY') -> None:
        """Link ADR to file. See RelationshipOperations.link_adr_to_file for details."""
        self._rel_ops.link_adr_to_file(adr_id, file_path, relationship)

    def link_task_to_file(self, card_id: str, file_path: str) -> None:
        """Link task to file. See RelationshipOperations.link_task_to_file for details."""
        self._rel_ops.link_task_to_file(card_id, file_path)

    def get_file(self, path: str) -> Optional[Dict]:
        """Get file details. See QueryOperations.get_file for details."""
        return self._query_ops.get_file(path)

    def get_impact_analysis(self, file_path: str, depth: int=3) -> List[Dict]:
        """Get impact analysis. See QueryOperations.get_impact_analysis for details."""
        return self._query_ops.get_impact_analysis(file_path, depth)

    def get_circular_dependencies(self) -> List[Dict]:
        """Get circular dependencies. See QueryOperations.get_circular_dependencies for details."""
        return self._query_ops.get_circular_dependencies()

    def get_untested_functions(self) -> List[Dict]:
        """Get untested functions. See QueryOperations.get_untested_functions for details."""
        return self._query_ops.get_untested_functions()

    def get_decision_lineage(self, adr_id: str) -> List[Dict]:
        """Get decision lineage. See QueryOperations.get_decision_lineage for details."""
        return self._query_ops.get_decision_lineage(adr_id)

    def get_architectural_violations(self, forbidden_patterns: List[tuple]) -> List[Dict]:
        """Get architectural violations. See QueryOperations.get_architectural_violations for details."""
        return self._query_ops.get_architectural_violations(forbidden_patterns)

    def get_file_dependencies(self, file_path: str) -> Dict[str, List[str]]:
        """Get file dependencies. See QueryOperations.get_file_dependencies for details."""
        return self._query_ops.get_file_dependencies(file_path)

    def get_graph_stats(self) -> Dict[str, int]:
        """Get graph statistics. See QueryOperations.get_graph_stats for details."""
        return self._query_ops.get_graph_stats()

    def clear_all(self) -> None:
        """Clear entire graph. See StorageOperations.clear_all for details."""
        self._storage_ops.clear_all()

    def export_to_json(self, output_path: str) -> None:
        """Export to JSON. See StorageOperations.export_to_json for details."""
        self._storage_ops.export_to_json(output_path)
__all__ = ['KnowledgeGraph', 'MEMGRAPH_AVAILABLE']