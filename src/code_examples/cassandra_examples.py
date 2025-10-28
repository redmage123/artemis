"""
Cassandra-specific code examples for RAG/KG population.

WHY:
Cassandra examples showcase data modeling for distributed, write-heavy workloads
with focus on partition key design and query patterns that avoid anti-patterns.

RESPONSIBILITY:
- Provide Cassandra data modeling best practices
- Demonstrate partition key and clustering key design for time-series data
- Show proper use of materialized views and counters
- Include TTL and compaction strategy configurations

PATTERNS:
- Focus on partition key design to avoid hot partitions
- Demonstrate time-series patterns with date-based partitioning
- Show proper use of ALLOW FILTERING (sparingly)
- Include SASI index examples for text search
"""

from code_example_types import CodeExample


CASSANDRA_EXAMPLES = [
    CodeExample(
        language="CQL",
        pattern="Cassandra Data Modeling",
        title="Time-Series Data Modeling for IoT Sensors",
        description="Cassandra data modeling optimized for write-heavy time-series queries",
        code='''-- Cassandra Time-Series Data Model for IoT Sensors
-- Why: Optimized for write-heavy workloads, time-based queries
-- Prevents: Hot partitions, slow range queries

-- Create keyspace with NetworkTopologyStrategy for production
CREATE KEYSPACE IF NOT EXISTS iot_data
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3  -- 3 replicas in datacenter1
};

USE iot_data;

-- Sensor readings table - partitioned by sensor and day
-- Why: Evenly distributes data, efficient time-range queries within partition
CREATE TABLE sensor_readings (
    sensor_id UUID,
    reading_date DATE,          -- Partition key component (distribution)
    reading_time TIMESTAMP,     -- Clustering key (ordering within partition)
    temperature DOUBLE,
    humidity DOUBLE,
    battery_level INT,
    PRIMARY KEY ((sensor_id, reading_date), reading_time)
) WITH CLUSTERING ORDER BY (reading_time DESC)  -- Newest first
AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_unit': 'DAYS', 'compaction_window_size': 1}
AND default_time_to_live = 2592000;  -- 30 days TTL (auto-delete old data)

-- Sensor metadata table (reference data, low cardinality)
CREATE TABLE sensors (
    sensor_id UUID PRIMARY KEY,
    location TEXT,
    type TEXT,
    install_date TIMESTAMP,
    metadata MAP<TEXT, TEXT>
);

-- Materialized view for querying by location
-- Why: Different query pattern (by location instead of sensor_id)
CREATE MATERIALIZED VIEW sensors_by_location AS
    SELECT sensor_id, location, type, install_date
    FROM sensors
    WHERE location IS NOT NULL AND sensor_id IS NOT NULL
    PRIMARY KEY (location, sensor_id);

-- Insert sensor reading (prepared statement - ALWAYS use these)
-- Application code:
INSERT INTO sensor_readings (
    sensor_id, reading_date, reading_time, temperature, humidity, battery_level
) VALUES (?, ?, ?, ?, ?, ?)
USING TTL 2592000;  -- 30 days
-- Parameters: sensor_id, current_date, current_timestamp, 72.5, 45.2, 85

-- Batch insert for same partition (good performance)
-- Why: All inserts go to same partition
BEGIN BATCH
INSERT INTO sensor_readings (sensor_id, reading_date, reading_time, temperature, humidity, battery_level)
    VALUES (?, ?, ?, ?, ?, ?);
INSERT INTO sensor_readings (sensor_id, reading_date, reading_time, temperature, humidity, battery_level)
    VALUES (?, ?, ?, ?, ?, ?);
-- ... more inserts for SAME sensor_id and reading_date
APPLY BATCH;

-- Query recent readings for a sensor (efficient - within partition)
SELECT temperature, humidity, reading_time
FROM sensor_readings
WHERE sensor_id = ?
  AND reading_date = ?
  AND reading_time >= ?
  AND reading_time <= ?
ORDER BY reading_time DESC
LIMIT 100;

-- Query across multiple days (multiple partitions - less efficient but necessary)
SELECT temperature, AVG(temperature) OVER (ORDER BY reading_time ROWS 10 PRECEDING)
FROM sensor_readings
WHERE sensor_id = ?
  AND reading_date IN (?, ?, ?);  -- List of dates

-- Aggregate query with GROUP BY (Cassandra 3.10+)
SELECT sensor_id, reading_date, AVG(temperature) as avg_temp, MAX(humidity) as max_humidity
FROM sensor_readings
WHERE sensor_id = ?
  AND reading_date IN (?, ?)
GROUP BY sensor_id, reading_date;

-- Create index on battery_level for low-battery queries
-- Note: Secondary indexes are expensive, use sparingly
CREATE INDEX ON sensor_readings (battery_level);

-- Query low-battery sensors (uses secondary index)
SELECT sensor_id, reading_date, reading_time, battery_level
FROM sensor_readings
WHERE battery_level < 20
LIMIT 100
ALLOW FILTERING;  -- Explicit acknowledgment of performance impact

-- Counter table for sensor statistics
CREATE TABLE sensor_stats (
    sensor_id UUID,
    stat_type TEXT,              -- 'readings_count', 'errors_count', etc.
    counter_value COUNTER,
    PRIMARY KEY (sensor_id, stat_type)
);

-- Increment counter (atomic operation)
UPDATE sensor_stats
SET counter_value = counter_value + 1
WHERE sensor_id = ?
  AND stat_type = 'readings_count';

-- Use SASI index for text search (better than secondary index for strings)
CREATE CUSTOM INDEX sensor_location_sasi ON sensors (location)
USING 'org.apache.cassandra.index.sasi.SASIIndex'
WITH OPTIONS = {'mode': 'CONTAINS', 'analyzer_class': 'org.apache.cassandra.index.sasi.analyzer.StandardAnalyzer'};

-- Query with SASI (supports LIKE)
SELECT sensor_id, location FROM sensors
WHERE location LIKE '%Building%';
''',
        quality_score=96,
        tags=["Cassandra", "CQL", "data-modeling", "time-series", "partitioning"],
        complexity="advanced",
        demonstrates=["Partition Key Design", "Clustering Keys", "TTL", "Materialized Views", "Counters"],
        prevents=["Hot Partitions", "Slow Range Queries", "Unbounded Queries"]
    ),
]
