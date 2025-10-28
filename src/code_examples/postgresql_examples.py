"""
PostgreSQL-specific code examples for RAG/KG population.

WHY:
PostgreSQL examples showcase advanced features like JSONB indexing, window functions,
and full-text search that are critical for modern application development.

RESPONSIBILITY:
- Provide production-quality PostgreSQL code patterns
- Demonstrate advanced PostgreSQL features (JSONB, window functions, CTEs)
- Include performance optimization strategies (GIN indexes, partial indexes)
- Show proper parameterization to prevent SQL injection

PATTERNS:
- Each example includes WHY/PREVENTS documentation
- Focuses on PostgreSQL-specific features not available in standard SQL
- Emphasizes performance optimization and query efficiency
- Includes realistic use cases (user preferences, analytics)
"""

from code_example_types import CodeExample


POSTGRESQL_EXAMPLES = [
    CodeExample(
        language="SQL",
        pattern="PostgreSQL JSONB Indexing",
        title="JSONB Query Optimization with GIN Index",
        description="Using PostgreSQL's JSONB type with proper indexing for semi-structured data",
        code='''-- User preferences stored as JSONB with optimal indexing
-- Why: Flexible schema for user preferences, fast queries
-- Prevents: Full table scans, slow JSON queries

CREATE TABLE user_preferences (
    user_id BIGINT PRIMARY KEY,
    preferences JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- GIN index for JSONB containment queries (@> operator)
CREATE INDEX idx_user_preferences_jsonb
ON user_preferences USING GIN (preferences);

-- Partial index for specific preference keys (more efficient)
CREATE INDEX idx_user_preferences_theme
ON user_preferences ((preferences->>'theme'))
WHERE preferences ? 'theme';

-- Insert user preferences (parameterized - prevent SQL injection)
INSERT INTO user_preferences (user_id, preferences)
VALUES ($1, $2::jsonb)
ON CONFLICT (user_id)
DO UPDATE SET
    preferences = user_preferences.preferences || EXCLUDED.preferences,
    updated_at = CURRENT_TIMESTAMP;
-- Example: $1 = 123, $2 = '{"theme": "dark", "language": "en"}'

-- Query users with specific preference (uses GIN index)
SELECT user_id, preferences
FROM user_preferences
WHERE preferences @> '{"theme": "dark"}'::jsonb;

-- Query with nested JSON path (PostgreSQL 12+)
SELECT user_id, preferences->'notifications'->>'email' as email_pref
FROM user_preferences
WHERE preferences @> '{"notifications": {"email": "enabled"}}'::jsonb;

-- Aggregate JSONB data
SELECT
    preferences->>'theme' as theme,
    COUNT(*) as user_count
FROM user_preferences
WHERE preferences ? 'theme'
GROUP BY preferences->>'theme'
ORDER BY user_count DESC;

-- Update nested JSONB using jsonb_set (immutable operation)
UPDATE user_preferences
SET preferences = jsonb_set(
    preferences,
    '{notifications,email}',
    '"disabled"'::jsonb,
    true  -- create_missing
)
WHERE user_id = $1;

-- Full-text search on JSONB text values
CREATE INDEX idx_user_preferences_fts
ON user_preferences USING GIN (
    to_tsvector('english', preferences::text)
);

SELECT user_id
FROM user_preferences
WHERE to_tsvector('english', preferences::text) @@ to_tsquery('dark & mode');
''',
        quality_score=96,
        tags=["PostgreSQL", "JSONB", "indexing", "GIN", "full-text-search"],
        complexity="advanced",
        demonstrates=["JSONB Queries", "GIN Indexing", "Partial Indexes", "Upsert", "Full-Text Search"],
        prevents=["Full Table Scans", "SQL Injection", "Slow JSON Queries"]
    ),

    CodeExample(
        language="SQL",
        pattern="PostgreSQL Window Functions",
        title="Running Totals and Rankings with Window Functions",
        description="Using PostgreSQL window functions for analytics without self-joins",
        code='''-- Order analytics using window functions
-- Why: Avoid expensive self-joins, get running totals and rankings
-- Prevents: N+1 queries, performance issues

-- Create sample table
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL
);

-- Running total per user (OVER clause)
SELECT
    order_id,
    user_id,
    amount,
    SUM(amount) OVER (
        PARTITION BY user_id
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total
FROM orders
WHERE status = 'completed'
ORDER BY user_id, order_date;

-- Rank orders within each user (ROW_NUMBER, RANK, DENSE_RANK)
SELECT
    order_id,
    user_id,
    amount,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY amount DESC) as row_num,
    RANK() OVER (PARTITION BY user_id ORDER BY amount DESC) as rank,
    DENSE_RANK() OVER (PARTITION BY user_id ORDER BY amount DESC) as dense_rank
FROM orders;

-- Compare with previous/next row (LAG/LEAD)
SELECT
    order_id,
    user_id,
    amount,
    order_date,
    LAG(amount) OVER (PARTITION BY user_id ORDER BY order_date) as prev_amount,
    LEAD(amount) OVER (PARTITION BY user_id ORDER BY order_date) as next_amount,
    amount - LAG(amount) OVER (PARTITION BY user_id ORDER BY order_date) as amount_change
FROM orders;

-- Moving average (3-order window)
SELECT
    order_id,
    user_id,
    amount,
    AVG(amount) OVER (
        PARTITION BY user_id
        ORDER BY order_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as moving_avg_3
FROM orders;

-- Percentiles and quartiles
SELECT
    user_id,
    amount,
    NTILE(4) OVER (ORDER BY amount) as quartile,
    PERCENT_RANK() OVER (ORDER BY amount) as percent_rank,
    CUME_DIST() OVER (ORDER BY amount) as cumulative_dist
FROM orders;

-- First and last value in partition
SELECT
    order_id,
    user_id,
    amount,
    FIRST_VALUE(amount) OVER (
        PARTITION BY user_id ORDER BY order_date
    ) as first_order_amount,
    LAST_VALUE(amount) OVER (
        PARTITION BY user_id ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) as last_order_amount
FROM orders;
''',
        quality_score=94,
        tags=["PostgreSQL", "window-functions", "analytics", "ranking", "running-totals"],
        complexity="advanced",
        demonstrates=["Window Functions", "PARTITION BY", "LAG/LEAD", "ROW_NUMBER", "Running Totals"],
        prevents=["Self-Joins", "Subqueries", "Performance Issues"]
    ),
]
