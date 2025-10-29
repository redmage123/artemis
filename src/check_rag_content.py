from artemis_logger import get_logger
logger = get_logger('check_rag_content')
'\nCheck RAG Database Content for Django and React\n'
from rag_agent import RAGAgent
from collections import Counter

def _print_sources_from_results(results, category_name, max_display=5):
    """
    Helper method to extract and print unique sources from query results.

    Args:
        results: List of query results
        category_name: Name of the category for display
        max_display: Maximum number of sources to display

    Returns:
        Set of unique sources found
    """
    if not results:
        
        logger.log(f'   ❌ No {category_name} content found', 'INFO')
        return set()
    
    logger.log(f'\n✅ Found {len(results)} {category_name}-related artifacts', 'INFO')
    sources = set()
    for result in results[:max_display]:
        metadata = result.get('metadata', {})
        source = metadata.get('book_title', metadata.get('file_name', 'Unknown'))
        sources.add(source)
        
        logger.log(f'   - {source}', 'INFO')
    return sources

def _print_django_content_section(rag):
    """Search for and display Django content."""
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('🐍 DJANGO CONTENT', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    django_results = rag.query_similar(query_text='Django web framework forms models views templates', top_k=10, artifact_types=['code_example'])
    django_sources = _print_sources_from_results(django_results, 'Django')
    if django_sources:
        
        logger.log(f'\n   Total unique Django sources: {len(django_sources)}', 'INFO')
    return django_results

def _print_react_content_section(rag):
    """Search for and display React content."""
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('⚛️  REACT CONTENT', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    react_results = rag.query_similar(query_text='React components hooks useState useEffect JSX frontend', top_k=10, artifact_types=['code_example'])
    react_sources = _print_sources_from_results(react_results, 'React')
    if react_sources:
        
        logger.log(f'\n   Total unique React sources: {len(react_sources)}', 'INFO')
    return react_results

def _print_forms_content_section(rag):
    """Search for and display forms content."""
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('📝 FORMS & VALIDATION CONTENT', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    forms_results = rag.query_similar(query_text='form validation input field submit handling', top_k=10, artifact_types=['code_example'])
    _print_sources_from_results(forms_results, 'form')
    return forms_results

def _print_fullstack_content_section(rag):
    """Search for and display full-stack content."""
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('🔗 FULL-STACK INTEGRATION CONTENT', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    fullstack_results = rag.query_similar(query_text='REST API backend frontend integration database', top_k=10, artifact_types=['code_example'])
    _print_sources_from_results(fullstack_results, 'full-stack')
    return fullstack_results

def _print_verdict_both_technologies():
    """Print verdict when both Django and React content are available."""
    
    logger.log('\n🎯 VERDICT: Artemis should be capable of producing quality', 'INFO')
    
    logger.log('   output for Django backends and React frontends with the', 'INFO')
    
    logger.log('   reference material now available in the RAG database.', 'INFO')

def _print_verdict_react_only():
    """Print verdict when only React content is available."""
    
    logger.log('\n⚠️  VERDICT: React support is good, but Django content may be limited.', 'INFO')
    
    logger.log('   Consider uploading more Django reference material.', 'INFO')

def _print_verdict_django_only():
    """Print verdict when only Django content is available."""
    
    logger.log('\n⚠️  VERDICT: Django support is good, but React content may be limited.', 'INFO')
    
    logger.log('   Upload more React reference material.', 'INFO')

def _print_verdict_limited_content():
    """Print verdict when both technologies have limited content."""
    
    logger.log('\n❌ VERDICT: Limited Django and React content. More reference', 'INFO')
    
    logger.log('   material needed for quality output.', 'INFO')

def _print_assessment_summary(django_results, react_results):
    """
    Print assessment summary based on available Django and React content.

    Args:
        django_results: Results from Django content query
        react_results: Results from React content query
    """
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('ASSESSMENT SUMMARY', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    has_django = len(django_results) > 0 if django_results else False
    has_react = len(react_results) > 0 if react_results else False
    
    logger.log(f"\n{('✅' if has_django else '❌')} Django backend development support", 'INFO')
    
    logger.log(f"{('✅' if has_react else '❌')} React frontend development support", 'INFO')
    
    logger.log(f"{('✅' if has_django and has_react else '❌')} Full-stack Django + React capability", 'INFO')
    if has_django and has_react:
        _print_verdict_both_technologies()
        return
    if has_react and (not has_django):
        _print_verdict_react_only()
        return
    if has_django and (not has_react):
        _print_verdict_django_only()
        return
    _print_verdict_limited_content()

def main():
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('RAG DATABASE CONTENT ANALYSIS', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=False)
    stats = rag.get_stats()
    
    logger.log('\n📊 Overall Statistics:', 'INFO')
    
    logger.log(f"   Total artifacts: {stats['total_artifacts']}", 'INFO')
    
    logger.log(f"   Code examples: {stats['by_type'].get('code_example', 0)}", 'INFO')
    django_results = _print_django_content_section(rag)
    react_results = _print_react_content_section(rag)
    _print_forms_content_section(rag)
    _print_fullstack_content_section(rag)
    _print_assessment_summary(django_results, react_results)
    
    logger.log('=' * 70 + '\n', 'INFO')
if __name__ == '__main__':
    main()