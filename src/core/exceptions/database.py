#!/usr/bin/env python3
"""
Module: core/exceptions/database.py

WHY: Centralizes all database-related exceptions (RAG, Redis, Knowledge Graph).
     Before modularization, database exceptions were mixed with other exception types.
     This module isolates database concerns for better organization and discoverability.

RESPONSIBILITY: Define database-specific exception types for RAG, Redis, and Knowledge Graph.
                Single Responsibility - only database exceptions, nothing else.

PATTERNS: Exception Hierarchy Pattern, Category Grouping Pattern
          - Hierarchy: Base classes (RAGException, RedisException) with specific subtypes
          - Grouping: All database exceptions in one place for easy discovery

Integration: Used by rag_agent.py, ai_query_service.py, knowledge_graph.py, and
             any component that interacts with databases or caching layers.
"""

from core.exceptions.base import ArtemisException


# ============================================================================
# RAG DATABASE EXCEPTIONS
# ============================================================================

class RAGException(ArtemisException):
    """
    Base exception for RAG-related errors.

    WHY: Enables catching all RAG errors with single except clause.
         Distinguishes RAG errors from other database types (Redis, KG).

    RESPONSIBILITY: Base class for RAG database operations (query, storage, connection).

    Use case:
        try:
            rag_query()
        except RAGException as e:  # Catches all RAG errors
            handle_rag_error(e)
    """
    pass


# Alias for compatibility with AIQueryService
RAGError = RAGException


class RAGQueryError(RAGException):
    """
    Error querying RAG database.

    WHY: Specific error type for query operations. Enables targeted error
         handling (retry query vs reconnect vs fail).

    Example context:
        {"query": "search term", "collection": "code_examples", "limit": 10}
    """
    pass


class RAGStorageError(RAGException):
    """
    Error storing data in RAG database.

    WHY: Distinguishes storage failures from query failures. Storage errors
         may indicate disk space, permissions, or schema issues.

    Example context:
        {"document_count": 100, "collection": "requirements", "size_mb": 50}
    """
    pass


class RAGConnectionError(RAGException):
    """
    Error connecting to RAG database (ChromaDB).

    WHY: Connection errors require different handling (retry, fallback, alert).
         Separates connection issues from query/storage logic errors.

    Example context:
        {"host": "localhost", "port": 8000, "timeout": 30, "attempt": 3}
    """
    pass


# ============================================================================
# REDIS CACHE EXCEPTIONS
# ============================================================================

class RedisException(ArtemisException):
    """
    Base exception for Redis-related errors.

    WHY: Enables catching all Redis cache errors. Redis is used for
         session state, caching, and distributed locking.

    RESPONSIBILITY: Base class for Redis operations (connection, cache ops).

    Use case:
        try:
            cache.get(key)
        except RedisException as e:  # Catches all Redis errors
            use_fallback_storage()
    """
    pass


class RedisConnectionError(RedisException):
    """
    Error connecting to Redis.

    WHY: Connection errors need immediate attention. May indicate Redis down,
         network issues, or configuration problems.

    Example context:
        {"host": "redis.local", "port": 6379, "db": 0, "timeout": 5}
    """
    pass


class RedisCacheError(RedisException):
    """
    Error performing Redis cache operation.

    WHY: Distinguishes cache operation errors (set, get, delete) from
         connection errors. May indicate memory limits or data serialization issues.

    Example context:
        {"operation": "set", "key": "session:123", "value_size": 1024}
    """
    pass


# ============================================================================
# KNOWLEDGE GRAPH EXCEPTIONS
# ============================================================================

class KnowledgeGraphError(ArtemisException):
    """
    Base exception for Knowledge Graph errors.

    WHY: Knowledge Graph stores project relationships, dependencies, and
         architectural decisions. Separate from RAG (document storage) and
         Redis (cache).

    RESPONSIBILITY: Base class for Knowledge Graph operations (query, connection).

    Use case:
        try:
            kg.query_dependencies()
        except KnowledgeGraphError as e:  # Catches all KG errors
            log_kg_error(e)
    """
    pass


class KGQueryError(KnowledgeGraphError):
    """
    Error executing Knowledge Graph query.

    WHY: Query errors may indicate Cypher syntax issues, graph corruption,
         or missing nodes/relationships.

    Example context:
        {"query": "MATCH (n)-[r]->(m)", "params": {"id": "123"}, "type": "cypher"}
    """
    pass


class KGConnectionError(KnowledgeGraphError):
    """
    Error connecting to Knowledge Graph database.

    WHY: Connection errors need different handling than query errors.
         May indicate Neo4j down or network issues.

    Example context:
        {"host": "neo4j.local", "port": 7687, "timeout": 10, "attempt": 2}
    """
    pass
