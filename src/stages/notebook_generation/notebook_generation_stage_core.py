from artemis_logger import get_logger
logger = get_logger('notebook_generation_stage_core')
'\nModule: notebook_generation_stage_core.py\n\nWHY: Core orchestration logic for notebook generation pipeline stage.\n     Coordinates template selection, cell generation, validation, and I/O.\n\nRESPONSIBILITY:\n- Orchestrate notebook generation workflow\n- Coordinate between template selector, cell generator, validator, and I/O\n- Handle pipeline observer notifications\n- Manage agent messenger communication\n- Implement PipelineStage interface\n\nPATTERNS:\n- Template Method: execute() defines workflow, delegates to strategies\n- Facade: Provides simple interface to complex subsystem\n- Observer: Notifies pipeline events\n- Dependency Injection: Components injected via constructor\n- Guard Clauses: Early returns for error conditions\n'
from typing import Dict, Any, List, Optional
from pathlib import Path
from artemis_exceptions import PipelineStageError, wrap_exception
from pipeline_observer import PipelineObservable, PipelineEvent, EventType
from agent_messenger import AgentMessenger
from .template_selector import TemplateSelector
from .cell_generator import CellGeneratorStrategy
from .notebook_validator import NotebookValidator
from .output_formatter import OutputFormatter
from .execution_handler import ExecutionHandler

