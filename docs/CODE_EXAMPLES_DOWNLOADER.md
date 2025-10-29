# Artemis Code Examples Downloader

**Automated background service that continuously downloads high-quality code examples for all supported languages and build systems, storing them in the RAG database.**

---

## Overview

The Code Examples Downloader runs as a background daemon, continuously populating Artemis's RAG (Retrieval Augmented Generation) database with code examples from multiple sources:

- **GitHub**: Trending repositories, Awesome lists, popular projects
- **Rosetta Code**: Common algorithms in multiple languages
- **Official Documentation**: Framework examples
- **Language Playgrounds**: Beginner-friendly snippets

---

## Supported Languages & Build Systems

### JVM Ecosystem
- **Java**: Maven, Gradle, Ant
- **Kotlin**: Gradle, Maven
- **Scala**: SBT, Maven, Gradle

### JavaScript/TypeScript
- **JavaScript**: npm, yarn, pnpm
- **TypeScript**: npm, yarn, pnpm

### Python
- **Python**: pip, poetry, pipenv, conda

### Systems Languages
- **C/C++**: CMake, Make
- **Rust**: Cargo
- **Go**: Go modules
- **Zig**: Zig build

### Scripting Languages
- **Lua**: LuaRocks
- **Ruby**: Bundler, Gem
- **Perl**: CPAN
- **PHP**: Composer
- **Bash**: Shell scripts
- **PowerShell**: PowerShell modules

### .NET Ecosystem
- **C#**: dotnet, NuGet
- **F#**: dotnet, NuGet

### Functional Languages
- **Haskell**: Cabal, Stack
- **Elixir**: Mix
- **Erlang**: Rebar3
- **Clojure**: Leiningen, deps.edn

### Infrastructure
- **Terraform**: Terraform modules
- **Ansible**: Ansible playbooks

---

## Installation

### Option 1: Run Manually

```bash
cd /home/bbrelin/src/repos/artemis/src

# Run in foreground (for testing)
./start_code_downloader.sh --foreground

# Run in background
./start_code_downloader.sh

# Custom interval (every 2 hours)
./start_code_downloader.sh --interval 7200

# Limit examples per language
./start_code_downloader.sh --max-examples 50
```

### Option 2: Install as Systemd Service (Recommended)

```bash
cd /home/bbrelin/src/repos/artemis/src

# Install and start service
./start_code_downloader.sh --install-service

# Check status
sudo systemctl status artemis-code-downloader

# View live logs
sudo journalctl -u artemis-code-downloader -f

# Stop service
sudo systemctl stop artemis-code-downloader

# Restart service
sudo systemctl restart artemis-code-downloader
```

---

## Configuration

### Environment Variables

```bash
# GitHub API token (increases rate limit from 60 to 5000 requests/hour)
export GITHUB_TOKEN="your_github_token_here"

# Download directory (default: /tmp/artemis_examples)
export ARTEMIS_DOWNLOAD_DIR="/path/to/downloads"
```

### Command-Line Options

```bash
python3 code_examples_downloader.py \
  --interval 3600 \           # Update interval in seconds (default: 3600 = 1 hour)
  --max-examples 100 \        # Max examples per language (default: 100)
  --download-dir /tmp/examples \  # Temporary download directory
  --foreground                # Run in foreground (default: background daemon)
```

---

## How It Works

### Download Cycle

1. **Language Iteration**: Iterates through all supported languages
2. **Multi-Source Download**:
   - GitHub Awesome lists (curated resources)
   - GitHub trending repos (modern best practices)
   - Rosetta Code (algorithm implementations)
   - Official playgrounds (beginner examples)
3. **Quality Filtering**: Filters examples by quality score (≥0.7/1.0)
4. **Deduplication**: Removes duplicate examples
5. **RAG Storage**: Stores in vector database with metadata
6. **Sleep**: Waits for configured interval before next cycle

### Quality Scoring

Examples are scored based on:
- **Code clarity**: Comments, structure, readability
- **Best practices**: Modern patterns, error handling
- **Completeness**: Runnable, includes dependencies
- **Popularity**: Stars, forks, community engagement
- **Recency**: Updated within last 2 years

### Storage Format

Each example is stored with rich metadata:

```json
{
  "type": "code_example",
  "language": "python",
  "build_systems": ["pip", "poetry"],
  "title": "FastAPI REST API Example",
  "description": "Production-ready REST API with authentication",
  "source_url": "https://github.com/...",
  "tags": ["web", "api", "rest", "authentication"],
  "complexity": "intermediate",
  "quality_score": 0.92,
  "framework": "fastapi",
  "dependencies": ["fastapi", "uvicorn", "pydantic"],
  "ingested_at": "2025-10-26T12:00:00Z"
}
```

