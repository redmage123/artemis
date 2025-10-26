# Artemis - AI-Powered Agile Development Pipeline

**Artemis** is an autonomous multi-agent system for software development that implements agile methodologies including TDD, BDD, code review, sprint planning, and project management workflows.

## Overview

Artemis orchestrates multiple AI developer agents to collaboratively build software following industry best practices:

- **Requirements-Driven Development**: Automatically analyzes requirements to select appropriate workflows
- **Multi-Developer Arbitration**: Multiple agents compete to produce the best solution
- **TDD & Quality-Driven Workflows**: Automated RED-GREEN-REFACTOR cycles and quality validation
- **Knowledge Graph Integration**: Tracks project knowledge and relationships
- **RAG-Powered Code Generation**: Leverages vector database for context-aware code generation
- **Checkpoint-Based State Management**: Resume workflows from any point

## Features

### Agent Types
- **Supervisor Agent**: Orchestrates multi-agent workflows and learning
- **Developer Agents**: Generate code using TDD or quality-driven workflows
- **Code Review Agent**: Analyzes code quality and suggests improvements
- **Project Analysis Agent**: Analyzes requirements and project structure
- **RAG Agent**: Retrieves relevant code examples and documentation
- **Retrospective Agent**: Analyzes completed sprints and suggests improvements

### Workflows
1. **Sprint Planning**: Planning poker for effort estimation
2. **Requirements Analysis**: Parse and validate requirements
3. **Development**: TDD (RED-GREEN-REFACTOR) or Quality-Driven (EXTRACT-GENERATE-VALIDATE-ENHANCE)
4. **Code Review**: Multi-agent code review with configurable reviewers
5. **BDD Testing**: Scenario generation and validation
6. **Project Review**: Comprehensive project analysis and reporting
7. **Retrospective**: Sprint retrospective with actionable insights

### Quality Validation
- **Artifact-Specific Validators**: Jupyter notebooks, code files, UI artifacts
- **WCAG Compliance**: Accessibility validation for UI components
- **GDPR Compliance**: Privacy and data protection checks
- **Build System Integration**: Maven, Gradle, npm, pip, cargo, and more

## Architecture

```
artemis/
├── src/                          # Source code
│   ├── artemis_orchestrator.py   # Main orchestrator
│   ├── supervisor_agent.py       # Supervisor agent
│   ├── standalone_developer_agent.py  # Developer agent
│   ├── code_review_agent.py      # Code review agent
│   ├── rag_agent.py              # RAG agent
│   ├── knowledge_graph.py        # Knowledge graph
│   ├── artemis_stages.py         # Pipeline stages
│   ├── conf/                     # Hydra configuration
│   ├── prompts/                  # Agent prompts
│   └── stages/                   # Modular stage implementations
├── .artemis_data/                # Runtime data (gitignored)
│   ├── developer_output/         # Generated artifacts
│   ├── code_reviews/             # Code review outputs
│   ├── rag_db/                   # RAG vector database
│   └── logs/                     # Execution logs
├── docs/                         # Documentation
├── output/                       # Output files
├── .gitignore                    # Git ignore patterns
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Installation

### Prerequisites
- Python 3.10+
- Neo4j (optional, for knowledge graph)
- Anthropic API key or OpenAI API key

### Setup

1. **Clone the repository:**
```bash
cd /home/bbrelin/src/repos/artemis
```

2. **Create virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cd src
cp .env.example .env
# Edit .env and add your API keys:
# ANTHROPIC_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here (optional)
# NEO4J_URI=bolt://localhost:7687 (optional)
# NEO4J_USER=neo4j (optional)
# NEO4J_PASSWORD=password (optional)
```

5. **Configure Hydra (optional):**
Edit `src/conf/config.yaml` to customize:
- LLM provider (Anthropic Claude or OpenAI)
- Storage paths
- Logging levels
- Sprint configuration

## Usage

### Basic Usage

Run Artemis with a Kanban card ID:

```bash
cd /home/bbrelin/src/repos/artemis/src
python artemis_orchestrator.py --card-id card-001 --full
```

### Command-Line Options

```bash
python artemis_orchestrator.py --help

Options:
  --card-id TEXT          Kanban card ID to process
  --full                  Run full pipeline (all stages)
  --stage TEXT            Run specific stage only
  --debug                 Enable debug mode
  --config PATH           Path to custom config file
```

### Example: TDD Workflow

Create a Kanban card in `src/.agents/agile/kanban_board.json`:

