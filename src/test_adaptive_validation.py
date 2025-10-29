"""
Adaptive Pipeline Validation Tests

WHY: Validate that adaptive complexity detection works correctly on historical tasks
RESPONSIBILITY: Test against known tasks and verify correct path selection
PATTERNS: Test-driven validation with historical data

USAGE:
    # Run all validation tests
    python3 test_adaptive_validation.py

    # Run with detailed output
    python3 test_adaptive_validation.py --verbose

    # Generate validation report
    python3 test_adaptive_validation.py --report
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
sys.path.insert(0, str(Path(__file__).parent))
from artemis_logger import get_logger
from adaptive_pipeline_builder import AdaptivePipelineBuilder, TaskComplexityDetector, TaskComplexity, PipelinePath
logger = get_logger(__name__)


@dataclass
class ValidationTestCase:
    """Test case for adaptive pipeline validation."""
    task_id: str
    title: str
    description: str
    expected_complexity: TaskComplexity
    expected_path: PipelinePath
    task_type: str
    estimated_hours: float
    metadata: Dict[str, Any] = None


VALIDATION_TEST_CASES = [ValidationTestCase(task_id='test-simple-html',
    title='Create HTML Presentation Page', description=
    'Create a single HTML page with CSS styling to showcase project features',
    expected_complexity=TaskComplexity.SIMPLE, expected_path=PipelinePath.
    FAST, task_type='feature', estimated_hours=5, metadata={'indicators': [
    'html', 'single file', 'css', 'presentation']}), ValidationTestCase(
    task_id='test-simple-refactor', title=
    'Refactor User Authentication to Use Async/Await', description=
    """Simple refactoring task to modernize the user authentication module:

- Replace callback-based authentication with async/await pattern
- Update function signatures to use async def
- Ensure all database calls use await
- Update tests to handle async functions"""
    , expected_complexity=TaskComplexity.SIMPLE, expected_path=PipelinePath
    .FAST, task_type='refactor', estimated_hours=8, metadata={'indicators':
    ['refactor', 'modernize', 'async']}), ValidationTestCase(task_id=
    'test-simple-bugfix', title='Fix Login Button Alignment', description=
    'Fix CSS alignment issue where login button is not centered on mobile devices'
    , expected_complexity=TaskComplexity.SIMPLE, expected_path=PipelinePath
    .FAST, task_type='bugfix', estimated_hours=2, metadata={'indicators': [
    'css', 'fix', 'alignment', 'mobile']}), ValidationTestCase(task_id=
    'test-medium-api', title='Add REST API Endpoint for User Profile',
    description=
    """Add new REST API endpoint:

- GET /api/users/:id/profile
- Include user details, preferences, and activity
- Add authentication middleware
- Write integration tests
- Update API documentation"""
    , expected_complexity=TaskComplexity.MEDIUM, expected_path=PipelinePath
    .MEDIUM, task_type='feature', estimated_hours=16, metadata={
    'indicators': ['api', 'rest', 'endpoint', 'authentication', 'tests']}),
    ValidationTestCase(task_id='test-medium-dashboard', title=
    'Build Analytics Dashboard', description=
    """Create analytics dashboard with:

- Chart.js visualizations (line, bar, pie charts)
- Real-time data updates
- Filter by date range
- Export to CSV
- Responsive design"""
    , expected_complexity=TaskComplexity.MEDIUM, expected_path=PipelinePath
    .MEDIUM, task_type='feature', estimated_hours=32, metadata={
    'indicators': ['dashboard', 'charts', 'analytics', 'real-time']}),
    ValidationTestCase(task_id='test-complex-chat', title=
    'Build Real-Time WebSocket Chat Service with Redis Pub/Sub',
    description=
    """Build a comprehensive real-time chat service:

- WebSocket-based real-time communication
- Redis Pub/Sub for message distribution across multiple server instances
- User authentication and session management
- Message persistence in PostgreSQL database
- Message history retrieval with pagination
- Typing indicators and read receipts
- File upload support (images, documents)
- Rate limiting and spam prevention
- End-to-end encryption for private messages
- Admin dashboard for monitoring active connections
- Support for chat rooms and direct messages
- Notification system for offline users"""
    , expected_complexity=TaskComplexity.COMPLEX, expected_path=
    PipelinePath.FULL, task_type='feature', estimated_hours=120, metadata={
    'indicators': ['websocket', 'redis', 'database', 'authentication',
    'encryption', 'real-time', 'microservice']}), ValidationTestCase(
    task_id='test-complex-ecommerce', title='Build E-Commerce Platform',
    description=
    """Build full e-commerce platform:

