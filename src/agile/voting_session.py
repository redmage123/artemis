#!/usr/bin/env python3
"""
Planning Poker Voting Session Manager

WHY: Manages individual voting sessions with agents, handling vote collection
and error recovery during estimation rounds.

RESPONSIBILITY:
- Collect votes from multiple agents in parallel
- Generate agent-specific voting prompts
- Handle voting errors with graceful fallback
- Coordinate concurrent vote collection for performance

PATTERNS:
- Concurrent Execution: ThreadPoolExecutor for parallel LLM calls
- Error Handling: Graceful degradation with default votes
- Builder Pattern: Construct complex prompts systematically
- Guard Clauses: Early returns for invalid states
"""

import json
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from artemis_stage_interface import LoggerInterface
from llm_client import LLMClient, LLMMessage
from pipeline_observer import EventType, PipelineObservable

from .models import EstimationVote, EstimationConfig, FibonacciScale


class VotingSession:
    """
    Manages a single round of Planning Poker voting

    WHY: Coordinates parallel vote collection with error handling
    """

    def __init__(
        self,
        agents: List[str],
        llm_client: LLMClient,
        logger: LoggerInterface,
        observable: Optional[PipelineObservable] = None
    ):
        """
        Initialize voting session

        Args:
            agents: List of agent names participating
            llm_client: LLM client for generating votes
            logger: Logger interface
            observable: Optional PipelineObservable for event broadcasting
        """
        self.agents = agents
        self.llm_client = llm_client
        self.logger = logger
        self.observable = observable

    def collect_votes(
        self,
        feature_title: str,
        feature_description: str,
        acceptance_criteria: List[str],
        round_num: int,
        previous_votes: Optional[List[EstimationVote]] = None
    ) -> List[EstimationVote]:
        """
        Collect estimation votes from all agents in parallel

        WHY: Parallel execution reduces voting time by ~3x

        Args:
            feature_title: Feature name
            feature_description: Detailed description
            acceptance_criteria: List of acceptance criteria
            round_num: Current round number
            previous_votes: Votes from previous round (for context)

        Returns:
            List of EstimationVote objects sorted by agent name
        """
        # Guard clause: validate agents exist
        if not self.agents:
            self.logger.log("No agents available for voting", "ERROR")
            return []

        votes = []

        # Parallelize LLM calls for 3x speedup
        with ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            # Submit all votes concurrently
            future_to_agent = {
                executor.submit(
                    self._agent_vote,
                    agent_name,
                    feature_title,
                    feature_description,
                    acceptance_criteria,
                    round_num,
                    previous_votes
                ): agent_name
                for agent_name in self.agents
            }

            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    vote = future.result()
                    votes.append(vote)
                    self.logger.log(
                        f"  {agent_name}: {vote.story_points} points (confidence: {vote.confidence:.0%})",
                        "INFO"
                    )
                except Exception as e:
                    self.logger.log(f"Error getting vote from {agent_name}: {e}", "ERROR")
                    self._notify_vote_failure(agent_name, str(e))
                    # Add default vote on error
                    votes.append(self._create_default_vote(agent_name))

        # Sort votes by agent name for consistent ordering
        votes.sort(key=lambda v: v.agent_name)
        return votes

    def _agent_vote(
        self,
        agent_name: str,
        feature_title: str,
        feature_description: str,
        acceptance_criteria: List[str],
        round_num: int,
        previous_votes: Optional[List[EstimationVote]] = None
    ) -> EstimationVote:
        """
        Get a single agent's vote using LLM

        WHY: Isolates individual agent voting logic with error handling

        Args:
            agent_name: Name of the voting agent
            feature_title: Feature name
            feature_description: Detailed description
            acceptance_criteria: List of acceptance criteria
            round_num: Current round number
            previous_votes: Votes from previous round

        Returns:
            EstimationVote from the agent
        """
        prompt = self._build_voting_prompt(
            agent_name,
            feature_title,
            feature_description,
            acceptance_criteria,
            round_num,
            previous_votes
        )

        try:
            messages = [
                LLMMessage(
                    role="system",
                    content=f"You are a {agent_name} agent providing technical estimates."
                ),
                LLMMessage(role="user", content=prompt)
            ]

            llm_response = self.llm_client.complete(
                messages=messages,
                response_format={"type": "json_object"}
            )

            data = json.loads(llm_response.content)
            return self._parse_vote_response(agent_name, data)

        except Exception as e:
            self.logger.log(f"Error getting vote from {agent_name}: {e}", "ERROR")
            return self._create_default_vote(agent_name, error=str(e))

    def _build_voting_prompt(
        self,
        agent_name: str,
        feature_title: str,
        feature_description: str,
        acceptance_criteria: List[str],
        round_num: int,
        previous_votes: Optional[List[EstimationVote]]
    ) -> str:
        """
        Build voting prompt for agent

        WHY: Separates prompt construction from LLM invocation

        Args:
            agent_name: Name of the voting agent
            feature_title: Feature name
            feature_description: Detailed description
            acceptance_criteria: List of acceptance criteria
            round_num: Current round number
            previous_votes: Votes from previous round

        Returns:
            Formatted prompt string
        """
        criteria_text = "\n".join(f"- {c}" for c in acceptance_criteria)

        previous_context = ""
        if previous_votes and round_num > 1:
            votes_summary = ", ".join(
                f"{v.agent_name}: {v.story_points}" for v in previous_votes
            )
            previous_context = (
                f"\n\nPrevious round votes: {votes_summary}\n"
                f"Please consider these votes and adjust if needed."
            )

        return f"""You are {agent_name} participating in Planning Poker estimation.

Feature: {feature_title}
Description: {feature_description}

Acceptance Criteria:
{criteria_text}

Vote using Fibonacci sequence: 1, 2, 3, 5, 8, 13, 21, 100 (100 = too complex)

Consider:
- Technical complexity
- Unknown dependencies
- Testing requirements
- Integration points
{previous_context}

Respond in JSON format:
{{
    "story_points": <number from Fibonacci sequence>,
    "reasoning": "<brief explanation>",
    "confidence": <0.0 to 1.0>,
    "concerns": ["<concern 1>", "<concern 2>"]
}}
"""

    def _parse_vote_response(self, agent_name: str, data: Dict[str, Any]) -> EstimationVote:
        """
        Parse LLM response into EstimationVote

        WHY: Centralizes response parsing with validation

        Args:
            agent_name: Name of the voting agent
            data: Parsed JSON response

        Returns:
            EstimationVote object
        """
        return EstimationVote(
            agent_name=agent_name,
            story_points=int(data.get("story_points", EstimationConfig.ERROR_VOTE_POINTS)),
            reasoning=data.get("reasoning", "No reasoning provided"),
            confidence=float(data.get("confidence", EstimationConfig.DEFAULT_CONFIDENCE)),
            concerns=data.get("concerns", [])
        )

    def _create_default_vote(
        self,
        agent_name: str,
        error: Optional[str] = None
    ) -> EstimationVote:
        """
        Create default vote on error

        WHY: Provides fallback voting behavior for error scenarios

        Args:
            agent_name: Name of the agent
            error: Optional error message

        Returns:
            Default EstimationVote
        """
        reasoning = f"Default vote (error: {error})" if error else "Default vote"
        return EstimationVote(
            agent_name=agent_name,
            story_points=EstimationConfig.ERROR_VOTE_POINTS,
            reasoning=reasoning,
            confidence=EstimationConfig.DEFAULT_CONFIDENCE,
            concerns=["Unable to properly estimate"]
        )

    def _notify_vote_failure(self, agent_name: str, error: str) -> None:
        """
        Notify observers of vote failure

        WHY: Enables monitoring and alerting on voting failures

        Args:
            agent_name: Name of the agent that failed
            error: Error message
        """
        if not self.observable:
            return

        from pipeline_observer import PipelineEvent

        event = PipelineEvent(
            event_type=EventType.STAGE_FAILED,
            stage_name="planning_poker",
            data={
                "agent_name": agent_name,
                "error": error,
                "fallback": "using_default_vote"
            }
        )
        self.observable.notify(event)
