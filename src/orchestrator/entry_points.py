#!/usr/bin/env python3
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

# Import debug service
from debug_service import DebugService

# Import orchestrator modules
from orchestrator.orchestrator_core import ArtemisOrchestrator
from orchestrator.cli_display import display_workflow_status, list_active_workflows
from orchestrator.config_validation import validate_config_or_exit, get_config_path


@hydra.main(version_base=None, config_path=get_config_path(), config_name="config")
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
    # Print configuration
    if cfg.logging.verbose:
        print("\n" + "="*70)
        print("🏹 ARTEMIS PIPELINE ORCHESTRATOR (Hydra-Powered)")
        print("="*70)
        print(f"\nCard ID: {cfg.card_id}")
        print(f"LLM: {cfg.llm.provider} ({cfg.llm.model})")
        print(f"Pipeline: {len(cfg.pipeline.stages)} stages")
        print(f"Max Parallel Developers: {cfg.pipeline.max_parallel_developers}")
        print(f"Code Review: {'Enabled' if cfg.pipeline.enable_code_review else 'Disabled'}")
        print(f"Supervision: {'Enabled' if cfg.pipeline.enable_supervision else 'Disabled'}")
        print("="*70 + "\n")

    # Initialize dependencies (Dependency Injection)
    board = KanbanBoard()

    # Initialize logger before debug service
    logger = PipelineLogger(verbose=cfg.logging.verbose)

    # Initialize Debug Service (supports Hydra config + environment variables)
    debug_config = cfg.get('debug', None) if hasattr(cfg, 'debug') else None
    DebugService.initialize(
        config=debug_config,
        logger=logger,
        cli_debug=None  # Hydra mode: CLI overrides via config
    )

    # Create messenger using factory (pluggable implementation)
    messenger = MessengerFactory.create_from_env(
        agent_name="artemis-orchestrator"
    )

    rag = RAGAgent(db_path=cfg.storage.rag_db_path, verbose=cfg.logging.verbose)

    # Initialize Git Agent from repository configuration
    from git_agent import GitAgent
    git_agent = GitAgent(verbose=cfg.logging.verbose)
    repo_config = git_agent.configure_repository(
        name=cfg.repository.name,
        local_path=cfg.repository.local_path,
        remote_url=cfg.repository.get('remote_url', None),
        branch_strategy=cfg.repository.branch_strategy,
        default_branch=cfg.repository.default_branch,
        auto_push=cfg.repository.auto_push,
        create_if_missing=cfg.repository.create_if_missing
    )

    if cfg.logging.verbose:
        print(f"\n🔧 Git Agent Configured:")
        print(f"   Repository: {repo_config.name}")
        print(f"   Path: {repo_config.local_path}")
        print(f"   Strategy: {repo_config.branch_strategy}")
        print(f"   Remote: {repo_config.remote_url or 'None (local only)'}")

    # Register orchestrator
    messenger.register_agent(
        capabilities=["coordinate_pipeline", "manage_workflow"],
        status="active"
    )

    try:
        # Create orchestrator with Hydra config
        orchestrator = ArtemisOrchestrator(
            card_id=cfg.card_id,
            board=board,
            messenger=messenger,
            rag=rag,
            hydra_config=cfg,
            git_agent=git_agent
        )

        # Run full pipeline
        from orchestrator.pipeline_execution import run_full_pipeline
        result = run_full_pipeline(orchestrator)
        print(f"\n✅ Pipeline completed: {result['status']}")

    except Exception as e:
        raise create_wrapped_exception(
            e,
            PipelineStageError,
            "Pipeline orchestrator execution failed",
            {
                "card_id": cfg.card_id
            }
        )


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
    parser = argparse.ArgumentParser(description="Artemis Pipeline Orchestrator")
    parser.add_argument("--card-id", help="Kanban card ID")
    parser.add_argument("--full", action="store_true", help="Run full pipeline")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint (if available)")
    parser.add_argument("--requirements-file", help="Path to requirements document (PDF, Word, Excel, text, etc.)")
    parser.add_argument("--config-report", action="store_true", help="Show configuration report")
    parser.add_argument("--skip-validation", action="store_true", help="Skip config validation (not recommended)")
    parser.add_argument("--status", action="store_true", help="Show workflow status for card-id")
    parser.add_argument("--list-active", action="store_true", help="List all active workflows")
    parser.add_argument("--json", action="store_true", help="Output status in JSON format")
    parser.add_argument("--debug", nargs='?', const='default', metavar='PROFILE',
                       help="Enable debug mode (optional profile: verbose, minimal, default)")
    parser.add_argument("--debug-profile", help="Debug profile to use (verbose, minimal, default)")
    args = parser.parse_args()

    # Handle status queries (don't require config)
    if args.list_active:
        list_active_workflows()
        return

    if args.status:
        # Guard: Missing required argument
        if not args.card_id:
            print("\n❌ Error: --card-id is required with --status\n")
            sys.exit(1)

        display_workflow_status(args.card_id, json_output=args.json)
        return

    # Load and validate configuration
    config = get_config(verbose=True)

    if args.config_report:
        config.print_configuration_report()
        return

    # Guard: Require card-id OR requirements-file for pipeline execution
    if not args.card_id and not args.requirements_file:
        print("\n❌ Error: --card-id or --requirements-file is required for pipeline execution\n")
        parser.print_help()
        sys.exit(1)

    # Validate configuration before proceeding
    validate_config_or_exit(config, args.skip_validation)

    # Initialize dependencies (Dependency Injection)
    board = KanbanBoard()

    # Initialize logger before debug service
    logger = PipelineLogger(verbose=True)

    # Initialize Debug Service (supports CLI + environment variables)
    # Determine debug CLI value (priority: --debug-profile > --debug)
    cli_debug_value = args.debug_profile or args.debug
    DebugService.initialize(
        config=None,  # Legacy mode: no Hydra config
        logger=logger,
        cli_debug=cli_debug_value
    )

    # Create messenger using factory (pluggable implementation)
    messenger = MessengerFactory.create_from_env(
        agent_name="artemis-orchestrator"
    )

    rag_db_path = config.get('ARTEMIS_RAG_DB_PATH', 'db')
    rag = RAGAgent(db_path=rag_db_path, verbose=True)

    # Register orchestrator
    messenger.register_agent(
        capabilities=["coordinate_pipeline", "manage_workflow"],
        status="active"
    )

    try:
        # Dispatch table for requirements handling strategies
        def _create_card_from_requirements():
            """Strategy: Create new card from requirements file (autonomous mode)"""
            from requirements_parser_agent import RequirementsParserAgent
            from document_reader import DocumentReader

            print(f"\n🤖 Autonomous Mode: Creating card from requirements file...")
            print(f"📄 Reading: {args.requirements_file}")

            # Read requirements document
            doc_reader = DocumentReader(verbose=False)
            requirements_text = doc_reader.read_document(args.requirements_file)

            # Parse requirements with AI
            parser = RequirementsParserAgent(
                llm_provider=config.get('ARTEMIS_LLM_PROVIDER', 'openai'),
                llm_model=config.get('ARTEMIS_LLM_MODEL', 'gpt-4'),
                rag=rag
            )

            parsed_reqs = parser.parse_requirements_file(args.requirements_file)

            # Extract title: prefer project_name, then first functional requirement, then filename
            filename_without_ext = Path(args.requirements_file).stem
            filename_as_title = filename_without_ext.replace('_', ' ').replace('-', ' ').title()

            # Determine title using priority order
            title = filename_as_title  # Default

            # Override with first functional requirement if available
            if parsed_reqs.functional_requirements:
                title = parsed_reqs.functional_requirements[0].title

            # Override with project_name if explicitly set (not just derived from filename)
            if parsed_reqs.project_name and parsed_reqs.project_name != filename_as_title:
                title = parsed_reqs.project_name

            # Generate unique card ID
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            card_id = f"auto-{timestamp}"

            # Determine priority from highest priority functional requirement
            # Map RequirementsParser priorities to KanbanManager priorities
            priority_map = {
                'critical': 'high',     # critical → high
                'high': 'high',         # high → high
                'medium': 'medium',     # medium → medium
                'low': 'low',           # low → low
                'nice_to_have': 'low'   # nice_to_have → low
            }

            # Determine priority - default to medium
            priority = 'medium'

            # Calculate from functional requirements if available
            if not parsed_reqs.functional_requirements:
                pass  # Use default
            else:
                # Get highest priority (critical > high > medium > low > nice_to_have)
                priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'nice_to_have': 4}
                priorities = [req.priority.value for req in parsed_reqs.functional_requirements]
                highest_priority = min(priorities, key=lambda p: priority_order.get(p, 2))
                priority = priority_map.get(highest_priority, 'medium')

            # Calculate story points based on number of requirements
            # Must use Fibonacci numbers: [1, 2, 3, 5, 8, 13]
            total_reqs = len(parsed_reqs.functional_requirements) + len(parsed_reqs.non_functional_requirements)
            fibonacci = [1, 2, 3, 5, 8, 13]
            # Find closest Fibonacci number
            story_points = min(fibonacci, key=lambda x: abs(x - total_reqs))

            # Create card using builder pattern
            card = (board.new_card(card_id, title)
                   .with_description(parsed_reqs.executive_summary or requirements_text[:500])
                   .with_priority(priority)
                   .with_story_points(story_points)
                   .build())

            # Add requirements file reference
            card['requirements_file'] = args.requirements_file
            card['metadata'] = card.get('metadata', {})
            card['metadata']['auto_created'] = True
            card['metadata']['created_from'] = args.requirements_file

            board.add_card(card)

            print(f"✅ Created card: {card_id}")
            print(f"   Title: {title}")
            print(f"   Priority: {card['priority']}")
            print(f"   Story Points: {card['story_points']}")

            return card_id

        def _attach_requirements_to_card():
            """Strategy: Attach requirements file to existing card"""
            card, _ = board._find_card(args.card_id)

            # Guard: Card not found
            if not card:
                print(f"⚠️  Card {args.card_id} not found - requirements file will be used from context")
                return args.card_id

            # Card found - attach requirements
            board.update_card(args.card_id, {"requirements_file": args.requirements_file})
            print(f"✅ Added requirements file to card: {args.requirements_file}")
            return args.card_id

        def _use_existing_card():
            """Strategy: Use existing card without requirements file"""
            return args.card_id

        # Dispatch table: O(1) strategy selection
        requirements_strategy = {
            (True, False): _create_card_from_requirements,    # requirements file, no card
            (True, True): _attach_requirements_to_card,       # requirements file + card
            (False, True): _use_existing_card,                # card only
        }

        # Execute appropriate strategy
        strategy_key = (bool(args.requirements_file), bool(args.card_id))
        handler = requirements_strategy.get(strategy_key)

        if handler:
            args.card_id = handler()

        # Create orchestrator with injected dependencies
        orchestrator = ArtemisOrchestrator(
            card_id=args.card_id,
            board=board,
            messenger=messenger,
            rag=rag,
            config=config,
            resume=args.resume
        )

        # Run pipeline
        if args.full:
            from orchestrator.pipeline_execution import run_full_pipeline
            result = run_full_pipeline(orchestrator)
            print(f"\n✅ Pipeline completed: {result['status']}")
        else:
            print("Use --full to run the complete pipeline")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("💡 Run with --config-report to see full configuration\n")
        sys.exit(1)
    except Exception as e:
        raise create_wrapped_exception(
            e,
            PipelineStageError,
            "Pipeline orchestrator execution failed",
            {
                "card_id": args.card_id
            }
        )
