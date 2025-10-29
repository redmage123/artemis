from artemis_logger import get_logger
logger = get_logger('create_init_files')
'\nUtility script to create __init__.py files for new package structure.\n\nWHY: Efficiently create __init__.py files for all new subdirectories.\n'
from pathlib import Path
SUBDIRS = ['services/llm', 'services/storage', 'services/messaging', 'services/knowledge_graph', 'managers/build', 'managers/git', 'managers/bash', 'managers/kanban', 'agents/supervisor', 'agents/developer', 'agents/analysis', 'agents/specialized', 'pipelines/two_pass', 'pipelines/dynamic', 'pipelines/thermodynamic', 'pipelines/strategies', 'stages/requirements', 'stages/architecture', 'stages/development', 'stages/testing', 'stages/validation', 'stages/integration', 'stages/deployment', 'validators/code_standards', 'validators/signature', 'workflows/handlers', 'utilities/helpers', 'tests/unit', 'tests/integration', 'tests/advanced', 'tests/fixtures']

def create_init_files():
    """Create __init__.py files for all subdirectories."""
    src_dir = Path(__file__).parent
    for subdir in SUBDIRS:
        init_file = src_dir / subdir / '__init__.py'
        if init_file.exists():
            
            logger.log(f'✓ Already exists: {init_file}', 'INFO')
            continue
        package_name = subdir.split('/')[-1]
        parent_package = '/'.join(subdir.split('/')[:-1])
        content = f'"""\n{package_name.capitalize()} subpackage.\n\nPart of: {parent_package}\n"""\n\n__all__ = []\n'
        init_file.write_text(content)
        
        logger.log(f'✓ Created: {init_file}', 'INFO')
if __name__ == '__main__':
    create_init_files()
    
    logger.log('\n✅ All __init__.py files created successfully!', 'INFO')