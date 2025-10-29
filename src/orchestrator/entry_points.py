"""
Entry Points - CLI entry point functions for Artemis orchestrator

WHAT:
Main entry point functions (main_hydra, main_legacy) that initialize
dependencies and run the orchestrator. Supports both Hydra-powered
and legacy argparse interfaces.

WHY:
Separates CLI logic from orchestrator core, enabling:
- Focused testing of CLI parsing
- Reusable orchestrator instantiation
- Clean separation between CLI and core logic
- Support for multiple CLI interfaces (Hydra, argparse)

RESPONSIBILITY:
- Parse CLI arguments (Hydra or argparse)
- Initialize dependencies (board, messenger, rag, etc.)
- Create orchestrator instance
- Run pipeline or display status
- Handle CLI-specific errors and display

PATTERNS:
- Facade Pattern: Simplifies complex orchestrator initialization
- Strategy Pattern: Pluggable CLI interface (Hydra vs argparse)
- Builder Pattern: Incrementally constructs orchestrator
- Dispatch Table: Command routing (status, list-active, run)

EXTRACTED FROM: artemis_orchestrator.py lines 1397-1738
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime
import hydra
from omegaconf import DictConfig
from artemis_services import PipelineLogger
from kanban_manager import KanbanBoard
from messenger_factory import MessengerFactory
from rag_agent import RAGAgent
from config_agent import get_config
from artemis_exceptions import PipelineStageError, create_wrapped_exception
from debug_service import DebugService
from orchestrator.orchestrator_core import ArtemisOrchestrator
from orchestrator.cli_display import display_workflow_status, list_active_workflows
from orchestrator.config_validation import validate_config_or_exit, get_config_path
from orchestrator.card_creation import create_card_from_requirements, attach_requirements_to_card
from orchestrator.adaptive_integration import select_adaptive_strategy

@hydra.main(version_base=None, config_path=get_config_path(), config_name='config')
def main_hydra(cfg: DictConfig) -> None:
    """
    Hydra-powered entry point with type-safe configuration

    WHAT:
    Main entry point for Hydra-based configuration. Parses Hydra config,
    initializes dependencies, creates orchestrator, and runs pipeline.

    WHY:
    Hydra provides:
    - Type-safe configuration with validation
    - Easy configuration composition
    - Command-line overrides
    - Multi-environment support (dev, prod, etc.)

    FLOW:
    1. Parse Hydra configuration
    2. Display pipeline configuration (if verbose)
    3. Initialize dependencies (board, logger, debug service, messenger, rag)
    4. Configure Git Agent from repository config
    5. Register orchestrator with messenger
    6. Create orchestrator with Hydra config
    7. Run full pipeline
    8. Display results

    Usage:
        python artemis_orchestrator.py card_id=card-001
        python artemis_orchestrator.py card_id=card-002 llm.provider=anthropic
        python artemis_orchestrator.py --config-name env/dev +card_id=dev-001

    Args:
        cfg: Hydra DictConfig with type-safe configuration

    PATTERNS:
        - Facade Pattern: Simplifies orchestrator initialization
        - Builder Pattern: Constructs orchestrator with dependencies
        - Exception Wrapper: Consistent error handling
    """
    if cfg.logging.verbose:
        
        logger.log('\n' + '=' * 70, 'INFO')
        
        logger.log('🏹 ARTEMIS PIPELINE ORCHESTRATOR (Hydra-Powered)', 'INFO')
        
        logger.log('=' * 70, 'INFO')
        
        logger.log(f'\nCard ID: {cfg.card_id}', 'INFO')
        
        logger.log(f'LLM: {cfg.llm.provider} ({cfg.llm.model})', 'INFO')
        
        logger.log(f'Pipeline: {len(cfg.pipeline.stages)} stages', 'INFO')
        
        logger.log(f'Max Parallel Developers: {cfg.pipeline.max_parallel_developers}', 'INFO')
        
        logger.log(f"Code Review: {('Enabled' if cfg.pipeline.enable_code_review else 'Disabled')}", 'INFO')
        
        logger.log(f"Supervision: {('Enabled' if cfg.pipeline.enable_supervision else 'Disabled')}", 'INFO')
        
        logger.log('=' * 70 + '\n', 'INFO')
    board = KanbanBoard()
    logger = PipelineLogger(verbose=cfg.logging.verbose)
    debug_config = cfg.get('debug', None) if hasattr(cfg, 'debug') else None
    DebugService.initialize(config=debug_config, logger=logger, cli_debug=None)
    messenger = MessengerFactory.create_from_env(agent_name='artemis-orchestrator')
    rag = RAGAgent(db_path=cfg.storage.rag_db_path, verbose=cfg.logging.verbose)
    from git_agent import GitAgent
    git_agent = GitAgent(verbose=cfg.logging.verbose)
    repo_config = git_agent.configure_repository(name=cfg.repository.name, local_path=cfg.repository.local_path, remote_url=cfg.repository.get('remote_url', None), branch_strategy=cfg.repository.branch_strategy, default_branch=cfg.repository.default_branch, auto_push=cfg.repository.auto_push, create_if_missing=cfg.repository.create_if_missing)
    if cfg.logging.verbose:
        
        logger.log(f'\n🔧 Git Agent Configured:', 'INFO')
        
        logger.log(f'   Repository: {repo_config.name}', 'INFO')
        
        logger.log(f'   Path: {repo_config.local_path}', 'INFO')
        
        logger.log(f'   Strategy: {repo_config.branch_strategy}', 'INFO')
        
        logger.log(f"   Remote: {repo_config.remote_url or 'None (local only)'}", 'INFO')
    messenger.register_agent(capabilities=['coordinate_pipeline', 'manage_workflow'], status='active')
    try:
        orchestrator = ArtemisOrchestrator(card_id=cfg.card_id, board=board, messenger=messenger, rag=rag, hydra_config=cfg, git_agent=git_agent)
        from orchestrator.pipeline_execution import run_full_pipeline
        result = run_full_pipeline(orchestrator)
        
        logger.log(f"\n✅ Pipeline completed: {result['status']}", 'INFO')
    except Exception as e:
        raise create_wrapped_exception(e, PipelineStageError, 'Pipeline orchestrator execution failed', {'card_id': cfg.card_id})

def main_legacy():
    """
    Legacy CLI entry point (backward compatibility with old argparse interface)

    WHAT:
    Main entry point for legacy argparse-based CLI. Parses arguments,
    initializes dependencies, creates orchestrator, and runs pipeline
    or displays status.

    WHY:
    Provides backward compatibility with existing scripts and workflows
    that use argparse interface. Supports:
    - Status queries (--status, --list-active)
    - Configuration reports (--config-report)
    - Requirements file processing (--requirements-file)
    - Checkpoint resume (--resume)
    - Debug mode (--debug)

    FLOW:
    1. Parse argparse arguments
    2. Handle status queries (--status, --list-active) and exit
    3. Load and validate configuration
    4. Handle config report (--config-report) and exit
    5. Initialize dependencies (board, logger, debug service, messenger, rag)
    6. Handle requirements file (create new card or attach to existing)
    7. Create orchestrator with legacy config
    8. Run pipeline (if --full) or display help

    Usage:
        python artemis_orchestrator.py --card-id card-001 --full
        python artemis_orchestrator.py --requirements-file reqs.pdf --full
        python artemis_orchestrator.py --status --card-id card-001
        python artemis_orchestrator.py --list-active
        python artemis_orchestrator.py --config-report

    PATTERNS:
        - Facade Pattern: Simplifies orchestrator initialization
        - Dispatch Table: Command routing based on arguments
        - Strategy Pattern: Different handling for requirements file scenarios
        - Guard Clause: Early returns for status queries
    """
    parser = argparse.ArgumentParser(description='Artemis Pipeline Orchestrator')
    parser.add_argument('--card-id', help='Kanban card ID')
    parser.add_argument('--full', action='store_true', help='Run full pipeline')
    parser.add_argument('--resume', action='store_true', help='Resume from last checkpoint (if available)')
    parser.add_argument('--requirements-file', help='Path to requirements document (PDF, Word, Excel, text, etc.)')
    parser.add_argument('--config-report', action='store_true', help='Show configuration report')
    parser.add_argument('--skip-validation', action='store_true', help='Skip config validation (not recommended)')
    parser.add_argument('--status', action='store_true', help='Show workflow status for card-id')
    parser.add_argument('--list-active', action='store_true', help='List all active workflows')
    parser.add_argument('--json', action='store_true', help='Output status in JSON format')
    parser.add_argument('--debug', nargs='?', const='default', metavar='PROFILE', help='Enable debug mode (optional profile: verbose, minimal, default)')
    parser.add_argument('--debug-profile', help='Debug profile to use (verbose, minimal, default)')
    args = parser.parse_args()
    if args.list_active:
        list_active_workflows()
        return
    if args.status:
        if not args.card_id:
            
            logger.log('\n❌ Error: --card-id is required with --status\n', 'INFO')
            sys.exit(1)
        display_workflow_status(args.card_id, json_output=args.json)
        return
    config = get_config(verbose=True)
    if args.config_report:
        config.print_configuration_report()
        return
    if not args.card_id and (not args.requirements_file):
        
        logger.log('\n❌ Error: --card-id or --requirements-file is required for pipeline execution\n', 'INFO')
        parser.print_help()
        sys.exit(1)
    validate_config_or_exit(config, args.skip_validation)
    board = KanbanBoard()
    logger = PipelineLogger(verbose=True)
    cli_debug_value = args.debug_profile or args.debug
    DebugService.initialize(config=None, logger=logger, cli_debug=cli_debug_value)
    messenger = MessengerFactory.create_from_env(agent_name='artemis-orchestrator')
    rag_db_path = config.get('ARTEMIS_RAG_DB_PATH', 'db')
    rag = RAGAgent(db_path=rag_db_path, verbose=True)
    messenger.register_agent(capabilities=['coordinate_pipeline', 'manage_workflow'], status='active')
    try:
        # Track parsed requirements and card for adaptive pipeline selection
        parsed_requirements = None
        card_for_adaptive = None

        def _create_card_from_requirements():
            """Strategy: Create new card from requirements file (autonomous mode)"""
            nonlocal parsed_requirements, card_for_adaptive
            card_id, parsed_requirements = create_card_from_requirements(
                args.requirements_file, board, rag, config
            )
            card_for_adaptive, _ = board._find_card(card_id)
            return card_id

        def _attach_requirements_to_card():
            """Strategy: Attach requirements file to existing card"""
            nonlocal card_for_adaptive
            card_id = attach_requirements_to_card(args.card_id, args.requirements_file, board)
            card_for_adaptive, _ = board._find_card(card_id)
            return card_id

        def _use_existing_card():
            """Strategy: Use existing card without requirements file"""
            nonlocal card_for_adaptive
            card_for_adaptive, _ = board._find_card(args.card_id)
            return args.card_id

        # Apply requirements strategy
        requirements_strategy = {
            (True, False): _create_card_from_requirements,
            (True, True): _attach_requirements_to_card,
            (False, True): _use_existing_card
        }
        strategy_key = (bool(args.requirements_file), bool(args.card_id))
        handler = requirements_strategy.get(strategy_key)
        if handler:
            args.card_id = handler()

        # Select adaptive pipeline strategy based on complexity
        pipeline_strategy = None
        adaptive_config = None
        if parsed_requirements and card_for_adaptive:
            logger.log("\n" + "=" * 70, "INFO")
            logger.log("🎯 ADAPTIVE PIPELINE SELECTION", "INFO")
            logger.log("=" * 70, "INFO")

            pipeline_strategy = select_adaptive_strategy(
                parsed_requirements,
                card_for_adaptive,
                force_path=getattr(args, 'pipeline_path', None),
                observable=None,
                verbose=True
            )

            logger.log("=" * 70 + "\n", "INFO")

            # Generate adaptive config based on task + platform
            from adaptive_config_generator import generate_adaptive_config
            adaptive_config = generate_adaptive_config(
                parsed_requirements,
                card_for_adaptive,
                platform_info=None  # Will auto-detect
            )

            # Display adaptive config with summary display
            from orchestrator.summary_display import create_summary_display
            verbose = getattr(args, 'verbose', False)
            summary = create_summary_display(logger, verbose=verbose)
            summary.show_adaptive_config(adaptive_config)

        # Create orchestrator with adaptive strategy and config
        orchestrator = ArtemisOrchestrator(
            card_id=args.card_id,
            board=board,
            messenger=messenger,
            rag=rag,
            config=config,
            resume=args.resume,
            strategy=pipeline_strategy,  # Pass adaptive strategy
            adaptive_config=adaptive_config  # Pass adaptive config
        )
        if args.full:
            from orchestrator.pipeline_execution import run_full_pipeline
            result = run_full_pipeline(orchestrator)
            
            logger.log(f"\n✅ Pipeline completed: {result['status']}", 'INFO')
        else:
            
            logger.log('Use --full to run the complete pipeline', 'INFO')
    except ValueError as e:
        
        logger.log(f'\n❌ Configuration Error: {e}', 'INFO')
        
        logger.log('💡 Run with --config-report to see full configuration\n', 'INFO')
        sys.exit(1)
    except Exception as e:
        raise create_wrapped_exception(e, PipelineStageError, 'Pipeline orchestrator execution failed', {'card_id': args.card_id})