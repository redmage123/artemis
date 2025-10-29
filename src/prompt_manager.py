from artemis_logger import get_logger
logger = get_logger('prompt_manager')
'\nWHY: Provide backward compatibility wrapper for existing code.\nRESPONSIBILITY: Redirect to new modular prompt_management package.\nPATTERNS: Facade pattern, deprecation wrapper.\n\nBACKWARD COMPATIBILITY WRAPPER\n================================\n\nThis module maintains backward compatibility with existing code that\nimports from prompt_manager.py. All functionality has been moved to\nthe modular prompt_management/ package.\n\nUsage (Legacy - Still Supported):\n    from prompt_manager import PromptManager, PromptTemplate\n\nUsage (New - Recommended):\n    from prompt_management import PromptManager, PromptTemplate\n\nThe legacy imports will continue to work, but new code should use\nthe prompt_management package directly.\n\nDEPTH Framework:\n- D: Define Multiple Perspectives\n- E: Establish Clear Success Metrics\n- P: Provide Context Layers\n- T: Task Breakdown\n- H: Human Feedback Loop (Self-Critique)\n'
from coding_standards import CODING_STANDARDS_ALL_LANGUAGES
from prompt_management import PromptManager, PromptTemplate, PromptContext, RenderedPrompt, ReasoningStrategyType, TemplateLoader, VariableSubstitutor, PromptFormatter, PromptBuilder, PromptBuilderFactory, PromptRepository
from typing import Dict, List, Optional, Any

def create_default_prompts(prompt_manager: PromptManager):
    """
    WHY: Create default prompts for Artemis agents with DEPTH framework.
    RESPONSIBILITY: Initialize system with standard prompt templates.
    PATTERNS: Factory function for default data.

    Create default prompts for Artemis agents with DEPTH framework applied.
    This function is preserved for backward compatibility.

    Args:
        prompt_manager: PromptManager instance
    """
    prompt_manager.store_prompt(name='developer_conservative_implementation', category='developer_agent', perspectives=['Senior Software Engineer with 15+ years focusing on reliability and maintainability', 'QA Engineer who prioritizes testability and edge case handling', 'Tech Lead who reviews code for SOLID principles and best practices'], success_metrics=['Code compiles without syntax errors', 'Returns valid JSON matching expected schema', 'Includes comprehensive unit tests (85%+ coverage)', 'Follows SOLID principles (validated against checklist)', "No generic AI clichés like 'robust', 'delve into', 'leverage'", 'Clear, production-ready implementation (not placeholder code)'], context_layers={'developer_type': 'conservative', 'approach': 'Proven patterns, stability over innovation', 'code_quality': 'Production-ready, battle-tested solutions', 'testing': 'TDD with comprehensive test coverage', 'principles': 'SOLID, DRY, KISS, YAGNI'}, task_breakdown=['Analyze the task requirements and ADR architectural decisions', 'Identify all edge cases and error conditions that need handling', 'Design the solution using proven design patterns', 'Write failing tests first (TDD approach)', 'Implement the solution to make tests pass', 'Refactor for SOLID principles and code clarity', 'Self-validate: Check JSON format, test coverage, and code quality'], self_critique='Before responding, validate your implementation:\n1. Does the JSON parse without errors?\n2. Are all required fields present in the JSON response?\n3. Is test coverage >= 85%?\n4. Did you avoid AI clichés and generic language?\n5. Is this production-ready code (not TODO placeholders)?\n6. Does it follow SOLID principles?\n\nIf any answer is NO, revise your implementation.', system_message=f'You are {{developer_name}}, a conservative senior software developer with 15+ years of experience.\n\nYour core principles:\n- Stability and reliability over clever tricks\n- Proven patterns over experimental approaches\n- Comprehensive testing and error handling\n- SOLID principles strictly applied\n- Production-ready code (no TODOs or placeholders)\n\n{CODING_STANDARDS_ALL_LANGUAGES}\n\n**NOTEBOOK TASKS:**\nIf the task requires creating Jupyter notebooks (.ipynb files):\n- Create notebooks in notebooks/ directory\n- Focus on content quality, visualizations, and narrative\n- Do NOT create pytest tests for notebook tasks\n- Validation checks notebook structure only (valid JSON, cells exist)\n- Optional: Create src/ directory only if notebook needs helper modules\n- Tests field can be null or minimal for notebook deliverables\n\nYou MUST respond with valid JSON only - no explanations, no markdown, just pure JSON.', user_template='Implement the following task:\n\n**Task:** {task_title}\n\n**Architecture Decision (ADR):**\n{adr_content}\n\n**Code Review Feedback (if available):**\n{code_review_feedback}\n\n**Response Format:**\nReturn a JSON object with this exact structure:\n{{\n  "approach": "Brief description of your approach",\n  "implementation": {{\n    "filename": "your_solution.py",\n    "content": "Complete implementation code"\n  }},\n  "tests": {{\n    "filename": "test_your_solution.py",\n    "content": "Complete test code"\n  }},\n  "explanation": "Brief explanation of key decisions"\n}}', tags=['developer', 'conservative', 'production-ready', 'TDD'], version='1.0')
    
    logger.log('[PromptManager] Created default prompts with DEPTH framework', 'INFO')
if __name__ == '__main__':
    from rag_agent import RAGAgent
    rag = RAGAgent(db_path='db', verbose=True)
    pm = PromptManager(rag, verbose=True)
    create_default_prompts(pm)
    prompt = pm.get_prompt('developer_conservative_implementation')
    if prompt:
        rendered = pm.render_prompt(prompt, {'developer_name': 'developer-a', 'task_title': 'Create user authentication module', 'adr_content': 'Use JWT tokens with RS256 signing...', 'code_review_feedback': 'No previous feedback'})
        
        logger.log('\n' + '=' * 70, 'INFO')
        
        logger.log('RENDERED PROMPT:', 'INFO')
        
        logger.log('=' * 70, 'INFO')
        
        logger.log('\nSYSTEM MESSAGE:', 'INFO')
        
        logger.log(rendered['system'], 'INFO')
        
        logger.log('\nUSER MESSAGE:', 'INFO')
        
        logger.log(rendered['user'][:500] + '...', 'INFO')
__all__ = ['PromptManager', 'PromptTemplate', 'PromptContext', 'RenderedPrompt', 'ReasoningStrategyType', 'TemplateLoader', 'VariableSubstitutor', 'PromptFormatter', 'PromptBuilder', 'PromptBuilderFactory', 'PromptRepository', 'create_default_prompts']