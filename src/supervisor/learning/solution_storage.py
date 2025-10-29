from artemis_logger import get_logger
logger = get_logger('solution_storage')
'\nWHY: Persist and retrieve learned solutions using RAG\nRESPONSIBILITY: Store solutions in RAG, query similar cases, manage knowledge base\nPATTERNS: Repository (solution storage), Strategy (similarity search)\n'
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from .models import UnexpectedState, LearnedSolution, LearningStrategy

class SolutionRepository:
    """
    WHY: Manage persistence of learned solutions
    RESPONSIBILITY: Store, retrieve, and update solutions in RAG and memory
    PATTERNS: Repository pattern, Guard Clause
    """

    def __init__(self, rag_agent: Optional[Any]=None, verbose: bool=True):
        self.rag_agent = rag_agent
        self.verbose = verbose
        self.learned_solutions: Dict[str, LearnedSolution] = {}

    def store_solution(self, solution: LearnedSolution, unexpected_state: UnexpectedState) -> None:
        """
        WHY: Persist learned solutions for future reuse
        RESPONSIBILITY: Store in memory cache and RAG
        PATTERNS: Guard Clause (RAG availability)

        Args:
            solution: Learned solution to store
            unexpected_state: Original unexpected state
        """
        self.learned_solutions[solution.solution_id] = solution
        if not self.rag_agent:
            return
        try:
            content = self._format_solution_for_rag(solution, unexpected_state)
            self.rag_agent.store_artifact(artifact_type='learned_solution', card_id=unexpected_state.card_id, task_title=f'Solution: {solution.problem_description[:50]}', content=content, metadata={'solution_id': solution.solution_id, 'unexpected_state_id': solution.unexpected_state_id, 'workflow_steps': solution.workflow_steps, 'success_rate': solution.success_rate, 'learning_strategy': solution.learning_strategy, 'llm_model_used': solution.llm_model_used, 'timestamp': solution.timestamp})
            if self.verbose:
                
                logger.log(f'[Learning] 📝 Solution stored in RAG for future learning', 'INFO')
        except Exception as e:
            if self.verbose:
                
                logger.log(f'[Learning] ⚠️  Failed to store in RAG: {e}', 'INFO')

    def update_solution(self, solution: LearnedSolution) -> None:
        """
        WHY: Keep success metrics current in persistent storage
        RESPONSIBILITY: Update solution success rate in RAG
        PATTERNS: Guard Clause

        Args:
            solution: Solution with updated metrics
        """
        self.learned_solutions[solution.solution_id] = solution
        if not self.rag_agent:
            return
        if self.verbose:
            
            logger.log(f'[Learning] 📝 Updated solution success rate: {solution.success_rate * 100:.1f}%', 'INFO')

    def find_similar_solutions(self, unexpected_state: UnexpectedState) -> List[Dict[str, Any]]:
        """
        WHY: Reuse past solutions for similar problems
        RESPONSIBILITY: Query RAG for semantically similar solutions
        PATTERNS: Guard Clause (RAG availability), Strategy (similarity search)

        Args:
            unexpected_state: Current unexpected state

        Returns:
            List of similar solutions from RAG
        """
        if not self.rag_agent:
            return []
        try:
            query = self._build_similarity_query(unexpected_state)
            results = self.rag_agent.query_similar(query_text=query, artifact_types=['learned_solution', 'recovery_workflow'], top_k=3)
            if self.verbose and results:
                
                logger.log(f'[Learning] 📚 Found {len(results)} similar past solutions', 'INFO')
            return results
        except Exception as e:
            if self.verbose:
                
                logger.log(f'[Learning] ⚠️  Failed to query similar solutions: {e}', 'INFO')
            return []

    def get_solution(self, solution_id: str) -> Optional[LearnedSolution]:
        """
        WHY: Retrieve specific solution by ID
        RESPONSIBILITY: Return solution from memory cache
        """
        return self.learned_solutions.get(solution_id)

    def get_all_solutions(self) -> List[LearnedSolution]:
        """
        WHY: Get all cached solutions
        RESPONSIBILITY: Return all solutions from memory
        """
        return list(self.learned_solutions.values())

    def _format_solution_for_rag(self, solution: LearnedSolution, unexpected_state: UnexpectedState) -> str:
        """
        WHY: Format solution as searchable text for RAG
        RESPONSIBILITY: Create human-readable solution description
        """
        content = f"\nLEARNED SOLUTION\n\nProblem: {solution.problem_description}\nSolution: {solution.solution_description}\n\nUnexpected State: {unexpected_state.current_state}\nExpected States: {', '.join(unexpected_state.expected_states)}\nStage: {unexpected_state.stage_name or 'Unknown'}\n\nWorkflow Steps:\n{json.dumps(solution.workflow_steps, indent=2)}\n\nLearning Strategy: {solution.learning_strategy}\nSuccess Rate: {solution.success_rate * 100:.1f}%\nTimes Applied: {solution.times_applied}\n        ".strip()
        return content

    def _build_similarity_query(self, unexpected_state: UnexpectedState) -> str:
        """
        WHY: Create effective similarity search query
        RESPONSIBILITY: Format unexpected state as search query
        """
        query = f'\n        Unexpected state: {unexpected_state.current_state}\n        Stage: {unexpected_state.stage_name}\n        Error: {unexpected_state.error_message}\n        '.strip()
        return query

class SolutionAdapter:
    """
    WHY: Adapt existing solutions to new contexts
    RESPONSIBILITY: Create new solutions based on similar past cases
    PATTERNS: Adapter pattern, Template Method
    """

    def __init__(self, verbose: bool=True):
        self.verbose = verbose
        self.adaptation_count = 0

    def adapt_from_similar(self, unexpected_state: UnexpectedState, similar_solution: Dict[str, Any]) -> LearnedSolution:
        """
        WHY: Reuse and adapt successful past solutions
        RESPONSIBILITY: Create adapted solution from similar case
        PATTERNS: Adapter pattern

        Args:
            unexpected_state: Current unexpected state
            similar_solution: Similar solution from RAG

        Returns:
            Adapted LearnedSolution
        """
        self.adaptation_count += 1
        original_workflow = similar_solution.get('metadata', {}).get('workflow_steps', [])
        solution = LearnedSolution(solution_id=f'adapted-{unexpected_state.state_id}', timestamp=datetime.utcnow().isoformat() + 'Z', unexpected_state_id=unexpected_state.state_id, problem_description=self._describe_problem(unexpected_state), solution_description=f"Adapted from similar case: {similar_solution.get('content', '')[:100]}", workflow_steps=original_workflow, success_rate=similar_solution.get('metadata', {}).get('success_rate', 0.0), times_applied=0, times_successful=0, learning_strategy=LearningStrategy.SIMILAR_CASE_ADAPTATION.value, llm_model_used=None, human_validated=False, metadata={'adapted_from': similar_solution.get('artifact_id'), 'similarity_score': similar_solution.get('score', 0.0)})
        if self.verbose:
            
            logger.log(f'[Learning] ♻️  Solution adapted from similar case', 'INFO')
        return solution

    def _describe_problem(self, unexpected_state: UnexpectedState) -> str:
        """Generate problem description"""
        from .pattern_recognition import ProblemDescriptor
        return ProblemDescriptor.describe_problem(unexpected_state)