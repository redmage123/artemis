from artemis_logger import get_logger
logger = get_logger('check_upload_status')
'\nCheck upload status and what React books are in RAG\n'
from rag_agent import RAGAgent
from collections import Counter

def main():
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('UPLOAD STATUS CHECK', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    rag = RAGAgent(db_path='../.artemis_data/rag_db', verbose=False)
    stats = rag.get_stats()
    
    logger.log('\n📊 Overall Statistics:', 'INFO')
    
    logger.log(f"   Total artifacts: {stats['total_artifacts']}", 'INFO')
    
    logger.log(f"   Code examples: {stats['by_type'].get('code_example', 0)}", 'INFO')
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('⚛️  REACT BOOKS IN DATABASE', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    react_results = rag.query_similar(query_text='React web development frontend components hooks', top_k=50, artifact_types=['code_example'])
    react_books = {}
    for result in react_results:
        metadata = result.get('metadata', {})
        book_title = metadata.get('book_title', 'Unknown')
        if 'react' in book_title.lower():
            if book_title not in react_books:
                react_books[book_title] = 0
            react_books[book_title] += 1
    if react_books:
        
        logger.log(f'\n✅ Found {len(react_books)} unique React books:\n', 'INFO')
        for title, count in sorted(react_books.items(), key=lambda x: x[1], reverse=True):
            
            logger.log(f'   📚 {title}', 'INFO')
            
            logger.log(f'      └─ {count} chunks\n', 'INFO')
    else:
        
        logger.log('   ❌ No React books found', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    
    logger.log('🐍 DJANGO BOOKS IN DATABASE', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    django_results = rag.query_similar(query_text='Django web framework backend database models', top_k=50, artifact_types=['code_example'])
    django_books = {}
    for result in django_results:
        metadata = result.get('metadata', {})
        book_title = metadata.get('book_title', 'Unknown')
        if 'django' in book_title.lower():
            if book_title not in django_books:
                django_books[book_title] = 0
            django_books[book_title] += 1
    if django_books:
        
        logger.log(f'\n✅ Found {len(django_books)} unique Django books:\n', 'INFO')
        for title, count in sorted(django_books.items(), key=lambda x: x[1], reverse=True):
            
            logger.log(f'   📚 {title}', 'INFO')
            
            logger.log(f'      └─ {count} chunks\n', 'INFO')
    else:
        
        logger.log('   ❌ No Django books found', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    
    logger.log('EXPECTED REACT BOOKS', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    expected = ['Web Forms with React - Build Robust and Scalable Forms', "The React UX Architect's Handbook - Design Thinking Strategies", 'React 18 Design Patterns and Best Practices (4th Edition)', 'Fullstack React - The Complete Guide to ReactJS and Friends', 'The Complete Developer - Full Stack with TypeScript, React, Next.js']
    
    logger.log('\nExpected to upload:', 'INFO')
    for i, title in enumerate(expected, 1):
        status = '✅' if any((title.lower() in book.lower() for book in react_books.keys())) else '❌'
        
        logger.log(f'   {status} {i}. {title}', 'INFO')
    
    logger.log('\n' + '=' * 70 + '\n', 'INFO')
if __name__ == '__main__':
    main()