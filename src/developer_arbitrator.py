from artemis_logger import get_logger
logger = get_logger('developer_arbitrator')
'\nDeveloper Arbitrator - Intelligent Winner Selection\n\nIntelligently selects the best developer solution based on multiple criteria:\n- Code review scores (security, quality, GDPR, accessibility)\n- Test coverage percentage\n- SOLID principle compliance\n- Performance metrics\n- Code simplicity (lines of code)\n- Maintainability score\n\nUses weighted multi-criteria decision analysis (MCDA)\n'
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class DeveloperScore:
    """Comprehensive developer solution score"""
    developer_name: str
    security_score: float
    quality_score: float
    gdpr_score: float
    accessibility_score: float
    overall_review_score: float
    test_coverage: float
    tests_passing: int
    tests_total: int
    solid_score: float
    lines_of_code: int
    complexity_score: float
    final_score: float = 0.0
    weighted_scores: Dict[str, float] = None

class DeveloperArbitrator:
    """
    Selects best developer solution using multi-criteria analysis

    Single Responsibility: Determine winning developer based on multiple factors
    """
    DEFAULT_WEIGHTS = {'security': 0.25, 'quality': 0.2, 'test_coverage': 0.15, 'solid_compliance': 0.15, 'gdpr': 0.1, 'accessibility': 0.05, 'simplicity': 0.05, 'maintainability': 0.05}

    def __init__(self, weights: Optional[Dict[str, float]]=None):
        """
        Initialize arbitrator

        Args:
            weights: Custom weights for criteria (default: DEFAULT_WEIGHTS)
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f'Weights must sum to 1.0, got {total}')

    def select_winner(self, dev_a_result: Dict, dev_b_result: Dict, code_review_results: List[Dict]) -> Dict:
        """
        Select winning developer solution

        Args:
            dev_a_result: Developer A results
            dev_b_result: Developer B results
            code_review_results: Code review results for both developers

        Returns:
            Dict with winner and scoring details
        """
        score_a = self._calculate_developer_score('developer-a', dev_a_result, code_review_results)
        score_b = self._calculate_developer_score('developer-b', dev_b_result, code_review_results)
        if score_a.final_score > score_b.final_score:
            winner = 'developer-a'
            winner_score = score_a
            loser_score = score_b
        else:
            winner = 'developer-b'
            winner_score = score_b
            loser_score = score_a
        margin = abs(score_a.final_score - score_b.final_score)
        return {'winner': winner, 'winner_score': winner_score.final_score, 'loser_score': loser_score.final_score, 'margin': margin, 'confidence': self._calculate_confidence(margin), 'developer_a_details': asdict(score_a), 'developer_b_details': asdict(score_b), 'breakdown': {'developer-a': score_a.weighted_scores, 'developer-b': score_b.weighted_scores}, 'reasoning': self._generate_reasoning(winner_score, loser_score)}

    def _calculate_developer_score(self, developer_name: str, dev_result: Dict, code_review_results: List[Dict]) -> DeveloperScore:
        """Calculate comprehensive score for a developer"""
        review = self._find_review(developer_name, code_review_results)
        security_score = self._extract_review_score(review, 'security', 50.0)
        quality_score = self._extract_review_score(review, 'quality', 50.0)
        gdpr_score = self._extract_review_score(review, 'gdpr', 50.0)
        accessibility_score = self._extract_review_score(review, 'accessibility', 50.0)
        overall_review_score = review.get('overall_score', 50.0) if review else 50.0
        test_results = dev_result.get('test_results', {})
        tests_passing = test_results.get('passed', 0)
        tests_total = test_results.get('total', 1)
        test_coverage = tests_passing / tests_total * 100 if tests_total > 0 else 0
        solid_score = dev_result.get('solid_score', 50.0)
        lines_of_code = dev_result.get('lines_of_code', 100)
        complexity_score = dev_result.get('complexity_score', 10.0)
        weighted_scores = {'security': security_score * self.weights['security'], 'quality': quality_score * self.weights['quality'], 'test_coverage': test_coverage * self.weights['test_coverage'], 'solid_compliance': solid_score * self.weights['solid_compliance'], 'gdpr': gdpr_score * self.weights['gdpr'], 'accessibility': accessibility_score * self.weights['accessibility'], 'simplicity': self._calculate_simplicity_score(lines_of_code) * self.weights['simplicity'], 'maintainability': self._calculate_maintainability_score(complexity_score, solid_score) * self.weights['maintainability']}
        final_score = sum(weighted_scores.values())
        return DeveloperScore(developer_name=developer_name, security_score=security_score, quality_score=quality_score, gdpr_score=gdpr_score, accessibility_score=accessibility_score, overall_review_score=overall_review_score, test_coverage=test_coverage, tests_passing=tests_passing, tests_total=tests_total, solid_score=solid_score, lines_of_code=lines_of_code, complexity_score=complexity_score, final_score=final_score, weighted_scores=weighted_scores)

    def _find_review(self, developer_name: str, code_review_results: List[Dict]) -> Optional[Dict]:
        """Find code review for specific developer"""
        for review in code_review_results:
            if review.get('developer') == developer_name:
                return review
        return None

    def _extract_review_score(self, review: Optional[Dict], category: str, default: float) -> float:
        """Extract score for specific category from review"""
        if not review:
            return default
        category_scores = review.get('category_scores', {})
        if category in category_scores:
            return category_scores[category]
        return review.get('overall_score', default)

    def _calculate_simplicity_score(self, lines_of_code: int) -> float:
        """
        Calculate simplicity score (fewer lines = higher score)

        Scoring:
        - < 100 lines: 100
        - 100-300 lines: 90-70
        - 300-500 lines: 70-50
        - > 500 lines: 50-0
        """
        if lines_of_code < 100:
            return 100.0
        if lines_of_code < 300:
            return 100 - (lines_of_code - 100) / 200 * 30
        if lines_of_code < 500:
            return 70 - (lines_of_code - 300) / 200 * 20
        return max(0, 50 - (lines_of_code - 500) / 500 * 50)

    def _calculate_maintainability_score(self, complexity: float, solid_score: float) -> float:
        """
        Calculate maintainability score

        Lower complexity + higher SOLID = more maintainable
        """
        complexity_normalized = max(0, 100 - complexity / 20 * 100)
        return complexity_normalized * 0.4 + solid_score * 0.6

    def _calculate_confidence(self, margin: float) -> str:
        """
        Calculate confidence level based on margin

        Args:
            margin: Score difference between winner and loser

        Returns:
            Confidence level (high, medium, low)
        """
        if margin > 20:
            return 'high'
        if margin > 10:
            return 'medium'
        return 'low'

    def _generate_reasoning(self, winner_score: DeveloperScore, loser_score: DeveloperScore) -> str:
        """Generate human-readable reasoning for decision"""
        reasons = []
        if winner_score.security_score > loser_score.security_score + 10:
            reasons.append(f'Superior security ({winner_score.security_score:.0f} vs {loser_score.security_score:.0f})')
        if winner_score.test_coverage > loser_score.test_coverage + 10:
            reasons.append(f'Better test coverage ({winner_score.test_coverage:.0f}% vs {loser_score.test_coverage:.0f}%)')
        if winner_score.solid_score > loser_score.solid_score + 10:
            reasons.append(f'Stronger SOLID compliance ({winner_score.solid_score:.0f} vs {loser_score.solid_score:.0f})')
        if winner_score.quality_score > loser_score.quality_score + 10:
            reasons.append(f'Higher code quality ({winner_score.quality_score:.0f} vs {loser_score.quality_score:.0f})')
        if not reasons:
            reasons.append('Marginal advantage across multiple criteria')
        return '; '.join(reasons)
if __name__ == '__main__':
    'Example usage and testing'
    
    logger.log('Developer Arbitrator - Example Usage', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    arbitrator = DeveloperArbitrator()
    dev_a_result = {'developer': 'developer-a', 'test_results': {'passed': 42, 'total': 50}, 'solid_score': 85.0, 'lines_of_code': 250, 'complexity_score': 8.5}
    dev_b_result = {'developer': 'developer-b', 'test_results': {'passed': 45, 'total': 50}, 'solid_score': 75.0, 'lines_of_code': 180, 'complexity_score': 12.0}
    code_review_results = [{'developer': 'developer-a', 'overall_score': 85, 'category_scores': {'security': 90, 'quality': 85, 'gdpr': 80, 'accessibility': 75}}, {'developer': 'developer-b', 'overall_score': 82, 'category_scores': {'security': 85, 'quality': 90, 'gdpr': 75, 'accessibility': 80}}]
    result = arbitrator.select_winner(dev_a_result, dev_b_result, code_review_results)
    
    logger.log(f"\n🏆 Winner: {result['winner']}", 'INFO')
    
    logger.log(f"   Score: {result['winner_score']:.2f}/100", 'INFO')
    
    logger.log(f"   Margin: {result['margin']:.2f} points", 'INFO')
    
    logger.log(f"   Confidence: {result['confidence']}", 'INFO')
    
    logger.log(f"\n💡 Reasoning: {result['reasoning']}", 'INFO')
    
    logger.log(f'\n📊 Detailed Breakdown:', 'INFO')
    
    logger.log(f'   Developer A:', 'INFO')
    for criterion, score in result['breakdown']['developer-a'].items():
        
        logger.log(f'      {criterion}: {score:.2f}', 'INFO')
    
    logger.log(f'\n   Developer B:', 'INFO')
    for criterion, score in result['breakdown']['developer-b'].items():
        
        logger.log(f'      {criterion}: {score:.2f}', 'INFO')
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('✅ Developer arbitration working correctly!', 'INFO')