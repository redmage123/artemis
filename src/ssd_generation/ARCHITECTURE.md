# SSD Generation Package Architecture

## Overview

The SSD Generation package creates comprehensive Software Specification Documents that guide the architecture and development phases of the Artemis pipeline.

## Package Structure

```
ssd_generation/
├── models/              # Data models (immutable structures)
├── services/            # Business logic services
├── generators/          # Output format generators
├── prompts/             # LLM prompt templates
└── ssd_generation_stage.py  # Main orchestrator
```

## Component Responsibilities

### Models (`models/`)
**WHY**: Immutable data structures for type safety and clarity.

- `RequirementItem`: Single requirement with ID, category, priority, acceptance criteria
- `DiagramSpec`: Diagram specification with Mermaid/Chart.js config
- `SSDDocument`: Complete SSD aggregating all sections

### Services (`services/`)
**WHY**: Business logic separated from data and presentation.

- `SSDDecisionService`: Intelligent decision-making for SSD necessity
- `RequirementsAnalyzer`: Analyzes cards and extracts structured requirements
- `DiagramGenerator`: Creates architecture and ERD diagram specifications
- `RAGStorageService`: Stores SSD artifacts in RAG for architecture agent

### Generators (`generators/`)
**WHY**: Output format generation separated from business logic.

- `MarkdownGenerator`: Generates Markdown documentation
- `HTMLGenerator`: Generates HTML with embedded Mermaid diagrams
- `PDFGenerator`: Converts HTML to PDF (requires weasyprint)
- `OutputFileGenerator`: Facade coordinating all output formats

### Prompts (`prompts/`)
**WHY**: LLM prompts separated from business logic for maintainability.

- `RequirementsPrompts`: Prompts for requirements analysis and extraction
- `DiagramPrompts`: Prompts for diagram generation

### Orchestrator
**WHY**: Coordinates all services to produce complete SSD.

- `SSDGenerationStage`: Main pipeline stage implementing PipelineStage interface

## Design Patterns

1. **Facade Pattern**: OutputFileGenerator simplifies multiple generator calls
2. **Template Method**: Prompt builders use template method pattern
3. **Generator Pattern**: Used for memory-efficient large data processing
4. **Dependency Injection**: All dependencies injected via constructors
5. **Guard Clauses**: Early returns for clarity and error handling
6. **Single Responsibility**: Each module has one clear purpose

## Data Flow

```
1. Card Analysis
   └─> SSDDecisionService: Should SSD be generated?
       ├─> Yes: Continue
       └─> No: Return skipped status

2. Requirements Analysis
   └─> RequirementsAnalyzer
       ├─> Analyze high-level requirements
       ├─> Generate executive summary
       ├─> Extract structured requirements
       └─> Generate constraints/assumptions/risks

3. Diagram Generation
   └─> DiagramGenerator
       └─> Generate architecture, ERD, component diagrams

4. Document Assembly
   └─> SSDDocument (immutable data structure)

5. Output Generation
   └─> OutputFileGenerator
       ├─> JSON output
       ├─> Markdown output (via MarkdownGenerator)
       ├─> HTML output (via HTMLGenerator)
       └─> PDF output (via PDFGenerator)

6. RAG Storage
   └─> RAGStorageService
       ├─> Store executive summary
       ├─> Store requirements
       └─> Store diagrams
```

## Extension Points

### Adding New Output Formats
1. Create new generator in `generators/`
2. Implement generation method taking `SSDDocument`
3. Register in `OutputFileGenerator`

### Adding New Diagram Types
1. Update `DiagramPrompts.build_diagram_generation_prompt()`
2. Update `DiagramGenerator` to handle new type
3. Update HTML/Markdown generators to render new type

### Adding New Requirement Types
1. Add category to `RequirementItem.category`
2. Update `RequirementsPrompts.build_requirements_extraction_prompt()`
3. Update `RequirementsAnalyzer.extract_requirements()`
4. Update generators to render new category

## Testing Strategy

### Unit Tests
- Test each service independently with mocked dependencies
- Test generators with sample `SSDDocument` instances
- Test prompt builders with various inputs

### Integration Tests
- Test full pipeline from card to output files
- Test RAG storage and retrieval
- Test error handling and edge cases

### Contract Tests
- Verify PipelineStage interface compliance
- Verify backward compatibility with wrapper
- Verify output format schemas

## Performance Considerations

1. **Generator Pattern**: Used for large requirement lists to avoid memory bloat
2. **Lazy Evaluation**: Diagrams only generated when needed
3. **Streaming Output**: Large HTML/Markdown built incrementally
4. **Caching**: LLM responses could be cached (future enhancement)

## Dependencies

### Required
- `llm_client`: LLM interaction
- `artemis_stage_interface`: PipelineStage interface
- `artemis_exceptions`: Error handling

### Optional
- `rag_agent`: RAG storage (gracefully degraded if unavailable)
- `weasyprint`: PDF generation (skipped if unavailable)

## Backward Compatibility

The original `ssd_generation_stage.py` is now a thin wrapper (66 lines) that re-exports all symbols from the modularized package. This ensures:

1. **Zero Breaking Changes**: Existing imports continue to work
2. **Gradual Migration**: Consumers can migrate to direct package imports at their own pace
3. **Clean Deprecation Path**: Wrapper can be deprecated in future versions

## Future Enhancements

1. **Template Customization**: Allow custom SSD templates
2. **Multi-Language Support**: Generate SSDs in multiple languages
3. **Diagram Validation**: Validate Mermaid syntax before saving
4. **Interactive HTML**: Add collapsible sections, search, filtering
5. **Version Control**: Track SSD changes over time
6. **Collaboration Features**: Comments, approvals, sign-offs