---

## Monitoring

### Check Statistics

```bash
# View logs
tail -f /tmp/artemis_logs/CodeExamplesDownloader.log

# For systemd service
sudo journalctl -u artemis-code-downloader -f
```

### Statistics Reported

- **Total examples downloaded**
- **Success rate** (successful / total)
- **Failed downloads** (with reasons)
- **Skipped examples** (duplicates, low quality)
- **Total storage size** (MB)
- **Elapsed time** (hours, minutes)

Example output:
```
📊 Download Statistics:
   Total examples: 2,450
   Successful: 2,380
   Failed: 45
   Skipped: 25
   Success rate: 98.1%
   Total size: 15.3 MB
   Elapsed time: 2h 15m
```

---

## GitHub Rate Limiting

### Without Token
- **60 requests/hour** (very limited)
- Only suitable for light testing

### With Token
- **5,000 requests/hour** (recommended for production)

### Generate Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `public_repo`, `read:org`
4. Copy token and set environment variable:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

Or add to systemd service:
```bash
sudo nano /etc/systemd/system/artemis-code-downloader.service

# Add under [Service]:
Environment="GITHUB_TOKEN=ghp_your_token_here"

# Reload
sudo systemctl daemon-reload
sudo systemctl restart artemis-code-downloader
```

---

## Troubleshooting

### Check if Running

```bash
# For background process
ps aux | grep code_examples_downloader

# For systemd service
sudo systemctl status artemis-code-downloader
```

### Common Issues

**1. Rate limit exceeded**
```
Solution: Set GITHUB_TOKEN environment variable
```

**2. Permission denied on /var/log/artemis**
```
Solution: Downloader automatically falls back to /tmp/artemis_logs
```

**3. RAG database connection failed**
```
Solution: Ensure RAG storage helper is configured correctly
Check: rag_storage_helper.py configuration
```

**4. Out of disk space**
```
Solution: Downloads are temporary - check /tmp/artemis_examples
Clean up: rm -rf /tmp/artemis_examples/*
```

---

## Resource Usage

### Typical Usage
- **CPU**: 5-10% during downloads, <1% while sleeping
- **Memory**: 200-500 MB (depends on example size)
- **Network**: 10-50 MB/hour (depends on interval)
- **Disk**: ~100 MB temporary (cleared after RAG storage)

### Systemd Resource Limits
The service file includes:
- **Memory limit**: 2 GB
- **CPU quota**: 50% (half of one core)

---

## Advanced Usage

### Custom Source Integration

Add your own download sources by extending the downloader:

```python
from code_examples_downloader import CodeExamplesDownloader

class CustomDownloader(CodeExamplesDownloader):
    def _download_from_custom_source(self, language: str):
        # Your custom download logic
        pass
```

### Filtering Customization

Adjust quality thresholds:

```python
def _filter_quality(self, examples):
    # Custom filtering logic
    return [ex for ex in examples if ex.quality_score >= 0.85]
```

---

## Performance Tuning

### For Low-Resource Systems
```bash
# Longer interval (4 hours)
# Fewer examples (50 per language)
./start_code_downloader.sh --interval 14400 --max-examples 50
```

### For High-Throughput Systems
```bash
# Shorter interval (30 minutes)
# More examples (200 per language)
./start_code_downloader.sh --interval 1800 --max-examples 200
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│          Code Examples Downloader Daemon            │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │         Download Sources                    │    │
│  │  • GitHub Trending                         │    │
│  │  • GitHub Awesome Lists                    │    │
│  │  • Rosetta Code                            │    │
│  │  • Official Playgrounds                    │    │
│  └────────────────────────────────────────────┘    │
│                     ↓                                │
│  ┌────────────────────────────────────────────┐    │
│  │         Quality Filtering                   │    │
│  │  • Score >= 0.7                            │    │
│  │  • Deduplication                           │    │
│  │  • Limit per language                      │    │
│  └────────────────────────────────────────────┘    │
│                     ↓                                │
│  ┌────────────────────────────────────────────┐    │
│  │         RAG Storage                         │    │
│  │  • Vector embeddings                       │    │
│  │  • Metadata indexing                       │    │
│  │  • Semantic search                         │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
                      ↓
         Available for code generation
         via RAG retrieval
```

---

## License

Part of the Artemis Autonomous Pipeline
MIT License

---

## Support

- **Issues**: https://github.com/artemis-ai/artemis/issues
- **Documentation**: https://docs.artemis-ai.dev
- **Logs**: `/tmp/artemis_logs/CodeExamplesDownloader.log`
