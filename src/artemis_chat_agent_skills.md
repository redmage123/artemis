# Artemis Chat Agent - Skills

## Agent Overview
**File**: `artemis_chat_agent.py`
**Purpose**: Interactive chat interface for Artemis pipeline
**Single Responsibility**: Enable natural language interaction with pipeline

## Core Skills

### 1. Natural Language Understanding
- **Intent Recognition**: Understand user requests
- **Context Awareness**: Maintains conversation history
- **Command Interpretation**: Converts chat to pipeline commands
- **Query Understanding**: Interprets questions about pipeline state

### 2. Pipeline Control
- **Start Tasks**: Initiate pipeline tasks via chat
- **Check Status**: Query task and pipeline status
- **Cancel Operations**: Stop running tasks
- **View Results**: Display task outcomes

### 3. Information Retrieval
- **Pipeline Status**: Current state of all stages
- **Task Details**: Information about specific tasks
- **Agent Status**: Health of individual agents
- **Historical Data**: Query past pipeline runs

### 4. LLM-Powered Interaction
- **Conversational**: Natural dialogue flow
- **Multi-Turn**: Maintains conversation context
- **Clarification**: Asks for clarification when needed
- **Helpful Responses**: Provides actionable information

## Usage Patterns

```python
# Initialize chat agent
chat = ArtemisChatAgent(
    llm_provider="openai",
    logger=logger,
    orchestrator=orchestrator
)

# User interaction
user_input = "What's the status of card-20251027-001?"
response = chat.process_message(user_input)
print(response)

# Pipeline control
user_input = "Start development on user authentication feature"
response = chat.process_message(user_input)
print(response)

# Query capabilities
user_input = "Show me all failed tasks from today"
response = chat.process_message(user_input)
print(response)
```

## Supported Commands

- **Status Queries**: "What's the status?", "How's card-123?"
- **Task Control**: "Start task", "Cancel task", "Retry failed task"
- **Information Requests**: "Show recent errors", "List all agents"
- **Help**: "What can you do?", "Help with...", "How do I..."

## Design Patterns

- **Command Pattern**: Chat messages map to pipeline commands
- **Interpreter Pattern**: Parses natural language to actions
- **Observer Pattern**: Watches pipeline for status updates

## Integration Points

- **Orchestrator**: Executes pipeline commands
- **Supervisor**: Queries agent health
- **RAG Agent**: Retrieves historical context
- **State Machine**: Checks pipeline state

## Response Types

- **Status Updates**: Current task/pipeline state
- **Action Confirmation**: "Started task X"
- **Information**: Detailed query responses
- **Errors**: Clear error messages with solutions
- **Help**: Usage instructions

## LLM Provider Support

- **OpenAI**: GPT models for chat
- **Anthropic**: Claude models for chat
- **Fallback**: Keyword-based responses without LLM

## Context Management

- **Session History**: Remembers conversation
- **Card Context**: Tracks which card is being discussed
- **Agent Context**: Remembers which agent was mentioned
- **Clear Context**: "Start over", "New conversation"
