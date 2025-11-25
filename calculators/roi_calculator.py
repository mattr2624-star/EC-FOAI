"""
ROI Calculation Engine

Implements:
1. Basic ROI: (Benefit - Cost) / Cost × 100%
2. NPV at 10% discount rate
3. Payback Period
4. Risk-Adjusted Value
"""

from typing import List, Tuple
import numpy as np
from models.data_models import AIUseCase, ROIMetrics, RiskLevel


class ROICalculator:
    """
    Calculates ROI metrics for AI use cases.
    """
    
    DISCOUNT_RATE = 0.10  # 10% annual discount rate
    ANALYSIS_YEARS = 3    # 3-year analysis horizon
    
    # Risk multipliers for risk-adjusted value
    RISK_MULTIPLIERS = {
        RiskLevel.LOW: 0.95,      # 5% risk discount
        RiskLevel.MEDIUM: 0.80,   # 20% risk discount
        RiskLevel.HIGH: 0.60      # 40% risk discount
    }
    
    def calculate_metrics(self, use_case: AIUseCase) -> ROIMetrics:
        """
        Calculate all ROI metrics for a single use case.
        
        Args:
            use_case: The AI use case to analyze
            
        Returns:
            ROIMetrics with all calculated values
        """
        # Calculate 3-year cash flows
        cash_flows = self._generate_cash_flows(use_case)
        
        # Total costs and benefits over 3 years
        three_year_cost = use_case.initial_cost + (use_case.annual_cost * self.ANALYSIS_YEARS)
        three_year_benefit = self._calculate_total_benefit(use_case)
        
        # Basic ROI
        basic_roi = self._calculate_basic_roi(three_year_benefit, three_year_cost)
        
        # NPV
        npv = self._calculate_npv(cash_flows)
        
        # Payback Period
        payback_months = self._calculate_payback_period(use_case)
        
        # Risk-Adjusted Value
        risk_adjusted = self._calculate_risk_adjusted_value(npv, use_case.risk_level)
        
        # Annual net benefit (steady state)
        annual_net = use_case.annual_benefit - use_case.annual_cost
        
        return ROIMetrics(
            use_case_id=use_case.id,
            basic_roi_percent=basic_roi,
            npv=npv,
            payback_months=payback_months,
            risk_adjusted_value=risk_adjusted,
            three_year_benefit=three_year_benefit,
            three_year_cost=three_year_cost,
            annual_net_benefit=annual_net
        )
    
    def calculate_batch(self, use_cases: List[AIUseCase]) -> List[ROIMetrics]:
        """Calculate ROI metrics for multiple use cases."""
        return [self.calculate_metrics(uc) for uc in use_cases]
    
    def _generate_cash_flows(self, use_case: AIUseCase) -> List[float]:
        """
        Generate monthly cash flows for the analysis period.
        
        Returns a list of 36 monthly cash flows (3 years).
        """
        months = self.ANALYSIS_YEARS * 12
        cash_flows = []
        
        for month in range(months):
            flow = 0.0
            
            # Initial cost in month 0
            if month == 0:
                flow -= use_case.initial_cost
            
            # Monthly operating cost (spread annual cost)
            flow -= use_case.annual_cost / 12
            
            # Benefits start after implementation and benefit delay
            benefit_start = use_case.implementation_months + use_case.benefit_start_month - 1
            if month >= benefit_start:
                flow += use_case.annual_benefit / 12
            
            cash_flows.append(flow)
        
        return cash_flows
    
    def _calculate_basic_roi(self, total_benefit: float, total_cost: float) -> float:
        """
        Calculate simple ROI percentage.
        
        Formula: (Benefit - Cost) / Cost × 100
        """
        if total_cost == 0:
            return 0.0
        
        return ((total_benefit - total_cost) / total_cost) * 100
    
    def _calculate_npv(self, cash_flows: List[float]) -> float:
        """
        Calculate Net Present Value using monthly discounting.
        
        Formula: NPV = Σ(CF_t / (1 + r)^t)
        Where r is the monthly discount rate.
        """
        monthly_rate = (1 + self.DISCOUNT_RATE) ** (1/12) - 1
        
        npv = 0.0
        for t, cf in enumerate(cash_flows):
            npv += cf / ((1 + monthly_rate) ** t)
        
        return round(npv, 2)
    
    def _calculate_payback_period(self, use_case: AIUseCase) -> float:
        """
        Calculate the payback period in months.
        
        Time to recover the initial investment from net cash flows.
        """
        if use_case.annual_benefit <= use_case.annual_cost:
            return float('inf')  # Never pays back
        
        monthly_net_benefit = (use_case.annual_benefit - use_case.annual_cost) / 12
        
        if monthly_net_benefit <= 0:
            return float('inf')
        
        # Months to recover initial investment after benefits start
        benefit_start = use_case.implementation_months + use_case.benefit_start_month - 1
        months_to_recover = use_case.initial_cost / monthly_net_benefit
        
        return round(benefit_start + months_to_recover, 1)
    
    def _calculate_risk_adjusted_value(self, base_value: float, risk_level: RiskLevel) -> float:
        """
        Calculate risk-adjusted value.
        
        Formula: Value × (1 - Risk Factor)
        Higher risk = lower adjusted value
        """
        multiplier = self.RISK_MULTIPLIERS.get(risk_level, 0.80)
        return round(base_value * multiplier, 2)
    
    def _calculate_total_benefit(self, use_case: AIUseCase) -> float:
        """
        Calculate total benefits over the 3-year period,
        accounting for implementation delay.
        """
        # Months when benefits are realized
        benefit_start = use_case.implementation_months + use_case.benefit_start_month - 1
        benefit_months = max(0, (self.ANALYSIS_YEARS * 12) - benefit_start)
        
        return (use_case.annual_benefit / 12) * benefit_months
    
    def get_roi_summary(self, metrics: List[ROIMetrics]) -> dict:
        """
        Generate a summary of ROI metrics across all use cases.
        """
        if not metrics:
            return {}
        
        return {
            "total_npv": sum(m.npv for m in metrics),
            "average_roi": np.mean([m.basic_roi_percent for m in metrics]),
            "total_3yr_benefit": sum(m.three_year_benefit for m in metrics),
            "total_3yr_cost": sum(m.three_year_cost for m in metrics),
            "portfolio_roi": self._calculate_basic_roi(
                sum(m.three_year_benefit for m in metrics),
                sum(m.three_year_cost for m in metrics)
            ),
            "average_payback_months": np.mean([
                m.payback_months for m in metrics 
                if m.payback_months != float('inf')
            ]) if any(m.payback_months != float('inf') for m in metrics) else float('inf'),
            "total_risk_adjusted_value": sum(m.risk_adjusted_value for m in metrics)
        }
    
    def format_currency(self, value: float) -> str:
        """Format a value as currency."""
        if abs(value) >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"${value/1_000:.1f}K"
        else:
            return f"${value:.2f}"
    
    def format_metrics_table(self, use_case: AIUseCase, metrics: ROIMetrics) -> str:
        """Generate a formatted table of metrics for display."""
        lines = [
            f"📊 ROI Analysis: {use_case.name}",
            "=" * 50,
            f"Initial Investment:    {self.format_currency(use_case.initial_cost)}",
            f"Annual Operating Cost: {self.format_currency(use_case.annual_cost)}",
            f"Annual Benefit:        {self.format_currency(use_case.annual_benefit)}",
            "-" * 50,
            f"3-Year Total Cost:     {self.format_currency(metrics.three_year_cost)}",
            f"3-Year Total Benefit:  {self.format_currency(metrics.three_year_benefit)}",
            "-" * 50,
            f"Basic ROI:             {metrics.basic_roi_percent:.1f}%",
            f"NPV (10% discount):    {self.format_currency(metrics.npv)}",
            f"Payback Period:        {metrics.payback_months:.1f} months" if metrics.payback_months != float('inf') else "Payback Period:        Never",
            f"Risk-Adjusted Value:   {self.format_currency(metrics.risk_adjusted_value)}",
            "=" * 50
        ]
        return "\n".join(lines)