```json
{
  "id": "card-tdd-001",
  "title": "Implement Binary Search Algorithm",
  "description": "Create a binary search function with comprehensive tests",
  "requirements": "Implement binary search with O(log n) complexity. Include unit tests.",
  "column": "backlog",
  "priority": "high"
}
```

Run:
```bash
python artemis_orchestrator.py --card-id card-tdd-001 --full
```

Artemis will:
1. Analyze requirements
2. Select TDD workflow (code artifact detected)
3. Generate RED (failing tests)
4. Generate GREEN (implementation)
5. Generate REFACTOR (optimized version)
6. Run code reviews
7. Output results to `.artemis_data/developer_output/`

### Example: Quality-Driven Workflow (Jupyter Notebook)

```json
{
  "id": "card-viz-001",
  "title": "Sales Data Visualization",
  "description": "Create interactive sales dashboard",
  "requirements": "Create Jupyter notebook with Plotly visualizations showing monthly sales trends, top products, and regional performance. Use Chart.js for web dashboard.",
  "column": "backlog",
  "priority": "medium"
}
```

Run:
```bash
python artemis_orchestrator.py --card-id card-viz-001 --full
```

Artemis will:
1. Detect UI/visualization artifact type
2. Use quality-driven workflow
3. Generate comprehensive notebook with multiple visualizations
4. Validate against quality criteria (min cells, visualizations, etc.)
5. Enhance based on validation feedback

## Configuration

### Hydra Configuration Files

Located in `src/conf/`:

- `config.yaml` - Main configuration
- `llm/anthropic.yaml` - Claude configuration
- `llm/openai.yaml` - OpenAI configuration
- `storage/local.yaml` - Local storage paths
- `logging/*.yaml` - Logging configuration
- `sprint/*.yaml` - Sprint settings

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
OPENAI_API_KEY=sk-...
HF_TOKEN=hf_...  # For HuggingFace datasets
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## Testing

Run tests:
```bash
cd src
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Project Structure Details

### Key Modules

- **artemis_orchestrator.py**: Main orchestrator - loads cards, runs pipeline
- **supervisor_agent.py**: Supervisor for multi-agent workflows
- **standalone_developer_agent.py**: Autonomous developer agent
- **code_review_agent.py**: Automated code review
- **rag_agent.py**: RAG for code examples and documentation
- **knowledge_graph.py**: Neo4j knowledge graph integration
- **artifact_quality_validator.py**: Quality validation for artifacts
- **artemis_stages.py**: Pipeline stage implementations
- **kanban_manager.py**: Kanban board management

### Pipeline Stages

1. **Requirements Stage**: Parse and validate requirements
2. **Sprint Planning Stage**: Effort estimation with planning poker
3. **Development Stage**: Multi-developer agent execution
4. **Code Review Stage**: Multi-agent code review
5. **BDD Validation Stage**: Behavior-driven testing
6. **Project Review Stage**: Comprehensive analysis
7. **Retrospective Stage**: Sprint retrospective

## Advanced Features

### Multi-Developer Arbitration

Artemis can run multiple developer agents in parallel and select the best solution:

```yaml
# In config.yaml
development:
  num_developers: 3
  selection_criteria: "code_quality"
```

### Knowledge Graph

Track project relationships using Neo4j:

```python
from knowledge_graph_factory import get_knowledge_graph

kg = get_knowledge_graph()
kg.add_entity("Module", "auth_service", {"language": "Python"})
kg.add_relation("auth_service", "uses", "jwt_library")
```

### RAG-Powered Code Generation

Store and retrieve code examples:

```python
from rag_agent import RAGAgent

rag = RAGAgent()
rag.store_artifact(
    artifact_type="code_example",
    card_id="example-001",
    task_title="Async Error Handling",
    content="...",
    metadata={"language": "JavaScript"}
)

results = rag.query("async error handling patterns", top_k=5)
```

### Checkpoint Recovery

Resume from checkpoints:

```bash
# Artemis automatically creates checkpoints
# Resume from last checkpoint:
python artemis_orchestrator.py --card-id card-001 --resume
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add license information]

## Support

For issues and questions:
- GitHub Issues: [Add repository URL]
- Documentation: `docs/` directory

## Roadmap

- [ ] GitHub integration for PR creation
- [ ] Docker containerization
- [ ] Web UI for monitoring
- [ ] Support for more programming languages
- [ ] Integration with Jira/Linear
- [ ] Claude Code integration
- [ ] Multi-repository support

## Credits

Developed using:
- Anthropic Claude API
- OpenAI API
- ChromaDB
- Neo4j
- Hydra

---

**Artemis** - Autonomous AI-Powered Development
