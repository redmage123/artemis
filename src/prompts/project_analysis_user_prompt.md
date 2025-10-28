# Project Analysis: Task Analysis Request

Analyze the following task BEFORE implementation across these dimensions:

1. **Scope & Requirements**: Are requirements clear and complete?
2. **Security**: Any security vulnerabilities or compliance issues?
3. **Performance & Scalability**: Performance concerns or bottlenecks?
4. **Testing Strategy**: Is testing approach comprehensive?
5. **Error Handling**: Are edge cases and failures addressed?
6. **Architecture**: Architectural concerns or design issues?
7. **Dependencies**: External dependencies or integration risks?
8. **Accessibility**: WCAG compliance and UX considerations?

**Task Title:** {title}
**Description:** {description}
**Priority:** {priority}
**Story Points:** {points}
**Acceptance Criteria:**
{acceptance_criteria}

{context_summary}

{environment_context}

**Task Breakdown:**
1. Read the task requirements carefully
2. Analyze each dimension systematically
3. Identify issues categorized by severity (CRITICAL/HIGH/MEDIUM)
4. Provide specific, actionable recommendations
5. Self-validate your analysis before responding

**Response Format (JSON only):**
```json
{
  "issues": [
    {
      "category": "Security|Performance|Testing|Architecture|Dependencies|Accessibility|Scope|Error Handling",
      "severity": "CRITICAL|HIGH|MEDIUM",
      "description": "Brief issue description",
      "impact": "What happens if not addressed",
      "suggestion": "Specific actionable fix",
      "reasoning": "Why this matters",
      "user_approval_needed": true|false
    }
  ],
  "recommendations": [
    "Specific recommendation 1",
    "Specific recommendation 2"
  ],
  "overall_assessment": "Brief 1-2 sentence summary",
  "recommendation_action": "APPROVE_ALL|APPROVE_CRITICAL|REJECT"
}
```

Return ONLY valid JSON, no markdown, no explanations.