- Product catalog with search and filters
- Shopping cart and checkout flow
- Payment processing (Stripe, PayPal)
- Order management system
- Inventory tracking
- User authentication and profiles
- Admin dashboard
- Email notifications
- Analytics and reporting
- Security and GDPR compliance
- Performance optimization
- Database design (products, orders, users)
- API for mobile apps"""
    , expected_complexity=TaskComplexity.COMPLEX, expected_path=
    PipelinePath.FULL, task_type='feature', estimated_hours=200, metadata={
    'indicators': ['payment', 'database', 'authentication', 'security',
    'gdpr', 'api', 'microservice', 'scale']})]


class AdaptiveValidationTester:
    """Test adaptive pipeline selection with known test cases."""

    def __init__(self, verbose: bool=False):
        """
        Initialize validation tester.

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.detector = TaskComplexityDetector()
        self.builder = AdaptivePipelineBuilder()
        self.results = []

    def run_test_case(self, test_case: ValidationTestCase) ->Dict[str, Any]:
        """
        Run a single test case.

        Args:
            test_case: Test case to run

        Returns:
            Test result dictionary
        """
        if self.verbose:
            logger.log(f"\n{'─' * 80}", 'INFO')
            logger.log(f'Testing: {test_case.title}', 'INFO')
            logger.log(f"{'─' * 80}", 'INFO')
        requirements = {'functional': [{'id': 'FR-1', 'description':
            test_case.description, 'priority': 'high'}], 'non_functional': []}
        card = {'title': test_case.title, 'description': test_case.
            description, 'task_type': test_case.task_type,
            'estimated_hours': test_case.estimated_hours}
        detected_complexity = self.detector.detect(requirements, card)
        pipeline_config = self.builder.build_pipeline(requirements, card)
        detected_path = pipeline_config['path']
        complexity_match = (detected_complexity.value == test_case.
            expected_complexity.value)
        path_match = detected_path == test_case.expected_path.value
        result = {'task_id': test_case.task_id, 'title': test_case.title,
            'expected_complexity': test_case.expected_complexity.value,
            'detected_complexity': detected_complexity.value,
            'complexity_match': complexity_match, 'expected_path':
            test_case.expected_path.value, 'detected_path': detected_path,
            'path_match': path_match, 'estimated_duration': pipeline_config
            ['estimated_duration_minutes'], 'num_stages': len(
            pipeline_config['stages']), 'reasoning': pipeline_config[
            'reasoning']}
        if self.verbose:
            logger.log(
                f"""
   Expected: {test_case.expected_complexity.value.upper()} → {test_case.expected_path.value.upper()}"""
                , 'INFO')
            logger.log(
                f'   Detected: {detected_complexity.value.upper()} → {detected_path.upper()}'
                , 'INFO')
            logger.log(
                f"   Match: {'✅ PASS' if complexity_match and path_match else '❌ FAIL'}"
                , 'INFO')
            if not complexity_match or not path_match:
                logger.log(f"   Reasoning: {pipeline_config['reasoning']}",
                    'INFO')
        self.results.append(result)
        return result

    def run_all_tests(self) ->Dict[str, Any]:
        """
        Run all validation test cases.

        Returns:
            Summary of test results
        """
        logger.log('\n' + '=' * 80, 'INFO')
        logger.log('🧪 ADAPTIVE PIPELINE VALIDATION TESTS', 'INFO')
        logger.log('=' * 80 + '\n', 'INFO')
        for test_case in VALIDATION_TEST_CASES:
            self.run_test_case(test_case)
        return self.generate_summary()

    def generate_summary(self) ->Dict[str, Any]:
        """
        Generate summary of test results.

        Returns:
            Summary dictionary
        """
        total = len(self.results)
        complexity_correct = sum(1 for r in self.results if r[
            'complexity_match'])
        path_correct = sum(1 for r in self.results if r['path_match'])
        both_correct = sum(1 for r in self.results if r['complexity_match'] and
            r['path_match'])
        complexity_accuracy = (complexity_correct / total * 100 if total > 
            0 else 0)
        path_accuracy = path_correct / total * 100 if total > 0 else 0
        overall_accuracy = both_correct / total * 100 if total > 0 else 0
        summary = {'total_tests': total, 'complexity_correct':
            complexity_correct, 'path_correct': path_correct,
            'both_correct': both_correct, 'complexity_accuracy':
            complexity_accuracy, 'path_accuracy': path_accuracy,
            'overall_accuracy': overall_accuracy, 'results': self.results}
        return summary

    def display_summary(self, summary: Dict[str, Any]):
        """
        Display test summary.

        Args:
            summary: Summary dictionary
        """
        logger.log('\n' + '=' * 80, 'INFO')
        logger.log('📊 VALIDATION SUMMARY', 'INFO')
        logger.log('=' * 80 + '\n', 'INFO')
        logger.log(f"   Total Test Cases: {summary['total_tests']}", 'INFO')
        logger.log(
            f"   Complexity Detection Accuracy: {summary['complexity_accuracy']:.1f}% ({summary['complexity_correct']}/{summary['total_tests']})"
            , 'INFO')
        logger.log(
            f"   Path Selection Accuracy: {summary['path_accuracy']:.1f}% ({summary['path_correct']}/{summary['total_tests']})"
            , 'INFO')
        logger.log(
            f"   Overall Accuracy: {summary['overall_accuracy']:.1f}% ({summary['both_correct']}/{summary['total_tests']})"
            , 'INFO')
        failed = [r for r in summary['results'] if not (r[
            'complexity_match'] and r['path_match'])]
        if failed:
            logger.log('\n   ❌ Failed Tests:', 'INFO')
            for result in failed:
                logger.log(f"      • {result['title']}", 'INFO')
                if not result['complexity_match']:
                    logger.log(
                        f"        Expected: {result['expected_complexity']}, Got: {result['detected_complexity']}"
                        , 'INFO')
                if not result['path_match']:
                    logger.log(
                        f"        Expected: {result['expected_path']}, Got: {result['detected_path']}"
                        , 'INFO')
        else:
            logger.log('\n   ✅ All tests passed!', 'INFO')
        logger.log('\n' + '─' * 80, 'INFO')
        logger.log('📈 SYSTEM GRADE', 'INFO')
        logger.log('─' * 80, 'INFO')
        accuracy = summary['overall_accuracy']
        if accuracy >= 90:
            grade = 'A'
            assessment = 'Excellent! System is highly accurate.'
        elif accuracy >= 80:
            grade = 'B'
            assessment = 'Good! Minor tuning recommended.'
        elif accuracy >= 70:
            grade = 'C'
            assessment = 'Fair. Needs tuning and more indicators.'
        elif accuracy >= 60:
            grade = 'D'
            assessment = 'Poor. Significant tuning required.'
        else:
            grade = 'F'
            assessment = 'Failing. Major overhaul needed.'
        logger.log(f'\n   Grade: {grade} ({accuracy:.1f}%)', 'INFO')
        logger.log(f'   Assessment: {assessment}', 'INFO')
        logger.log('\n' + '=' * 80 + '\n', 'INFO')


