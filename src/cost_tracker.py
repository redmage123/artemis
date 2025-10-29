from artemis_logger import get_logger
logger = get_logger('cost_tracker')
'\nCost Tracker - LLM API Cost Management & Budget Controls\n\nTracks and limits LLM API costs to prevent runaway spending:\n- Token usage tracking (input + output)\n- Cost calculation per model\n- Daily/monthly budget limits\n- Cost alerts and blocking\n- Per-stage cost breakdown\n- Historical cost analysis\n\nSupports:\n- OpenAI (GPT-4, GPT-4o, GPT-3.5-turbo, etc.)\n- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus, etc.)\n- Custom pricing models\n'
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class BudgetExceededError(Exception):
    """Raised when budget limit is exceeded"""
    pass

@dataclass
class LLMCall:
    """Record of a single LLM API call"""
    timestamp: str
    model: str
    provider: str
    tokens_input: int
    tokens_output: int
    cost: float
    stage: str
    card_id: str
    purpose: str

class ModelPricing:
    """
    Pricing for various LLM models (as of 2025)

    Prices are per 1M tokens (input/output)
    """
    PRICING = {'gpt-4o': {'input': 2.5, 'output': 10.0}, 'gpt-4o-mini': {'input': 0.15, 'output': 0.6}, 'gpt-4-turbo': {'input': 10.0, 'output': 30.0}, 'gpt-4': {'input': 30.0, 'output': 60.0}, 'gpt-3.5-turbo': {'input': 0.5, 'output': 1.5}, 'claude-3-5-sonnet-20241022': {'input': 3.0, 'output': 15.0}, 'claude-3-5-sonnet': {'input': 3.0, 'output': 15.0}, 'claude-3-opus': {'input': 15.0, 'output': 75.0}, 'claude-3-sonnet': {'input': 3.0, 'output': 15.0}, 'claude-3-haiku': {'input': 0.25, 'output': 1.25}, 'default': {'input': 10.0, 'output': 30.0}}

    @classmethod
    def get_cost(cls, model: str, tokens_input: int, tokens_output: int) -> float:
        """
        Calculate cost for LLM call

        Args:
            model: Model name
            tokens_input: Input tokens
            tokens_output: Output tokens

        Returns:
            Cost in USD
        """
        model_lower = model.lower()
        pricing = None
        for model_key, model_pricing in cls.PRICING.items():
            if model_key in model_lower:
                pricing = model_pricing
                break
        if pricing is None:
            pricing = cls.PRICING['default']
        input_cost = tokens_input / 1000000 * pricing['input']
        output_cost = tokens_output / 1000000 * pricing['output']
        return input_cost + output_cost

