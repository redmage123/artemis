#!/usr/bin/env python3
"""
Tree of Thoughts (ToT) Reasoning Strategy

WHY: Explores multiple reasoning paths in parallel using tree search,
     enabling systematic exploration of solution space for complex problems.

RESPONSIBILITY:
    - Generate prompts for branching thought exploration
    - Parse multiple thought branches from LLM responses
    - Manage thought tree structure and scoring
    - Select optimal reasoning path through tree

PATTERNS:
    - Strategy Pattern: Concrete reasoning strategy implementation
    - Composite Pattern: Tree structure with nodes
    - Depth-First Search: Path finding algorithm
    - Guard Clauses: Early returns and validation
"""

from typing import Dict, List, Optional, Any, Tuple
import json
import logging

from .models import ReasoningStrategyBase, ThoughtNode


class TreeOfThoughtsStrategy(ReasoningStrategyBase):
    """
    Tree of Thoughts (ToT) prompting strategy.

    Explores multiple reasoning paths in parallel and selects the best.

    WHY: Parallel exploration finds better solutions than linear reasoning
    RESPONSIBILITY: Manage thought tree generation and path selection

    Example:
        tot = TreeOfThoughtsStrategy(branching_factor=3, max_depth=4)
        prompt = tot.generate_prompt("Design a database schema...")
        result = tot.parse_response(llm_response)
        best_path = tot.select_best_path()
    """

    def __init__(
        self,
        branching_factor: int = 3,
        max_depth: int = 4,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize ToT strategy.

        Args:
            branching_factor: Number of branches to explore at each node
            max_depth: Maximum tree depth
            logger: Optional logger instance
        """
        super().__init__(logger)
        self.branching_factor = branching_factor
        self.max_depth = max_depth
        self.root: Optional[ThoughtNode] = None

    def generate_prompt(
        self,
        task: str,
        context: Optional[str] = None,
        depth: int = 0
    ) -> str:
        """
        Generate ToT prompt for exploring thought branches.

        WHY: Different prompts for different tree depths guide exploration
        PATTERNS: Guard clauses for depth-based prompt variation

        Args:
            task: The task to solve
            context: Additional context information
            depth: Current depth in thought tree

        Returns:
            Formatted prompt for generating thought branches
        """
        prompt = "Let's explore multiple approaches to solve this problem.\n\n"

        # Guard clause: Add context if provided
        if context:
            prompt += f"Context:\n{context}\n\n"

        prompt += f"Task: {task}\n\n"

        # Dispatch based on depth (guard clause pattern)
        if depth == 0:
            prompt += self._get_root_level_instructions()
        else:
            prompt += self._get_child_level_instructions()

        prompt += self._get_json_format_template()

        return prompt

    def _get_root_level_instructions(self) -> str:
        """
        Get instructions for root-level thought generation.

        WHY: Root level explores high-level approaches
        RESPONSIBILITY: Provide root-level exploration instructions

        Returns:
            Root level instruction text
        """
        return (
            f"Generate {self.branching_factor} different high-level approaches to solve this problem.\n"
            "For each approach:\n"
            "1. Describe the core idea\n"
            "2. List key advantages\n"
            "3. Identify potential challenges\n"
            "4. Rate the approach from 0-10\n\n"
        )

    def _get_child_level_instructions(self) -> str:
        """
        Get instructions for child-level thought generation.

        WHY: Child levels explore specific next steps
        RESPONSIBILITY: Provide child-level exploration instructions

        Returns:
            Child level instruction text
        """
        return (
            f"For the current approach, generate {self.branching_factor} different next steps.\n"
            "For each step:\n"
            "1. Describe the specific action\n"
            "2. Explain the reasoning\n"
            "3. Predict the outcome\n"
            "4. Rate the step from 0-10\n\n"
        )

    def _get_json_format_template(self) -> str:
        """
        Get JSON format template for response.

        WHY: Structured output enables reliable parsing
        RESPONSIBILITY: Provide response format template

        Returns:
            JSON format template string
        """
        return (
            f"Provide {self.branching_factor} alternatives in JSON format:\n"
            "[\n"
            '  {"thought": "...", "advantages": [...], "challenges": [...], "score": X},\n'
            "  ...\n"
            "]"
        )

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse ToT response into thought tree.

        WHY: Structured parsing enables tree construction and analysis
        PATTERNS: Guard clauses for error handling

        Args:
            response: LLM response with multiple thought branches

        Returns:
            Structured thought tree information
        """
        # Guard clause: Handle empty response
        if not response or not response.strip():
            return {
                "strategy": "tree_of_thoughts",
                "error": "empty_response",
                "branches": 0
            }

        thoughts_data = self._extract_json(response)

        # Guard clause: Handle JSON extraction failure
        if not thoughts_data:
            return {
                "strategy": "tree_of_thoughts",
                "error": "parse_error",
                "raw_response": response[:200]  # Truncate for safety
            }

        self._build_tree(thoughts_data)

        return {
            "strategy": "tree_of_thoughts",
            "branches": len(thoughts_data),
            "thoughts": thoughts_data,
            "best_score": self._get_best_score(thoughts_data)
        }

    def _extract_json(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract JSON array from response text.

        WHY: Separate extraction logic for testability
        RESPONSIBILITY: Parse JSON from potentially noisy text
        PATTERNS: Guard clauses for error handling

        Args:
            response: Response text containing JSON

        Returns:
            Parsed JSON data or empty list on failure
        """
        try:
            # Find JSON array boundaries
            start = response.find('[')
            end = response.rfind(']') + 1

            # Guard clause: No JSON found
            if start == -1 or end <= start:
                self.logger.warning("No JSON array found in response")
                return []

            json_str = response[start:end]
            return json.loads(json_str)

        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse ToT response as JSON: {e}")
            return []

    def _build_tree(self, thoughts_data: List[Dict[str, Any]]) -> None:
        """
        Build thought tree from parsed data.

        WHY: Construct tree structure for path analysis
        RESPONSIBILITY: Create root and child nodes

        Args:
            thoughts_data: List of thought dictionaries
        """
        # Initialize root if needed
        if not self.root:
            self.root = ThoughtNode(
                thought="Root",
                depth=0,
                score=0.0
            )

        # Add thoughts as child nodes
        for data in thoughts_data:
            node = ThoughtNode(
                thought=data.get("thought", ""),
                depth=1,
                score=data.get("score", 0.0)
            )
            self.root.add_child(node)

    def _get_best_score(self, thoughts_data: List[Dict[str, Any]]) -> float:
        """
        Get the best score from thoughts.

        WHY: Track quality of generated thoughts
        RESPONSIBILITY: Find maximum score

        Args:
            thoughts_data: List of thought dictionaries

        Returns:
            Best score found, or 0.0 if no scores
        """
        return max(
            (t.get("score", 0.0) for t in thoughts_data),
            default=0.0
        )

    def select_best_path(self) -> List[ThoughtNode]:
        """
        Select the best path through the thought tree.

        WHY: Find optimal solution path from explored alternatives
        RESPONSIBILITY: DFS to find highest-scoring path
        PATTERNS: Recursive depth-first search

        Returns:
            List of nodes representing the best path
        """
        # Guard clause: No tree to search
        if not self.root:
            return []

        _, best_path = self._dfs_best_path(self.root, 0.0)
        return best_path

    def _dfs_best_path(
        self,
        node: ThoughtNode,
        current_score: float
    ) -> Tuple[float, List[ThoughtNode]]:
        """
        Depth-first search to find best path.

        WHY: Recursive search explores all paths efficiently
        RESPONSIBILITY: Find path with highest cumulative score

        Args:
            node: Current node being explored
            current_score: Cumulative score to this node

        Returns:
            Tuple of (best_score, best_path)
        """
        node.path_score = current_score + node.score

        # Base case: Leaf node
        if not node.children:
            return node.path_score, [node]

        # Recursive case: Explore children
        best_score = node.path_score
        best_path = [node]

        for child in node.children:
            child_score, child_path = self._dfs_best_path(child, node.path_score)
            # Guard clause: Update if better path found
            if child_score > best_score:
                best_score = child_score
                best_path = [node] + child_path

        return best_score, best_path
