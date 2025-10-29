"""
BACKWARD COMPATIBILITY WRAPPER

WHY: Maintains backward compatibility with existing code
RESPONSIBILITY: Re-exports classes from refactored java_framework package
PATTERNS: Facade Pattern, Adapter Pattern

This module serves as a backward compatibility wrapper for the refactored
java_framework package. All functionality has been moved to the java_framework/
package with improved modularity and maintainability.

Old usage (still works):
    from java_web_framework_detector import JavaWebFrameworkDetector

    detector = JavaWebFrameworkDetector(project_dir="/path/to/project")
    analysis = detector.analyze()

New usage (recommended):
    from java_framework import JavaWebFrameworkAnalyzer

    analyzer = JavaWebFrameworkAnalyzer(project_dir="/path/to/project")
    analysis = analyzer.analyze()

MIGRATION NOTE:
The class JavaWebFrameworkDetector has been renamed to JavaWebFrameworkAnalyzer
in the new package to better reflect its purpose. This wrapper maintains the old
name for backward compatibility.
"""
from java_framework.models import JavaWebFramework, JavaWebFrameworkAnalysis, TemplateEngine, WebServer
from java_framework.analyzer import JavaWebFrameworkAnalyzer

class JavaWebFrameworkDetector(JavaWebFrameworkAnalyzer):
    """
    WHY: Backward compatibility alias for JavaWebFrameworkAnalyzer
    RESPONSIBILITY: Maintains old class name for existing code
    PATTERNS: Adapter Pattern

    DEPRECATED: Use java_framework.JavaWebFrameworkAnalyzer instead
    """
    pass
if __name__ == '__main__':
    import argparse
    import json
    import logging
    parser = argparse.ArgumentParser(description='Java Web Framework Detector and Analyzer')
    parser.add_argument('--project-dir', default='.', help='Java project directory')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    detector = JavaWebFrameworkDetector(project_dir=args.project_dir)
    analysis = detector.analyze()
    if args.json:
        _output_json_format(analysis)
    else:
        _output_human_readable_format(analysis)

def _output_json_format(analysis: JavaWebFrameworkAnalysis) -> None:
    """Output analysis results in JSON format"""
    import json
    result = {'framework': analysis.primary_framework.value, 'framework_version': analysis.framework_version, 'web_server': analysis.web_server.value, 'web_server_version': analysis.web_server_version, 'build_system': analysis.build_system, 'template_engines': [e.value for e in analysis.template_engines], 'database_technologies': analysis.database_technologies, 'databases': analysis.databases, 'has_rest_api': analysis.has_rest_api, 'rest_framework': analysis.rest_framework, 'has_graphql': analysis.has_graphql, 'security_frameworks': analysis.security_frameworks, 'test_frameworks': analysis.test_frameworks, 'architecture': 'Microservices' if analysis.is_microservices else 'Monolith'}
    
    logger.log(json.dumps(result, indent=2), 'INFO')

def _output_human_readable_format(analysis: JavaWebFrameworkAnalysis) -> None:
    """Output analysis results in human-readable format"""
    _print_header()
    _print_core_info(analysis)
    _print_optional_info(analysis)
    _print_footer()

def _print_header() -> None:
    """Print report header"""
    
    logger.log(f"\n{'=' * 60}", 'INFO')
    
    logger.log(f'Java Web Framework Analysis', 'INFO')
    
    logger.log(f"{'=' * 60}", 'INFO')

def _print_core_info(analysis: JavaWebFrameworkAnalysis) -> None:
    """Print core framework information"""
    
    logger.log(f'Framework:     {analysis.primary_framework.value}', 'INFO')
    if analysis.framework_version:
        
        logger.log(f'Version:       {analysis.framework_version}', 'INFO')
    
    logger.log(f'Build System:  {analysis.build_system}', 'INFO')
    
    logger.log(f'Web Server:    {analysis.web_server.value}', 'INFO')
    if analysis.web_server_version:
        
        logger.log(f'Server Version: {analysis.web_server_version}', 'INFO')

def _print_optional_info(analysis: JavaWebFrameworkAnalysis) -> None:
    """Print optional technology information"""
    if analysis.template_engines:
        
        logger.log(f"Templates:     {', '.join((e.value for e in analysis.template_engines))}", 'INFO')
    if analysis.database_technologies:
        
        logger.log(f"Data Access:   {', '.join(analysis.database_technologies)}", 'INFO')
    if analysis.databases:
        
        logger.log(f"Databases:     {', '.join(analysis.databases)}", 'INFO')
    if analysis.has_rest_api:
        
        logger.log(f'REST API:      Yes ({analysis.rest_framework})', 'INFO')
    if analysis.has_graphql:
        
        logger.log(f'GraphQL:       Yes', 'INFO')
    if analysis.security_frameworks:
        
        logger.log(f"Security:      {', '.join(analysis.security_frameworks)}", 'INFO')
    if analysis.test_frameworks:
        
        logger.log(f"Testing:       {', '.join(analysis.test_frameworks)}", 'INFO')
    
    logger.log(f"Architecture:  {('Microservices' if analysis.is_microservices else 'Monolith')}", 'INFO')
    if analysis.modules:
        
        logger.log(f"Modules:       {', '.join(analysis.modules)}", 'INFO')

def _print_footer() -> None:
    """Print report footer"""
    
    logger.log(f"{'=' * 60}\n", 'INFO')
__all__ = ['JavaWebFrameworkDetector', 'JavaWebFramework', 'JavaWebFrameworkAnalysis', 'WebServer', 'TemplateEngine']