"""
Code examples package for RAG/KG population.

WHY:
Provides comprehensive, production-quality code examples for various database technologies
to populate knowledge graphs and assist with code generation tasks.

RESPONSIBILITY:
- Organize database-specific code examples by technology
- Maintain high-quality, annotated examples for RAG ingestion
- Support multiple database paradigms (SQL, NoSQL, key-value, document, graph)

PATTERNS:
- Each module represents a specific database technology
- Examples include WHY/PREVENTS documentation for learning
- Quality scores and tags enable intelligent example selection
- Complexity ratings help match examples to user skill level
"""

from code_examples.postgresql_examples import POSTGRESQL_EXAMPLES
from code_examples.mongodb_examples import MONGODB_EXAMPLES
from code_examples.cassandra_examples import CASSANDRA_EXAMPLES
from code_examples.mysql_examples import MYSQL_EXAMPLES
from code_examples.redis_examples import REDIS_EXAMPLES
from code_examples.dynamodb_examples import DYNAMODB_EXAMPLES

__all__ = [
    "POSTGRESQL_EXAMPLES",
    "MONGODB_EXAMPLES",
    "CASSANDRA_EXAMPLES",
    "MYSQL_EXAMPLES",
    "REDIS_EXAMPLES",
    "DYNAMODB_EXAMPLES",
    "ALL_DATABASE_EXAMPLES",
]

# Export consolidated dictionary
ALL_DATABASE_EXAMPLES = {
    "PostgreSQL": POSTGRESQL_EXAMPLES,
    "MongoDB": MONGODB_EXAMPLES,
    "Cassandra": CASSANDRA_EXAMPLES,
    "MySQL": MYSQL_EXAMPLES,
    "Redis": REDIS_EXAMPLES,
    "DynamoDB": DYNAMODB_EXAMPLES,
}
