#!/usr/bin/env python3
"""
Tests for Enhanced Intelligent Router with Advanced Feature Integration

WHY these tests: Validate that enhanced router correctly:
    - Calculates task uncertainty
    - Identifies risk factors
    - Recommends appropriate pipeline modes
    - Creates rich context for advanced features
    - Maintains backward compatibility with base router
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys

# Import the enhanced router
from intelligent_router_enhanced import (
    IntelligentRouterEnhanced,
    RiskFactor,
    UncertaintyAnalysis,
    AdvancedFeatureRecommendation,
    EnhancedRoutingDecision
)

# Import base router types
from intelligent_router import TaskRequirements, StageDecision

# Import advanced pipeline types
from advanced_pipeline_integration import PipelineMode, AdvancedPipelineConfig


class TestUncertaintyCalculation(unittest.TestCase):
    """Test uncertainty calculation for Thermodynamic Computing integration"""

    def setUp(self):
        """Set up test fixtures"""
        self.router = IntelligentRouterEnhanced(
            ai_service=None,
            logger=None,
            config=None
        )

    def test_simple_task_low_uncertainty(self):
        """Simple tasks should have low uncertainty"""
        card = {
            'title': 'Fix typo in README',
            'description': 'Simple documentation fix',
            'story_points': 1
        }

        requirements = TaskRequirements(
            has_frontend=False,
            has_backend=False,
            has_api=False,
            has_database=False,
            has_external_dependencies=False,
            has_ui_components=False,
            has_accessibility_requirements=False,
            requires_notebook=False,
            complexity='simple',
            task_type='documentation',
            estimated_story_points=1,
            requires_architecture_review=False,
            requires_project_review=False,
            parallel_developers_recommended=1,
            confidence_score=0.9
        )

        uncertainty = self.router.calculate_task_uncertainty(card, requirements)

        self.assertLess(uncertainty.overall_uncertainty, 0.3)
        self.assertIn(uncertainty.confidence_level, ['high', 'very_high'])

    def test_complex_task_high_uncertainty(self):
        """Complex tasks with uncertainty keywords should have high uncertainty"""
        card = {
            'title': 'Implement experimental real-time collaboration',
            'description': 'Build real-time collaboration using unfamiliar WebSocket technology',
            'story_points': 21
        }

        requirements = TaskRequirements(
            has_frontend=True,
            has_backend=True,
            has_api=True,
            has_database=True,
            has_external_dependencies=True,
            has_ui_components=True,
            has_accessibility_requirements=False,
            requires_notebook=False,
            complexity='complex',
            task_type='feature',
            estimated_story_points=21,
            requires_architecture_review=True,
            requires_project_review=True,
            parallel_developers_recommended=2,
            confidence_score=0.5
        )

        uncertainty = self.router.calculate_task_uncertainty(card, requirements)

        self.assertGreater(uncertainty.overall_uncertainty, 0.6)
        self.assertIn(uncertainty.confidence_level, ['low', 'very_low'])
        self.assertTrue(len(uncertainty.known_unknowns) > 0)

    def test_database_migration_adds_uncertainty(self):
        """Database migrations should add significant uncertainty"""
        card = {
            'title': 'Migrate from MongoDB to PostgreSQL',
            'description': 'Database migration with schema changes',
            'story_points': 13
        }

        requirements = TaskRequirements(
            has_frontend=False,
            has_backend=True,
            has_api=False,
            has_database=True,
            has_external_dependencies=False,
            has_ui_components=False,
            has_accessibility_requirements=False,
            requires_notebook=False,
            complexity='complex',
            task_type='feature',
            estimated_story_points=13,
            requires_architecture_review=True,
            requires_project_review=True,
            parallel_developers_recommended=1,
            confidence_score=0.6
        )

        uncertainty = self.router.calculate_task_uncertainty(card, requirements)

        self.assertGreater(uncertainty.overall_uncertainty, 0.5)
        self.assertIn('migration', ' '.join(uncertainty.uncertainty_sources).lower())


class TestRiskIdentification(unittest.TestCase):
    """Test risk factor identification for Monte Carlo simulation"""

    def setUp(self):
        """Set up test fixtures"""
        self.router = IntelligentRouterEnhanced()

    def test_security_risk_detection(self):
        """Security keywords should trigger security risk"""
        card = {
            'title': 'Implement OAuth2 authentication',
            'description': 'Add authentication with JWT tokens and session management',
            'story_points': 13
        }

        requirements = TaskRequirements(
            has_frontend=False,
            has_backend=True,
            has_api=True,
            has_database=True,
            has_external_dependencies=True,
            has_ui_components=False,
            has_accessibility_requirements=False,
            requires_notebook=False,
            complexity='complex',
            task_type='feature',
            estimated_story_points=13,
            requires_architecture_review=True,
            requires_project_review=True,
            parallel_developers_recommended=2,
            confidence_score=0.7
        )

        risks = self.router.identify_risk_factors(card, requirements)

        security_risks = [r for r in risks if r.risk_type == 'security']
        self.assertTrue(len(security_risks) > 0)
        self.assertIn(security_risks[0].severity, ['medium', 'high', 'critical'])

    def test_database_migration_risk_detection(self):
        """Database migration should trigger high severity risk"""
        card = {
            'title': 'Migrate database schema',
            'description': 'Major schema migration with data transformation',
            'story_points': 13
        }

        requirements = TaskRequirements(
            has_frontend=False,
            has_backend=True,
            has_api=False,
            has_database=True,
            has_external_dependencies=False,
            has_ui_components=False,
            has_accessibility_requirements=False,
            requires_notebook=False,
            complexity='complex',
            task_type='feature',
            estimated_story_points=13,
            requires_architecture_review=True,
            requires_project_review=True,
            parallel_developers_recommended=1,
            confidence_score=0.6
        )

        risks = self.router.identify_risk_factors(card, requirements)

        db_risks = [r for r in risks if r.risk_type == 'database']
        self.assertTrue(len(db_risks) > 0)
        self.assertIn(db_risks[0].severity, ['high', 'critical'])
        self.assertGreater(db_risks[0].probability, 0.3)

    def test_multiple_risk_factors(self):
        """Complex task with multiple risk patterns should identify multiple risks"""
        card = {
            'title': 'Build secure payment processing with Stripe integration',
            'description': 'Complex payment system with performance requirements',
            'story_points': 21
        }

        requirements = TaskRequirements(
            has_frontend=True,
            has_backend=True,
            has_api=True,
            has_database=True,
            has_external_dependencies=True,
            has_ui_components=True,
            has_accessibility_requirements=False,
            requires_notebook=False,
            complexity='complex',
            task_type='feature',
            estimated_story_points=21,
            requires_architecture_review=True,
            requires_project_review=True,
            parallel_developers_recommended=2,
            confidence_score=0.6
        )

        risks = self.router.identify_risk_factors(card, requirements)

        # Should identify security, integration, complexity risks
        self.assertGreater(len(risks), 2)

        risk_types = {r.risk_type for r in risks}
        self.assertIn('security', risk_types)
        self.assertIn('dependency', risk_types)


class TestPipelineModeRecommendation(unittest.TestCase):
    """Test pipeline mode recommendation logic"""

    def setUp(self):
        """Set up test fixtures"""
        self.router = IntelligentRouterEnhanced()

    def test_simple_task_recommends_standard(self):
        """Simple tasks should recommend STANDARD mode"""
        card = {'title': 'Fix typo', 'description': 'Simple fix', 'story_points': 1}

        requirements = TaskRequirements(
            has_frontend=False, has_backend=False, has_api=False,
            has_database=False, has_external_dependencies=False,
            has_ui_components=False, has_accessibility_requirements=False,
            requires_notebook=False, complexity='simple', task_type='bugfix',
            estimated_story_points=1, requires_architecture_review=False,
            requires_project_review=False, parallel_developers_recommended=1,
            confidence_score=0.9
        )

        uncertainty = UncertaintyAnalysis(
            overall_uncertainty=0.1,
            uncertainty_sources=[],
            known_unknowns=[],
            similar_task_history=20,
            confidence_level='very_high'
        )

        risks = []

        recommendation = self.router.recommend_pipeline_mode(
            card, requirements, uncertainty, risks
        )

        self.assertEqual(recommendation.recommended_mode, PipelineMode.STANDARD)
        self.assertFalse(recommendation.use_dynamic_pipeline)
        self.assertFalse(recommendation.use_two_pass)
        self.assertFalse(recommendation.use_thermodynamic)

    def test_prototype_recommends_two_pass(self):
        """Prototype tasks should recommend TWO_PASS mode"""
        card = {
            'title': 'Prototype new feature',
            'description': 'Build experimental prototype to test approach',
            'story_points': 8
        }

        requirements = TaskRequirements(
            has_frontend=True, has_backend=True, has_api=False,
            has_database=False, has_external_dependencies=False,
            has_ui_components=True, has_accessibility_requirements=False,
            requires_notebook=False, complexity='medium', task_type='feature',
            estimated_story_points=8, requires_architecture_review=True,
            requires_project_review=False, parallel_developers_recommended=2,
            confidence_score=0.6
        )

        uncertainty = UncertaintyAnalysis(
            overall_uncertainty=0.5,
            uncertainty_sources=['experimental'],
            known_unknowns=['approach viability'],
            similar_task_history=2,
            confidence_level='medium'
        )

        risks = []

        recommendation = self.router.recommend_pipeline_mode(
            card, requirements, uncertainty, risks
        )

        self.assertEqual(recommendation.recommended_mode, PipelineMode.TWO_PASS)
        self.assertTrue(recommendation.use_two_pass)

    def test_high_uncertainty_recommends_adaptive(self):
        """High uncertainty should recommend ADAPTIVE mode"""
        card = {
            'title': 'Research new technology',
            'description': 'Investigate unfamiliar technology with unclear requirements',
            'story_points': 13
        }

        requirements = TaskRequirements(
            has_frontend=False, has_backend=True, has_api=True,
            has_database=False, has_external_dependencies=True,
            has_ui_components=False, has_accessibility_requirements=False,
            requires_notebook=False, complexity='complex', task_type='feature',
            estimated_story_points=13, requires_architecture_review=True,
            requires_project_review=True, parallel_developers_recommended=2,
            confidence_score=0.4
        )

        uncertainty = UncertaintyAnalysis(
            overall_uncertainty=0.8,
            uncertainty_sources=['unfamiliar tech', 'unclear requirements'],
            known_unknowns=['technology behavior', 'integration complexity'],
            similar_task_history=0,
            confidence_level='very_low'
        )

        risks = [
            RiskFactor('complexity', 'High technical complexity', 'high', 0.4, 'Research'),
            RiskFactor('dependency', 'External dependencies', 'medium', 0.3, 'Test')
        ]

        recommendation = self.router.recommend_pipeline_mode(
            card, requirements, uncertainty, risks
        )

        self.assertEqual(recommendation.recommended_mode, PipelineMode.ADAPTIVE)
        self.assertTrue(recommendation.use_thermodynamic)

    def test_complex_risky_task_recommends_full(self):
        """Complex tasks with high risk should recommend FULL mode"""
        card = {
            'title': 'Refactor authentication system',
            'description': 'Major refactoring of security-critical authentication',
            'story_points': 21
        }

        requirements = TaskRequirements(
            has_frontend=False, has_backend=True, has_api=True,
            has_database=True, has_external_dependencies=True,
            has_ui_components=False, has_accessibility_requirements=False,
            requires_notebook=False, complexity='complex', task_type='refactor',
            estimated_story_points=21, requires_architecture_review=True,
            requires_project_review=True, parallel_developers_recommended=2,
            confidence_score=0.5
        )

        uncertainty = UncertaintyAnalysis(
            overall_uncertainty=0.7,
            uncertainty_sources=['refactoring complexity', 'security critical'],
            known_unknowns=['edge cases', 'backward compatibility'],
            similar_task_history=1,
            confidence_level='low'
        )

        risks = [
            RiskFactor('security', 'Security critical', 'critical', 0.4, 'Review'),
            RiskFactor('complexity', 'High complexity', 'high', 0.4, 'Breakdown'),
            RiskFactor('database', 'Schema changes', 'high', 0.3, 'Test')
        ]

        recommendation = self.router.recommend_pipeline_mode(
            card, requirements, uncertainty, risks
        )

        self.assertEqual(recommendation.recommended_mode, PipelineMode.FULL)
        self.assertTrue(recommendation.use_dynamic_pipeline)
        self.assertTrue(recommendation.use_two_pass)
        self.assertTrue(recommendation.use_thermodynamic)


class TestEnhancedRoutingDecision(unittest.TestCase):
    """Test complete enhanced routing decision"""

    def setUp(self):
        """Set up test fixtures"""
        mock_logger = Mock()
        mock_logger.log = Mock()

        self.router = IntelligentRouterEnhanced(
            ai_service=None,
            logger=mock_logger,
            config=None
        )

    def test_enhanced_decision_includes_all_components(self):
        """Enhanced decision should include all new components"""
        card = {
            'card_id': 'TEST-123',
            'title': 'Test task',
            'description': 'Test description',
            'story_points': 5
        }

        decision = self.router.make_enhanced_routing_decision(card)

        # Should have base routing decision fields
        self.assertIsNotNone(decision.task_id)
        self.assertIsNotNone(decision.stages_to_run)
        self.assertIsNotNone(decision.requirements)

        # Should have enhanced fields
        self.assertIsNotNone(decision.feature_recommendation)
        self.assertIsNotNone(decision.uncertainty_analysis)
        self.assertIsNotNone(decision.risk_factors)
        self.assertIsNotNone(decision.thermodynamic_context)
        self.assertIsNotNone(decision.dynamic_pipeline_context)
        self.assertIsNotNone(decision.two_pass_context)

    def test_thermodynamic_context_completeness(self):
        """Thermodynamic context should contain all required fields"""
        card = {
            'card_id': 'TEST-456',
            'title': 'Complex task',
            'description': 'Complex description with uncertainty',
            'story_points': 13
        }

        decision = self.router.make_enhanced_routing_decision(card)
        context = decision.thermodynamic_context

        # Check required fields
        required_fields = [
            'task_type', 'complexity', 'story_points',
            'uncertainty_level', 'confidence_level',
            'suggested_strategy', 'suggested_samples',
            'suggested_temperature'
        ]

        for field in required_fields:
            self.assertIn(field, context)

    def test_dynamic_pipeline_context_completeness(self):
        """Dynamic pipeline context should contain configuration"""
        card = {
            'card_id': 'TEST-789',
            'title': 'Medium task',
            'description': 'Task with varying complexity',
            'story_points': 8
        }

        decision = self.router.make_enhanced_routing_decision(card)
        context = decision.dynamic_pipeline_context

        # Check required fields
        required_fields = [
            'complexity', 'estimated_duration',
            'suggested_max_workers', 'suggested_retry_attempts',
            'suggested_timeout'
        ]

        for field in required_fields:
            self.assertIn(field, context)


class TestContextCreation(unittest.TestCase):
    """Test context creation for advanced features"""

    def setUp(self):
        """Set up test fixtures"""
        self.router = IntelligentRouterEnhanced()

    def test_uncertainty_strategy_selection(self):
        """Test appropriate uncertainty strategy selection"""
        # Multiple risks → Monte Carlo
        uncertainty = UncertaintyAnalysis(0.5, [], [], 5, 'medium')
        risks = [
            RiskFactor('security', 'test', 'high', 0.3, ''),
            RiskFactor('database', 'test', 'high', 0.3, ''),
            RiskFactor('complexity', 'test', 'medium', 0.2, '')
        ]

        strategy = self.router._suggest_uncertainty_strategy(uncertainty, risks)
        self.assertEqual(strategy, 'monte_carlo')

        # Prior experience → Bayesian
        uncertainty = UncertaintyAnalysis(0.3, [], [], 10, 'high')
        risks = []

        strategy = self.router._suggest_uncertainty_strategy(uncertainty, risks)
        self.assertEqual(strategy, 'bayesian')

        # High uncertainty → Ensemble
        uncertainty = UncertaintyAnalysis(0.8, [], [], 1, 'very_low')
        risks = []

        strategy = self.router._suggest_uncertainty_strategy(uncertainty, risks)
        self.assertEqual(strategy, 'ensemble')

    def test_monte_carlo_sample_suggestions(self):
        """Test Monte Carlo sample count suggestions"""
        # Many risks → high sample count
        risks = [RiskFactor('test', '', 'high', 0.3, '')] * 4
        samples = self.router._suggest_monte_carlo_samples(risks)
        self.assertEqual(samples, 5000)

        # Some risks → moderate samples
        risks = [RiskFactor('test', '', 'medium', 0.2, '')] * 2
        samples = self.router._suggest_monte_carlo_samples(risks)
        self.assertEqual(samples, 1000)

        # Few risks → low samples
        risks = []
        samples = self.router._suggest_monte_carlo_samples(risks)
        self.assertEqual(samples, 500)

    def test_temperature_suggestions(self):
        """Test temperature sampling suggestions"""
        # High uncertainty → high temperature
        uncertainty = UncertaintyAnalysis(0.9, [], [], 0, 'very_low')
        temp = self.router._suggest_initial_temperature(uncertainty)
        self.assertGreater(temp, 1.5)

        # Low uncertainty → low temperature
        uncertainty = UncertaintyAnalysis(0.1, [], [], 20, 'very_high')
        temp = self.router._suggest_initial_temperature(uncertainty)
        self.assertLess(temp, 1.0)


class TestBackwardCompatibility(unittest.TestCase):
    """Test that enhanced router maintains backward compatibility"""

    def test_can_use_as_base_router(self):
        """Enhanced router should work where base router is expected"""
        router = IntelligentRouterEnhanced()

        card = {
            'title': 'Test task',
            'description': 'Test description',
            'story_points': 5
        }

        # Should be able to call base methods
        requirements = router.analyze_task_requirements(card)
        self.assertIsInstance(requirements, TaskRequirements)

        decision = router.make_routing_decision(card)
        self.assertIsInstance(decision.task_id, str)
        self.assertIsInstance(decision.stages_to_run, list)


if __name__ == '__main__':
    unittest.main()