def load_kanban_test_cases() ->List[ValidationTestCase]:
    """
    Load test cases from kanban board.

    Returns:
        List of validation test cases from kanban board
    """
    kanban_path = Path(
        '/home/bbrelin/src/repos/artemis/.agents/agile/kanban_board.json')
    if not kanban_path.exists():
        logger.log('⚠️  Kanban board not found, using built-in test cases only'
            , 'INFO')
        return []
    with open(kanban_path, 'r') as f:
        board_data = json.load(f)
    test_cases = []
    for column_name, column_data in board_data.get('columns', {}).items():
        for card in column_data.get('cards', []):
            card_id = card.get('card_id', '')
            if 'test' in card_id.lower():
                metadata = card.get('metadata', {})
                complexity = metadata.get('complexity', 'medium')
                complexity_map = {'simple': (TaskComplexity.SIMPLE,
                    PipelinePath.FAST), 'medium': (TaskComplexity.MEDIUM,
                    PipelinePath.MEDIUM), 'complex': (TaskComplexity.
                    COMPLEX, PipelinePath.FULL)}
                expected_complexity, expected_path = complexity_map.get(
                    complexity, (TaskComplexity.MEDIUM, PipelinePath.MEDIUM))
                test_case = ValidationTestCase(task_id=card_id, title=card[
                    'title'], description=card['description'],
                    expected_complexity=expected_complexity, expected_path=
                    expected_path, task_type=metadata.get('task_type',
                    'feature'), estimated_hours=metadata.get(
                    'estimated_hours', 16), metadata=metadata)
                test_cases.append(test_case)
    return test_cases


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=
        'Adaptive Pipeline Validation Tests', formatter_class=argparse.
        RawDescriptionHelpFormatter, epilog=
        """
Examples:
  # Run all tests
  %(prog)s

  # Run with verbose output
  %(prog)s --verbose

  # Generate validation report
  %(prog)s --report
        """
        )
    parser.add_argument('--verbose', action='store_true', help=
        'Enable verbose output')
    parser.add_argument('--report', action='store_true', help=
        'Generate detailed validation report')
    parser.add_argument('--include-kanban', action='store_true', help=
        'Include test cases from kanban board')
    args = parser.parse_args()
    try:
        tester = AdaptiveValidationTester(verbose=args.verbose or args.report)
        test_cases = VALIDATION_TEST_CASES.copy()
        if args.include_kanban:
            kanban_tests = load_kanban_test_cases()
            if kanban_tests:
                logger.log(
                    f'✅ Loaded {len(kanban_tests)} test cases from kanban board'
                    , 'INFO')
                test_cases.extend(kanban_tests)
        summary = tester.run_all_tests()
        tester.display_summary(summary)
        if args.report:
            report_path = Path('/tmp/adaptive_validation_report.json')
            with open(report_path, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.log(f'📄 Detailed report saved to: {report_path}', 'INFO')
        if summary['overall_accuracy'] < 70:
            logger.log('❌ Validation failed: accuracy below 70%', 'ERROR')
            sys.exit(1)
        else:
            logger.log('✅ Validation passed!', 'INFO')
            sys.exit(0)
    except Exception as e:
        logger.log(f'❌ Validation error: {e}', 'ERROR')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
