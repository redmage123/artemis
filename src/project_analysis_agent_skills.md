# Project Analysis Agent - Skills

## Agent Overview
**File**: `project_analysis_agent.py`
**Purpose**: Pre-implementation analysis across 8 dimensions
**Single Responsibility**: Identify issues and get user approval BEFORE implementation

## Core Skills

### 1. Multi-Dimensional Analysis (DEPTH Framework)

**D - Define Multiple Perspectives**:
- Security analysis
- Performance considerations
- Testing requirements
- Architecture decisions
- GDPR compliance
- Accessibility requirements
- Integration points
- Documentation needs

**E - Establish Clear Success Metrics**:
- Severity levels (CRITICAL, HIGH, MEDIUM)
- Approval criteria
- Quality gates

**P - Provide Context Layers**:
- Card details and requirements
- RAG historical context
- Knowledge Graph patterns
- Similar project outcomes

**T - Task Breakdown**:
- Dimension-by-dimension analysis
- Independent analyzers per dimension

**H - Human Feedback Loop**:
- Self-critique and validation
- User approval required

### 2. Dimension Analyzers

#### Security Analyzer
- **OWASP Risks**: Injection, XSS, authentication issues
- **Data Protection**: Encryption, secure storage
- **Access Control**: Authorization, authentication
- **API Security**: Rate limiting, validation

#### Performance Analyzer
- **Scalability**: Load handling, bottlenecks
- **Database**: Query optimization, indexing
- **Caching**: Strategy, invalidation
- **Resource Usage**: Memory, CPU, network

#### Testing Analyzer
- **Test Coverage**: Unit, integration, E2E
- **Test Data**: Fixtures, mocks, stubs
- **Test Automation**: CI/CD integration
- **Edge Cases**: Boundary conditions, errors

#### Architecture Analyzer
- **Design Patterns**: Appropriate patterns
- **SOLID Principles**: Compliance
- **Modularity**: Component separation
- **Dependencies**: External libraries, services

#### GDPR Analyzer
- **Personal Data**: PII identification
- **Consent**: User consent mechanisms
- **Data Retention**: Storage duration policies
- **Right to Erasure**: Data deletion capabilities

#### Accessibility Analyzer
- **WCAG 2.1 AA**: Compliance level
- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: ARIA, semantic HTML
- **Color Contrast**: Minimum ratios met

#### Integration Analyzer
- **External APIs**: Dependencies, versioning
- **Database**: Schema compatibility
- **Message Queues**: Event handling
- **Third-Party Services**: Reliability, fallbacks

#### Documentation Analyzer
- **Code Documentation**: Docstrings, comments
- **API Documentation**: OpenAPI, Swagger
- **User Documentation**: Guides, tutorials
- **Runbooks**: Deployment, troubleshooting

### 3. Issue Categorization

```python
Issue(
    category="Security",
    severity=Severity.CRITICAL,
    description="User passwords stored in plaintext",
    impact="Account takeover, data breach",
    suggestion="Use bcrypt or Argon2 for password hashing",
    reasoning="OWASP best practice, prevents credential theft",
    user_approval_needed=True
)
```

### 4. LLM-Powered Analysis
- **Context-Aware**: Uses task details and RAG context
- **Pattern Recognition**: Learns from past projects
- **Intelligent Suggestions**: AI-generated recommendations
- **Self-Critique**: Validates its own analysis

### 5. User Approval Workflow
- **Critical Issues**: Must be addressed before proceeding
- **High Issues**: Strongly recommended to address
- **Medium Issues**: Nice to have
- **Approval Gate**: User decides whether to proceed

## Analysis Output

```json
{
  "analysis_results": [
    {
      "dimension": "Security",
      "issues": [...],
      "recommendations": [...]
    },
    {
      "dimension": "Performance",
      "issues": [...],
      "recommendations": [...]
    }
  ],
  "critical_count": 2,
  "high_count": 5,
  "medium_count": 8,
  "requires_approval": true,
  "approval_status": "pending"
}
```

## SOLID Principles Applied

- **Single Responsibility**: Each analyzer handles ONE dimension
- **Open/Closed**: Add new analyzers without modifying core
- **Liskov Substitution**: All analyzers implement DimensionAnalyzer interface
- **Interface Segregation**: Minimal, focused interfaces
- **Dependency Inversion**: Depends on abstractions (DimensionAnalyzer)

## Dependencies

- `ai_query_service`: KG→RAG→LLM pipeline
- `llm_client`: LLM for analysis
- `environment_context`: Environment information
- `debug_mixin`: Debug capabilities

## Usage Patterns

```python
# Initialize project analysis agent
analyzer = ProjectAnalysisAgent(
    logger=logger,
    ai_service=ai_service
)

# Analyze task
analysis = analyzer.analyze_task(
    card_id="card-20251027-001",
    task_title="User Authentication System",
    task_description="Implement JWT-based authentication...",
    requirements_file="requirements.txt"
)

# Check if approval needed
if analysis['requires_approval']:
    print(f"Found {analysis['critical_count']} critical issues")
    user_decision = input("Proceed? (y/n): ")

    if user_decision.lower() != 'y':
        print("Task cancelled based on analysis")
        return

# Proceed with implementation
...
```

## Design Patterns

- **Strategy Pattern**: Pluggable dimension analyzers
- **Factory Pattern**: Analyzer creation
- **Template Method**: Standard analysis workflow
- **Observer Pattern**: Notify on critical issues

## Integration Points

- **Planning Stage**: Pre-implementation quality gate
- **Orchestrator**: Approval workflow
- **RAG Agent**: Historical project data
- **AI Query Service**: KG-enhanced analysis

## Quality Gates

### Must Fix (CRITICAL)
- Security vulnerabilities
- Data loss risks
- Compliance violations
- Breaking changes

### Should Fix (HIGH)
- Performance bottlenecks
- Poor architecture
- Missing test coverage
- Accessibility issues

### Nice to Have (MEDIUM)
- Code style improvements
- Documentation enhancements
- Minor optimizations

## Self-Critique Features

- **Completeness Check**: Did I analyze all dimensions?
- **Consistency Check**: Are recommendations contradictory?
- **Feasibility Check**: Are suggestions realistic?
- **Priority Check**: Are severities appropriate?

## Performance Optimizations

- **Parallel Analysis**: Dimensions analyzed concurrently
- **Cached Patterns**: RAG queries cached
- **Early Termination**: Critical issues stop analysis
- **Lazy Loading**: Only load needed analyzers

## Learning Capabilities

- **Historical Analysis**: "Similar project had this issue"
- **Pattern Detection**: Recurring problems
- **Best Practices**: What works in similar contexts
- **Anti-Patterns**: What to avoid

## Educational Value

- **Explains Why**: Rationale for each issue
- **Shows Impact**: What happens if ignored
- **Provides Solutions**: Concrete fix suggestions
- **Teaches Best Practices**: Improves team knowledge