class NotebookGenerationStage:
    """
    Pipeline stage for generating Jupyter notebooks

    WHY: Provides executable documentation combining code and narrative
    RESPONSIBILITY: Generate type-specific Jupyter notebooks from cards

    PATTERNS:
    - Template Method: execute() orchestrates workflow
    - Strategy: Delegates to CellGeneratorStrategy
    - Observer: Notifies PipelineObservable of events
    - Facade: Simple interface to complex notebook generation
    """

    def __init__(self, output_dir: str='.', logger: Optional[Any]=None, config: Optional[Dict[str, Any]]=None, observable: Optional[PipelineObservable]=None, messenger: Optional[AgentMessenger]=None, template_selector: Optional[TemplateSelector]=None, cell_generator: Optional[CellGeneratorStrategy]=None, validator: Optional[NotebookValidator]=None, formatter: Optional[OutputFormatter]=None, execution_handler: Optional[ExecutionHandler]=None):
        """
        Initialize notebook generation stage

        Args:
            output_dir: Directory to save notebooks
            logger: Optional logger instance
            config: Optional configuration dictionary
            observable: Optional PipelineObservable for events
            messenger: Optional AgentMessenger for communication
            template_selector: Optional TemplateSelector (injected)
            cell_generator: Optional CellGeneratorStrategy (injected)
            validator: Optional NotebookValidator (injected)
            formatter: Optional OutputFormatter (injected)
            execution_handler: Optional ExecutionHandler (injected)
        """
        self.output_dir = Path(output_dir)
        self.logger = logger
        self.config = config or {}
        self.observable = observable
        self.messenger = messenger
        self.template_selector = template_selector or TemplateSelector()
        self.cell_generator = cell_generator or CellGeneratorStrategy()
        self.validator = validator or NotebookValidator()
        self.formatter = formatter or OutputFormatter()
        self.execution_handler = execution_handler or ExecutionHandler(logger=logger)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, card: Dict[str, Any], context: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
        """
        Execute notebook generation stage (Template Method)

        Time Complexity: O(n) where n = number of cells
        Space Complexity: O(n) for notebook storage

        Args:
            card: Kanban card with task information
            context: Additional context from previous stages

        Returns:
            Stage results with notebook paths

        Raises:
            PipelineStageError: If notebook generation fails
        """
        try:
            self._notify_stage_start(card)
            self.log('📓 Starting Notebook Generation Stage', 'INFO')
            notebook_type = self.template_selector.determine_notebook_type(card, context)
            self.log(f'Notebook type: {notebook_type}', 'INFO')
            notebook = self._generate_notebook(card, notebook_type, context or {})
            is_valid, error = self.validator.validate_notebook(notebook)
            if not is_valid:
                raise ValueError(f'Invalid notebook: {error}')
            filename = self.formatter.format_filename(card.get('title', 'notebook'))
            output_path = self.formatter.format_output_path(self.output_dir, filename)
            success, write_error = self.execution_handler.write_notebook(notebook, output_path)
            if not success:
                raise IOError(f'Failed to write notebook: {write_error}')
            is_valid, verify_error = self.execution_handler.verify_written_notebook(output_path)
            if not is_valid:
                raise IOError(f'Notebook verification failed: {verify_error}')
            self.log(f'✅ Notebook generated: {output_path}', 'SUCCESS')
            result = self.formatter.format_stage_result(output_path, notebook_type)
            self._notify_stage_complete(result)
            self._send_data_update(card, output_path, notebook_type)
            return result
        except Exception as e:
            error_msg = f'Notebook generation failed: {str(e)}'
            self.log(error_msg, 'ERROR')
            self._notify_stage_failed(card, e)
            self._send_error_notification(card, error_msg, e)
            raise wrap_exception(e, PipelineStageError, error_msg, context={'stage': 'notebook_generation', 'card_id': card.get('id', 'unknown')})

    def _generate_notebook(self, card: Dict[str, Any], notebook_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate notebook using cell generator strategy

        Time Complexity: O(n) where n = number of cells
        Space Complexity: O(n) for notebook data

        Args:
            card: Kanban card
            notebook_type: Type of notebook
            context: Stage context

        Returns:
            Complete notebook dictionary
        """
        return self.cell_generator.generate_cells(notebook_type=notebook_type, card=card, context=context)

    def _notify_stage_start(self, card: Dict[str, Any]):
        """Notify observers of stage start"""
        if not self.observable:
            return
        self.observable.notify(PipelineEvent(event_type=EventType.STAGE_START, stage_name='notebook_generation', data={'card_id': card.get('id', 'unknown')}))

    def _notify_stage_complete(self, result: Dict[str, Any]):
        """Notify observers of stage completion"""
        if not self.observable:
            return
        self.observable.notify(PipelineEvent(event_type=EventType.STAGE_COMPLETE, stage_name='notebook_generation', data=result))

    def _notify_stage_failed(self, card: Dict[str, Any], error: Exception):
        """Notify observers of stage failure"""
        if not self.observable:
            return
        self.observable.notify(PipelineEvent(event_type=EventType.STAGE_FAILED, stage_name='notebook_generation', data={'card_id': card.get('id', 'unknown'), 'error': str(error)}))

    def _send_data_update(self, card: Dict[str, Any], notebook_path: Path, notebook_type: str):
        """Send data update via messenger"""
        if not self.messenger:
            return
        data = self.formatter.format_messenger_data(notebook_path, notebook_type, card.get('id', 'unknown'))
        self.messenger.send_data_update(to_agent='integration-agent', card_id=card.get('id', 'unknown'), data=data, priority='normal')

    def _send_error_notification(self, card: Dict[str, Any], error_msg: str, error: Exception):
        """Send error notification via messenger"""
        if not self.messenger:
            return
        self.messenger.send_error(to_agent='supervisor-agent', card_id=card.get('id', 'unknown'), data={'stage': 'notebook_generation', 'error': error_msg, 'error_type': type(error).__name__})

    def log(self, message: str, level: str='INFO'):
        """
        Log a message

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
        """
        if self.logger:
            self.logger.log(message, level)
        else:
            
            logger.log(f'[{level}] {message}', 'INFO')

def generate_notebook(card: Dict[str, Any], output_dir: str='.', notebook_type: Optional[str]=None, context: Optional[Dict[str, Any]]=None) -> str:
    """
    Generate a Jupyter notebook from a card (convenience function)

    Time Complexity: O(n) where n = number of cells
    Space Complexity: O(n) for notebook data

    Args:
        card: Kanban card with task information
        output_dir: Directory to save notebook
        notebook_type: Optional explicit notebook type
        context: Optional additional context

    Returns:
        Path to generated notebook
    """
    stage = NotebookGenerationStage(output_dir=output_dir)
    if notebook_type:
        if 'metadata' not in card:
            card['metadata'] = {}
        card['metadata']['notebook_type'] = notebook_type
    result = stage.execute(card=card, context=context)
    return result['notebook_path']