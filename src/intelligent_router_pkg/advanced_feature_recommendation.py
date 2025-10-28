#!/usr/bin/env python3
"""
Advanced Feature Recommendation Model

WHAT: Data structure representing intensity recommendations for all advanced features.

WHY: All three features (Thermodynamic, Two-Pass, Dynamic) work together simultaneously.
This recommends HOW AGGRESSIVELY to use each feature, not WHETHER to enable them.

RESPONSIBILITY:
    - Store recommended pipeline mode
    - Store intensity levels for each feature (0.0-1.0)
    - Provide backward-compatible boolean flags
    - Store rationale and expected benefits

PATTERNS:
    - Value Object: Immutable data structure
    - Strategy Pattern: Different intensity levels = different strategies
    - Adapter Pattern: Maps intensity to boolean flags for compatibility
"""

from dataclasses import dataclass
from typing import List
from advanced_pipeline_integration import PipelineMode


@dataclass
class AdvancedFeatureRecommendation:
    """
    Recommendation for intensity of ALL advanced features working in tandem.

    WHY: All three features work together simultaneously - this recommends
    HOW AGGRESSIVELY to use each feature, not WHETHER to enable them.

    Design Philosophy: Features are complementary layers, not alternatives
        - Thermodynamic: Always active, provides confidence scores throughout
        - Two-Pass: Optional layer, provides fast feedback + refinement
        - Dynamic: Always active within passes, optimization intensity varies

    Intensity Levels:
        0.0 = Minimal (feature present but not aggressive)
        0.5 = Moderate (balanced approach)
        1.0 = Maximum (full feature capability)

    Attributes:
        recommended_mode: Suggested pipeline execution mode
        thermodynamic_intensity: How much uncertainty quantification (0.0-1.0)
        two_pass_intensity: Single vs full two-pass (0.0-1.0)
        dynamic_intensity: Sequential vs max parallelism (0.0-1.0)
        use_dynamic_pipeline: Legacy boolean flag (True if dynamic_intensity > 0.3)
        use_two_pass: Legacy boolean flag (True if two_pass_intensity > 0.5)
        use_thermodynamic: Legacy boolean flag (True if thermodynamic_intensity > 0.3)
        rationale: Why these intensities were chosen
        confidence_in_recommendation: Confidence in this recommendation (0.0-1.0)
        expected_benefits: List of expected benefits from these intensities
    """
    recommended_mode: PipelineMode

    # Intensity levels for each feature (0.0-1.0)
    thermodynamic_intensity: float  # How much uncertainty quantification
    two_pass_intensity: float       # 0.0=single pass, 1.0=full two-pass
    dynamic_intensity: float        # 0.0=sequential, 1.0=max parallelism

    # Legacy boolean flags (computed from intensity for backward compatibility)
    use_dynamic_pipeline: bool      # True if dynamic_intensity > 0.3
    use_two_pass: bool              # True if two_pass_intensity > 0.5
    use_thermodynamic: bool         # True if thermodynamic_intensity > 0.3

    rationale: str
    confidence_in_recommendation: float  # 0.0-1.0
    expected_benefits: List[str]  # Why these intensities will help
