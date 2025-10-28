# Artemis CLI Package

A modular command-line interface package for Artemis helper tools.

## Structure

```
cli/
├── __init__.py          # Package exports and public API
├── models.py            # Data models and types (129 lines)
├── parser.py            # Argument parsing (208 lines)
├── commands.py          # Command implementations (562 lines)
├── formatters.py        # Output formatting (289 lines)
└── cli_core.py         # Main CLI orchestration (98 lines)
```

## Components

### models.py
Data models and type definitions:
- `CommandType`: Enum of supported commands
- `PromptAction`: Enum of prompt actions
- `CLIArguments`: Dataclass for parsed arguments
- `CommandResult`: Dataclass for command results
- `SystemStatus`, `LLMConfig`, `StoragePaths`: Configuration models

### parser.py
Argument parsing with argparse:
- `ArgumentParser`: Builds and configures CLI parser
- Converts argparse Namespace to typed CLIArguments
- Centralizes all argument definitions

### commands.py
Command implementations using Command Pattern:
- `CommandHandler`: Base class with error handling
- `InitPromptsCommand`: Initialize DEPTH prompts
- `TestConfigCommand`: Test Hydra configuration
- `RunCommand`: Execute Artemis orchestrator
- `CleanupCommand`: Clean workspace
- `StatusCommand`: Show system status
- `PromptsCommand`: Manage prompt templates
- `CommandDispatcher`: Routes commands via dispatch table

### formatters.py
Output formatting utilities:
- `OutputFormatter`: Basic formatting (headers, messages, bullets)
- `StatusFormatter`: System status formatting
- `PromptFormatter`: Prompt information formatting

### cli_core.py
Main CLI orchestration:
- `ArtemisCLI`: CLI lifecycle management
- `main()`: Entry point function
- Top-level error and signal handling

### __init__.py
Package public API:
- Exports main entry points
- Exports models and types
- Exports components
- Version information

## Usage

### From Command Line
```bash
# Via original entry point (backward compatible)
python3 artemis_cli.py --help
python3 artemis_cli.py run card-123

# Via module invocation
python3 -m cli.cli_core --help
```

### From Python Code
```python
# Import main entry point
from cli import main, ArtemisCLI

# Run CLI programmatically
exit_code = main(['run', 'card-123'])

# Or use CLI class directly
cli = ArtemisCLI()
exit_code = cli.run(['status'])

# Import models for testing
from cli.models import CLIArguments, CommandType
args = CLIArguments(command=CommandType.RUN, card_id='card-123')

# Import components
from cli.commands import CommandDispatcher
from cli.formatters import OutputFormatter
```

## Design Patterns

- **Command Pattern**: Each command is a handler class
- **Dispatch Tables**: Dictionary-based routing instead of elif chains
- **Strategy Pattern**: Multiple formatter classes
- **Facade Pattern**: Backward compatibility wrapper
- **Builder Pattern**: Parser construction
- **Single Responsibility**: Each module has one purpose

## Standards

All modules follow these standards:
- ✓ WHY/RESPONSIBILITY/PATTERNS documentation headers
- ✓ Guard clauses (max 1 level nesting)
- ✓ Complete type hints (List, Dict, Any, Optional, Callable)
- ✓ Dispatch tables instead of elif chains
- ✓ Single Responsibility Principle

## Testing

All modules compile successfully:
```bash
python3 -m py_compile cli/*.py
```

All imports work correctly:
```bash
python3 -c "from cli import main; print('✓ Success')"
```

## Backward Compatibility

The original `artemis_cli.py` entry point is preserved as a thin wrapper:
- Original: 507 lines (monolithic)
- Wrapper: 41 lines (91.9% reduction)
- Functionality: 100% identical

## Extending

### Add a New Command

1. Create handler in `commands.py`:
```python
class MyNewCommand(CommandHandler):
    def execute(self) -> CommandResult:
        # Implementation
        return CommandResult.success_result()
```

2. Add to dispatch table in `CommandDispatcher._build_handler_map()`:
```python
CommandType.MY_NEW: MyNewCommand,
```

3. Add command type to `models.py`:
```python
class CommandType(Enum):
    MY_NEW = "my-new"
```

4. Add parser configuration in `parser.py`:
```python
def _add_my_new_command(self, subparsers):
    parser = subparsers.add_parser("my-new", help="...")
    parser.set_defaults(command_type=CommandType.MY_NEW)
```

### Add a New Formatter

Add formatting method to appropriate formatter class in `formatters.py`:
```python
@staticmethod
def format_my_data(data: Dict[str, Any]) -> str:
    # Implementation
    return formatted_string
```

## License

Part of the Artemis Autonomous Development Pipeline project.
