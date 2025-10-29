from artemis_logger import get_logger
logger = get_logger('token_savings_tracker')
'\nToken Savings Tracker\n\nWHY: Tracks token savings across all queries for cost analysis and optimization.\n\nRESPONSIBILITY:\n- Record metrics for each query execution\n- Aggregate metrics by query type\n- Calculate overall and per-type savings\n- Provide comprehensive dashboard reporting\n\nPATTERNS:\n- Guard clauses for early returns (no nested ifs)\n- Extracted methods for query type vs overall metrics\n- Cost estimation formulas\n'
from typing import Dict, Any, Optional
from ai_query.query_type import QueryType
from ai_query.token_savings_metrics import TokenSavingsMetrics

class TokenSavingsTracker:
    """
    Tracks token savings across all queries

    Single Responsibility: Collect and report token savings metrics
    """

    def __init__(self):
        """Initialize token savings tracker"""
        self.metrics_by_type: Dict[str, Dict[str, Any]] = {}
        self.total_queries = 0
        self.total_tokens_saved = 0
        self.total_cost_saved = 0.0

    def record_query(self, query_type: QueryType, tokens_used: int, tokens_saved: int, cost_usd: float, kg_patterns_found: int):
        """
        Record metrics for a single query

        Args:
            query_type: Type of query
            tokens_used: Actual tokens used
            tokens_saved: Estimated tokens saved via KG-First
            cost_usd: Actual cost
            kg_patterns_found: Number of KG patterns found
        """
        type_name = query_type.value
        if type_name not in self.metrics_by_type:
            self.metrics_by_type[type_name] = {'queries': 0, 'tokens_used': 0, 'tokens_saved': 0, 'cost_usd': 0.0, 'kg_hits': 0, 'kg_misses': 0}
        metrics = self.metrics_by_type[type_name]
        metrics['queries'] += 1
        metrics['tokens_used'] += tokens_used
        metrics['tokens_saved'] += tokens_saved
        metrics['cost_usd'] += cost_usd
        if kg_patterns_found > 0:
            metrics['kg_hits'] += 1
        else:
            metrics['kg_misses'] += 1
        self.total_queries += 1
        self.total_tokens_saved += tokens_saved
        cost_saved = tokens_saved / 1000 * 0.015
        metrics['cost_saved'] = metrics.get('cost_saved', 0.0) + cost_saved
        self.total_cost_saved += cost_saved

    def get_metrics(self, query_type: Optional[QueryType]=None) -> TokenSavingsMetrics:
        """
        Get metrics for a specific query type or overall

        Args:
            query_type: Optional query type to filter by

        Returns:
            TokenSavingsMetrics with aggregated data
        """
        if query_type:
            return self._get_query_type_metrics(query_type)
        return self._get_overall_metrics()

    def _get_query_type_metrics(self, query_type: QueryType) -> TokenSavingsMetrics:
        """
        Get metrics for a specific query type.

        WHY: Extracted to avoid nested if statements (Early Return Pattern).

        Args:
            query_type: Query type to get metrics for

        Returns:
            TokenSavingsMetrics for the specified query type
        """
        type_name = query_type.value
        if type_name not in self.metrics_by_type:
            return TokenSavingsMetrics(query_type=type_name, queries_executed=0, total_tokens_used=0, total_tokens_saved=0, total_cost_usd=0.0, total_cost_saved_usd=0.0, average_savings_percent=0.0, kg_hits=0, kg_misses=0, kg_hit_rate=0.0)
        metrics = self.metrics_by_type[type_name]
        total_tokens = metrics['tokens_used'] + metrics['tokens_saved']
        savings_percent = metrics['tokens_saved'] / total_tokens * 100 if total_tokens > 0 else 0.0
        kg_total = metrics['kg_hits'] + metrics['kg_misses']
        kg_hit_rate = metrics['kg_hits'] / kg_total if kg_total > 0 else 0.0
        return TokenSavingsMetrics(query_type=type_name, queries_executed=metrics['queries'], total_tokens_used=metrics['tokens_used'], total_tokens_saved=metrics['tokens_saved'], total_cost_usd=metrics['cost_usd'], total_cost_saved_usd=metrics.get('cost_saved', 0.0), average_savings_percent=savings_percent, kg_hits=metrics['kg_hits'], kg_misses=metrics['kg_misses'], kg_hit_rate=kg_hit_rate)

    def _get_overall_metrics(self) -> TokenSavingsMetrics:
        """
        Get overall metrics across all query types.

        WHY: Extracted to avoid nested if/else (Early Return Pattern).

        Returns:
            TokenSavingsMetrics for all query types combined
        """
        total_tokens_used = sum((m['tokens_used'] for m in self.metrics_by_type.values()))
        total_cost = sum((m['cost_usd'] for m in self.metrics_by_type.values()))
        total_kg_hits = sum((m['kg_hits'] for m in self.metrics_by_type.values()))
        total_kg_misses = sum((m['kg_misses'] for m in self.metrics_by_type.values()))
        total_tokens = total_tokens_used + self.total_tokens_saved
        savings_percent = self.total_tokens_saved / total_tokens * 100 if total_tokens > 0 else 0.0
        kg_total = total_kg_hits + total_kg_misses
        kg_hit_rate = total_kg_hits / kg_total if kg_total > 0 else 0.0
        return TokenSavingsMetrics(query_type='OVERALL', queries_executed=self.total_queries, total_tokens_used=total_tokens_used, total_tokens_saved=self.total_tokens_saved, total_cost_usd=total_cost, total_cost_saved_usd=self.total_cost_saved, average_savings_percent=savings_percent, kg_hits=total_kg_hits, kg_misses=total_kg_misses, kg_hit_rate=kg_hit_rate)

    def print_dashboard(self):
        """Print a comprehensive metrics dashboard"""
        
        logger.log('=' * 80, 'INFO')
        
        logger.log('TOKEN SAVINGS DASHBOARD - AI Query Service', 'INFO')
        
        logger.log('=' * 80, 'INFO')
        
        pass
        overall = self.get_metrics()
        
        logger.log('OVERALL METRICS', 'INFO')
        
        logger.log('-' * 80, 'INFO')
        
        logger.log(f'Total Queries:        {overall.queries_executed:,}', 'INFO')
        
        logger.log(f'Tokens Used:          {overall.total_tokens_used:,}', 'INFO')
        
        logger.log(f'Tokens Saved:         {overall.total_tokens_saved:,}', 'INFO')
        
        logger.log(f'Savings Rate:         {overall.average_savings_percent:.1f}%', 'INFO')
        
        logger.log(f'KG Hit Rate:          {overall.kg_hit_rate:.1f}% ({overall.kg_hits}/{overall.kg_hits + overall.kg_misses})', 'INFO')
        
        logger.log(f'Cost (actual):        ${overall.total_cost_usd:.4f}', 'INFO')
        
        logger.log(f'Cost (saved):         ${overall.total_cost_saved_usd:.4f}', 'INFO')
        
        pass
        
        logger.log('BREAKDOWN BY QUERY TYPE', 'INFO')
        
        logger.log('-' * 80, 'INFO')
        
        logger.log(f"{'Type':<25} {'Queries':<10} {'Tokens Saved':<15} {'Savings %':<12} {'KG Hit %':<10}", 'INFO')
        
        logger.log('-' * 80, 'INFO')
        for query_type_str in sorted(self.metrics_by_type.keys()):
            query_type = QueryType(query_type_str)
            metrics = self.get_metrics(query_type)
            
            logger.log(f'{metrics.query_type:<25} {metrics.queries_executed:<10} {metrics.total_tokens_saved:<15,} {metrics.average_savings_percent:<11.1f}% {metrics.kg_hit_rate:<9.1f}%', 'INFO')
        
        logger.log('=' * 80, 'INFO')
        
        pass
        if overall.queries_executed > 0:
            queries_per_day = overall.queries_executed
            cost_saved_per_day = overall.total_cost_saved_usd
            annual_savings = cost_saved_per_day * 365
            
            logger.log('PROJECTED ANNUAL SAVINGS (at current rate)', 'INFO')
            
            logger.log('-' * 80, 'INFO')
            
            logger.log(f'Daily cost savings:   ${cost_saved_per_day:.2f}', 'INFO')
            
            logger.log(f'Annual cost savings:  ${annual_savings:.2f}', 'INFO')
            
            logger.log('=' * 80, 'INFO')