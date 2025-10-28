#!/usr/bin/env python3
"""
Planning Poker Consensus Builder

WHY: Analyzes voting patterns to determine consensus and generate
discussion summaries when consensus is not reached.

RESPONSIBILITY:
- Check for voting consensus using Fibonacci proximity
- Generate discussion summaries from divergent votes
- Force consensus using weighted averaging
- Identify outlier votes and key concerns

PATTERNS:
- Strategy Pattern: Different consensus strategies
- Guard Clauses: Early returns for edge cases
- Functional Programming: Comprehensions and generators
- Dispatcher: Consensus rules as lambda predicates
"""

from typing import List, Optional, Tuple, Callable
from statistics import median, mean

from .models import EstimationVote, FibonacciScale, EstimationConfig


class ConsensusBuilder:
    """
    Builds consensus from Planning Poker votes

    WHY: Encapsulates consensus logic and discussion generation
    """

    def __init__(self):
        """Initialize consensus builder"""
        # Fibonacci index for proximity checking
        self.fibonacci_index = {v.value: i for i, v in enumerate(FibonacciScale)}
        self.fibonacci_values = [1, 2, 3, 5, 8, 13, 21]  # Excluding UNKNOWN

    def check_consensus(self, votes: List[EstimationVote]) -> Tuple[bool, Optional[int]]:
        """
        Check if consensus reached among votes

        WHY: Determines if voting round succeeded or needs discussion

        Consensus rules:
        - All votes within 1 Fibonacci step = consensus
        - Median vote is the consensus value

        Args:
            votes: List of estimation votes

        Returns:
            Tuple of (consensus_reached, consensus_value)
        """
        # Guard clause: no votes
        if not votes:
            return False, None

        # Get all vote values
        values = [v.story_points for v in votes]

        # Find median
        median_value = int(median(values))

        # Get median Fibonacci index
        median_idx = self.fibonacci_index.get(median_value, 0)

        # Check if all values are within 1 Fibonacci step of median
        consensus = all(
            abs(self.fibonacci_index.get(value, 0) - median_idx) <= 1
            for value in values
        )

        return consensus, median_value if consensus else None

    def generate_discussion(self, votes: List[EstimationVote]) -> str:
        """
        Generate discussion summary for outlier votes

        WHY: Highlights divergent reasoning to guide next round

        Args:
            votes: List of estimation votes

        Returns:
            Discussion summary string
        """
        # Guard clause: insufficient votes for discussion
        if len(votes) < 2:
            return "Insufficient votes for discussion"

        # Find highest and lowest votes
        sorted_votes = sorted(votes, key=lambda v: v.story_points)
        lowest = sorted_votes[0]
        highest = sorted_votes[-1]

        # Collect all unique concerns
        all_concerns = ', '.join(set(
            concern
            for vote in votes
            for concern in vote.concerns
        ))

        # Guard clause: no spread between votes
        if lowest.story_points == highest.story_points:
            return f"All votes at {lowest.story_points} points. Key concerns: {all_concerns}"

        discussion = f"""Why the spread?
- {lowest.agent_name} (lowest): {lowest.reasoning}
- {highest.agent_name} (highest): {highest.reasoning}

Key concerns: {all_concerns}"""

        return discussion.strip()

    def force_consensus(self, votes: List[EstimationVote]) -> int:
        """
        Force consensus using weighted average

        WHY: Ensures estimation completes after max rounds

        Uses confidence-weighted averaging, then rounds to nearest
        Fibonacci value.

        Args:
            votes: List of estimation votes

        Returns:
            Forced consensus story points
        """
        # Guard clause: no votes
        if not votes:
            return EstimationConfig.ERROR_VOTE_POINTS

        # Calculate total confidence weight
        total_weight = sum(v.confidence for v in votes)

        # Guard clause: zero confidence (use median)
        if total_weight == 0:
            return int(median(v.story_points for v in votes))

        # Weighted average by confidence
        weighted_sum = sum(v.story_points * v.confidence for v in votes)
        weighted_avg = weighted_sum / total_weight

        # Round to nearest Fibonacci number
        nearest = min(
            self.fibonacci_values,
            key=lambda x: abs(x - weighted_avg)
        )

        return nearest

    def calculate_vote_spread(self, votes: List[EstimationVote]) -> int:
        """
        Calculate spread between highest and lowest votes

        WHY: Measures voting divergence for confidence calculation

        Args:
            votes: List of estimation votes

        Returns:
            Spread in story points
        """
        # Guard clause: insufficient votes
        if not votes:
            return 0

        values = [v.story_points for v in votes]
        return max(values) - min(values)

    def identify_outliers(
        self,
        votes: List[EstimationVote],
        median_value: int
    ) -> List[EstimationVote]:
        """
        Identify votes that are outliers from median

        WHY: Helps focus discussion on divergent perspectives

        Args:
            votes: List of estimation votes
            median_value: Median story points value

        Returns:
            List of outlier votes (>1 Fibonacci step from median)
        """
        # Guard clause: no votes
        if not votes:
            return []

        median_idx = self.fibonacci_index.get(median_value, 0)

        return [
            vote for vote in votes
            if abs(self.fibonacci_index.get(vote.story_points, 0) - median_idx) > 1
        ]

    def get_average_confidence(self, votes: List[EstimationVote]) -> float:
        """
        Calculate average confidence across all votes

        WHY: Provides confidence metric for estimation quality

        Args:
            votes: List of estimation votes

        Returns:
            Average confidence (0.0 to 1.0)
        """
        # Guard clause: no votes
        if not votes:
            return 0.0

        return mean(v.confidence for v in votes)
