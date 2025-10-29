from artemis_logger import get_logger
logger = get_logger('intent_detector')
'\nWHY: Classify user intent from natural language messages\nRESPONSIBILITY: Parse messages and extract intent with parameters\nPATTERNS: Strategy (LLM-based classification), Guard Clauses\n\nIntent detector uses LLM to understand user requests and route to\nappropriate handlers. Extracts parameters like task descriptions and card IDs.\n'
import json
import re
from typing import Dict, Any
from llm_client import LLMMessage, LLMClient
from chat.models import ChatContext

class IntentDetector:
    """
    Detects user intent from conversation.

    WHY: Natural language is ambiguous - need classification to route correctly.
    PATTERNS: Strategy (LLM classification), Fallback on errors.
    """
    CLASSIFICATION_PROMPT = 'Analyze the user\'s message and classify their intent.\n\nReturn a JSON object with:\n{\n  "type": "greeting|create_task|check_status|explain_feature|modify_task|ask_capability|general",\n  "parameters": {...extracted params like task description, card_id, etc...},\n  "confidence": 0.0-1.0\n}\n\nIntent types:\n- greeting: Hi, hello, how are you\n- create_task: Build X, implement Y, create a feature for Z\n- check_status: What\'s the status of X, how\'s Y going, is Z done\n- explain_feature: How does X work, what can you do, explain Y\n- modify_task: Change X, update Y, cancel Z\n- ask_capability: Can you do X, are you able to Y\n- general: Everything else\n\nBe direct. Extract concrete details.'

    def __init__(self, llm_client: LLMClient, verbose: bool=False):
        """
        Initialize intent detector.

        Args:
            llm_client: LLM client for classification
            verbose: Enable verbose logging
        """
        self.llm_client = llm_client
        self.verbose = verbose

    def detect_intent(self, message: str, context: ChatContext) -> Dict[str, Any]:
        """
        Figure out what the user wants.

        WHY: Routing requires understanding user intent from natural language.

        Args:
            message: User's message
            context: Conversation context

        Returns:
            Intent classification with extracted parameters:
            {
                "type": str,
                "parameters": dict,
                "confidence": float
            }

        Example:
            >>> intent = detector.detect_intent(
            ...     "Build a login page",
            ...     context
            ... )
            >>> intent["type"]
            'create_task'
            >>> intent["parameters"]["task_description"]
            'Build a login page'
        """
        recent_history = context.conversation_history[-6:]
        history_text = self._format_history(recent_history)
        user_prompt = f"Recent conversation:\n{(history_text if history_text else '(New conversation)')}\n\nLatest message: {message}\n\nClassify the intent:"
        messages = [LLMMessage(role='system', content=self.CLASSIFICATION_PROMPT), LLMMessage(role='user', content=user_prompt)]
        response = self.llm_client.complete(messages, temperature=0.3, max_tokens=500)
        return self._parse_intent_response(response.content)

    def _format_history(self, messages) -> str:
        """
        Format message history for prompt.

        WHY: Provides conversation context for better classification.

        Args:
            messages: List of ChatMessage objects

        Returns:
            Formatted history string
        """
        return '\n'.join([f"{('User' if msg.role == 'user' else 'Artemis')}: {msg.content}" for msg in messages])

    def _parse_intent_response(self, response: str) -> Dict[str, Any]:
        """
        Parse intent from LLM response.

        WHY: LLM may return JSON in different formats - need robust parsing.

        Args:
            response: LLM response content

        Returns:
            Parsed intent dict (fallback to "general" on error)
        """
        try:
            json_match = re.search('\\{.*\\}', response, re.DOTALL)
            if not json_match:
                return self._fallback_intent()
            return json.loads(json_match.group(0))
        except Exception as e:
            if self.verbose:
                
                logger.log(f'[IntentDetector] Parsing failed: {e}', 'INFO')
            return self._fallback_intent()

    def _fallback_intent(self) -> Dict[str, Any]:
        """
        Fallback intent when classification fails.

        WHY: Graceful degradation - route to general handler on errors.

        Returns:
            Generic intent dict
        """
        return {'type': 'general', 'parameters': {}, 'confidence': 0.5}