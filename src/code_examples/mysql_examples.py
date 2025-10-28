"""
MySQL-specific code examples for RAG/KG population.

WHY:
MySQL examples demonstrate InnoDB optimizations, utf8mb4 encoding for emoji support,
and JSON functions available in modern MySQL versions.

RESPONSIBILITY:
- Provide MySQL InnoDB best practices
- Demonstrate utf8mb4 character set configuration
- Show JSON column usage with generated columns for indexing
- Include full-text search and partitioning strategies

PATTERNS:
- Always use utf8mb4 for proper Unicode support
- Use generated columns to index JSON fields
- Demonstrate UPSERT with ON DUPLICATE KEY UPDATE
- Show partitioning for large table management
"""

from code_example_types import CodeExample


MYSQL_EXAMPLES = [
    CodeExample(
        language="SQL",
        pattern="MySQL InnoDB Optimization",
        title="Optimized InnoDB Table Design with utf8mb4",
        description="MySQL InnoDB best practices including utf8mb4, JSON functions, and partitioning",
        code='''-- MySQL InnoDB Best Practices
-- Why: Emoji support, ACID compliance, proper indexing
-- Prevents: Character encoding issues, slow queries, data loss

-- Set proper character set (supports emojis)
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create table with InnoDB engine
CREATE TABLE posts (
    post_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    title VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    content TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    tags JSON,  -- MySQL 5.7+ JSON type
    metadata JSON,
    view_count INT UNSIGNED DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_view_count (view_count),
    FULLTEXT INDEX idx_content_fulltext (title, content) WITH PARSER ngram
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  ROW_FORMAT=DYNAMIC;

-- JSON functions (MySQL 5.7+)
-- Insert with JSON data (use parameterized queries in application)
INSERT INTO posts (user_id, title, content, tags, metadata)
VALUES (
    ?,
    ?,
    ?,
    JSON_ARRAY('mysql', 'database', 'tutorial'),
    JSON_OBJECT('category', 'tutorial', 'difficulty', 'beginner')
);

-- Query JSON fields
SELECT post_id, title, JSON_EXTRACT(tags, '$[0]') as first_tag
FROM posts
WHERE JSON_CONTAINS(tags, '"mysql"');

-- Use generated columns for JSON indexing (MySQL 5.7+)
ALTER TABLE posts
ADD COLUMN category VARCHAR(50)
AS (JSON_UNQUOTE(JSON_EXTRACT(metadata, '$.category'))) STORED,
ADD INDEX idx_category (category);

-- Now can efficiently query by category
SELECT post_id, title, category
FROM posts
WHERE category = 'tutorial';

-- UPSERT using INSERT ... ON DUPLICATE KEY UPDATE
INSERT INTO posts (post_id, user_id, title, content, tags)
VALUES (?, ?, ?, ?, ?)
ON DUPLICATE KEY UPDATE
    title = VALUES(title),
    content = VALUES(content),
    tags = VALUES(tags),
    updated_at = CURRENT_TIMESTAMP;

-- Full-text search
SELECT post_id, title,
       MATCH(title, content) AGAINST (? IN NATURAL LANGUAGE MODE) as relevance_score
FROM posts
WHERE MATCH(title, content) AGAINST (? IN NATURAL LANGUAGE MODE)
ORDER BY relevance_score DESC
LIMIT 20;

-- Partitioning for large tables (by date range)
CREATE TABLE posts_partitioned (
    post_id BIGINT UNSIGNED AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    title VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    content TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, created_at)
) ENGINE=InnoDB
PARTITION BY RANGE (UNIX_TIMESTAMP(created_at)) (
    PARTITION p2024_q1 VALUES LESS THAN (UNIX_TIMESTAMP('2024-04-01')),
    PARTITION p2024_q2 VALUES LESS THAN (UNIX_TIMESTAMP('2024-07-01')),
    PARTITION p2024_q3 VALUES LESS THAN (UNIX_TIMESTAMP('2024-10-01')),
    PARTITION p2024_q4 VALUES LESS THAN (UNIX_TIMESTAMP('2025-01-01')),
    PARTITION p2025_q1 VALUES LESS THAN (UNIX_TIMESTAMP('2025-04-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- Explain query to verify index usage
EXPLAIN SELECT post_id, title FROM posts
WHERE user_id = ? AND created_at >= ?
ORDER BY created_at DESC LIMIT 10;
''',
        quality_score=93,
        tags=["MySQL", "InnoDB", "utf8mb4", "JSON", "partitioning", "full-text-search"],
        complexity="intermediate",
        demonstrates=["utf8mb4 Encoding", "JSON Functions", "Generated Columns", "Full-Text Search", "Partitioning"],
        prevents=["Character Encoding Issues", "Slow JSON Queries", "Table Scans"]
    ),
]