class CostTracker:
    """
    Track and manage LLM API costs

    Features:
    - Track all LLM calls with token counts
    - Calculate costs per model
    - Enforce daily/monthly budgets
    - Alert on threshold exceeded
    - Per-stage cost breakdown
    """

    def __init__(self, storage_path: str='../../.artemis_data/cost_tracking/artemis_costs.json', daily_budget: Optional[float]=None, monthly_budget: Optional[float]=None, alert_threshold: float=0.8):
        """
        Initialize cost tracker

        Args:
            storage_path: Path to store cost records (relative to .agents/agile)
            daily_budget: Daily budget limit in USD (None = unlimited)
            monthly_budget: Optional[float] = None,
            alert_threshold: Alert when budget usage exceeds this fraction
        """
        if not os.path.isabs(storage_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            storage_path = os.path.join(script_dir, storage_path)
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.daily_budget = daily_budget
        self.monthly_budget = monthly_budget
        self.alert_threshold = alert_threshold
        self.calls: List[LLMCall] = self._load_calls()

    def _load_calls(self) -> List[LLMCall]:
        """Load call records from storage"""
        if not self.storage_path.exists():
            return []
        try:
            with open(self.storage_path) as f:
                data = json.load(f)
                return [LLMCall(**call) for call in data]
        except Exception:
            return []

    def _save_calls(self):
        """Save call records to storage"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump([asdict(call) for call in self.calls], f, indent=2)

    def track_call(self, model: str, provider: str, tokens_input: int, tokens_output: int, stage: str, card_id: str, purpose: str='general') -> Dict:
        """
        Track an LLM API call

        Args:
            model: Model name
            provider: Provider (openai, anthropic)
            tokens_input: Input tokens
            tokens_output: Output tokens
            stage: Pipeline stage making the call
            card_id: Card ID
            purpose: Purpose of call (developer-a, code-review, etc.)

        Returns:
            Dict with cost info and budget status

        Raises:
            BudgetExceededError: If budget limit exceeded
        """
        cost = ModelPricing.get_cost(model, tokens_input, tokens_output)
        call = LLMCall(timestamp=datetime.utcnow().isoformat() + 'Z', model=model, provider=provider, tokens_input=tokens_input, tokens_output=tokens_output, cost=cost, stage=stage, card_id=card_id, purpose=purpose)
        self._check_budgets(cost)
        self.calls.append(call)
        self._save_calls()
        return {'cost': cost, 'total_tokens': tokens_input + tokens_output, 'daily_usage': self.get_daily_cost(), 'monthly_usage': self.get_monthly_cost(), 'daily_budget': self.daily_budget, 'monthly_budget': self.monthly_budget, 'daily_remaining': self._get_daily_remaining(), 'monthly_remaining': self._get_monthly_remaining(), 'alert': self._check_alert_threshold()}

    def _check_budgets(self, additional_cost: float):
        """
        Check if adding cost would exceed budget

        Raises:
            BudgetExceededError: If budget would be exceeded
        """
        daily_cost = self.get_daily_cost()
        monthly_cost = self.get_monthly_cost()
        if self.daily_budget and daily_cost + additional_cost > self.daily_budget:
            raise BudgetExceededError(f'Daily budget exceeded: ${daily_cost:.2f} + ${additional_cost:.2f} > ${self.daily_budget:.2f}')
        if self.monthly_budget and monthly_cost + additional_cost > self.monthly_budget:
            raise BudgetExceededError(f'Monthly budget exceeded: ${monthly_cost:.2f} + ${additional_cost:.2f} > ${self.monthly_budget:.2f}')

    def _check_alert_threshold(self) -> Optional[str]:
        """Check if alert threshold exceeded"""
        alerts = []
        if self.daily_budget:
            daily_usage = self.get_daily_cost() / self.daily_budget
            if daily_usage >= self.alert_threshold:
                alerts.append(f'Daily budget {daily_usage * 100:.0f}% used')
        if self.monthly_budget:
            monthly_usage = self.get_monthly_cost() / self.monthly_budget
            if monthly_usage >= self.alert_threshold:
                alerts.append(f'Monthly budget {monthly_usage * 100:.0f}% used')
        return '; '.join(alerts) if alerts else None

    def _get_daily_remaining(self) -> Optional[float]:
        """Get remaining daily budget"""
        if not self.daily_budget:
            return None
        return max(0, self.daily_budget - self.get_daily_cost())

    def _get_monthly_remaining(self) -> Optional[float]:
        """Get remaining monthly budget"""
        if not self.monthly_budget:
            return None
        return max(0, self.monthly_budget - self.get_monthly_cost())

    def get_daily_cost(self) -> float:
        """Get total cost for today"""
        today = datetime.utcnow().date()
        daily_calls = [call for call in self.calls if datetime.fromisoformat(call.timestamp.replace('Z', '+00:00')).date() == today]
        return sum((call.cost for call in daily_calls))

    def get_monthly_cost(self) -> float:
        """Get total cost for this month"""
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()
        monthly_calls = [call for call in self.calls if datetime.fromisoformat(call.timestamp.replace('Z', '+00:00')).date() >= month_start]
        return sum((call.cost for call in monthly_calls))

    def get_cost_by_stage(self, card_id: Optional[str]=None) -> Dict[str, float]:
        """Get cost breakdown by pipeline stage"""
        calls = self.calls
        if card_id:
            calls = [c for c in calls if c.card_id == card_id]
        by_stage = {}
        for call in calls:
            by_stage[call.stage] = by_stage.get(call.stage, 0) + call.cost
        return by_stage

    def get_cost_by_model(self) -> Dict[str, float]:
        """Get cost breakdown by model"""
        by_model = {}
        for call in self.calls:
            by_model[call.model] = by_model.get(call.model, 0) + call.cost
        return by_model

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        total_calls = len(self.calls)
        total_cost = sum((call.cost for call in self.calls))
        total_tokens = sum((call.tokens_input + call.tokens_output for call in self.calls))
        return {'total_calls': total_calls, 'total_cost': total_cost, 'total_tokens': total_tokens, 'daily_cost': self.get_daily_cost(), 'monthly_cost': self.get_monthly_cost(), 'daily_budget': self.daily_budget, 'monthly_budget': self.monthly_budget, 'daily_remaining': self._get_daily_remaining(), 'monthly_remaining': self._get_monthly_remaining(), 'average_cost_per_call': total_cost / total_calls if total_calls > 0 else 0, 'by_stage': self.get_cost_by_stage(), 'by_model': self.get_cost_by_model()}

    def cleanup_old_records(self, days: int=90):
        """Remove records older than X days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        self.calls = [call for call in self.calls if datetime.fromisoformat(call.timestamp.replace('Z', '+00:00')) >= cutoff]
        self._save_calls()
if __name__ == '__main__':
    'Example usage and testing'
    
    logger.log('Cost Tracker - Example Usage', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    tracker = CostTracker(storage_path='/tmp/test_costs.json', daily_budget=10.0, monthly_budget=200.0)
    
    logger.log(f'Budgets: Daily=${tracker.daily_budget}, Monthly=${tracker.monthly_budget}\n', 'INFO')
    
    logger.log('1. Tracking GPT-4o call (developer-a)...', 'INFO')
    result = tracker.track_call(model='gpt-4o', provider='openai', tokens_input=5000, tokens_output=2000, stage='development', card_id='card-001', purpose='developer-a')
    
    logger.log(f"   Cost: ${result['cost']:.4f}", 'INFO')
    
    logger.log(f"   Daily usage: ${result['daily_usage']:.2f} / ${result['daily_budget']:.2f}", 'INFO')
    
    logger.log(f"   Remaining: ${result['daily_remaining']:.2f}", 'INFO')
    
    logger.log('\n2. Tracking Claude 3.5 Sonnet call (code-review)...', 'INFO')
    result = tracker.track_call(model='claude-3-5-sonnet', provider='anthropic', tokens_input=8000, tokens_output=3000, stage='code_review', card_id='card-001', purpose='code-review')
    
    logger.log(f"   Cost: ${result['cost']:.4f}", 'INFO')
    
    logger.log(f"   Daily usage: ${result['daily_usage']:.2f}", 'INFO')
    if result['alert']:
        
        logger.log(f"   ⚠️  ALERT: {result['alert']}", 'INFO')
    
    logger.log('\n3. Statistics:', 'INFO')
    stats = tracker.get_statistics()
    
    logger.log(f"   Total calls: {stats['total_calls']}", 'INFO')
    
    logger.log(f"   Total cost: ${stats['total_cost']:.2f}", 'INFO')
    
    logger.log(f"   Total tokens: {stats['total_tokens']:,}", 'INFO')
    
    logger.log(f"   Average cost/call: ${stats['average_cost_per_call']:.4f}", 'INFO')
    
    logger.log(f'\n   By stage:', 'INFO')
    for stage, cost in stats['by_stage'].items():
        
        logger.log(f'      {stage}: ${cost:.4f}', 'INFO')
    
    logger.log(f'\n   By model:', 'INFO')
    for model, cost in stats['by_model'].items():
        
        logger.log(f'      {model}: ${cost:.4f}', 'INFO')
    
    logger.log('\n4. Testing budget enforcement...', 'INFO')
    try:
        for i in range(100):
            tracker.track_call(model='gpt-4o', provider='openai', tokens_input=10000, tokens_output=5000, stage='test', card_id='card-002', purpose='budget-test')
    except BudgetExceededError as e:
        
        logger.log(f'   ✅ Budget enforcement working: {e}', 'INFO')
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('✅ Cost tracker working correctly!', 'INFO')