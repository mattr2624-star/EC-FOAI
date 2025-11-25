"""
ROI Calculation Engine for AI Initiative Assessment

Provides comprehensive ROI analysis including:
- Simple ROI calculation
- Net Present Value (NPV) at 10% discount rate
- Payback period analysis
- Risk-adjusted value scoring
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class UseCase:
    """Represents an AI use case with all relevant metrics"""
    id: str
    name: str
    description: str
    problem_statement: str
    
    # KPIs and Benefits
    kpis: List[str]
    hard_benefits: float  # Annual quantifiable benefits ($)
    soft_benefits: List[str]  # Qualitative benefits
    
    # Costs
    initial_cost: float  # One-time implementation cost ($)
    annual_operating_cost: float  # Ongoing annual cost ($)
    
    # Effort and Timeline
    effort_score: int  # 1-10 scale (1=low effort, 10=high effort)
    implementation_months: int  # Months to implement
    
    # Risk Assessment
    risk_score: int  # 1-10 scale (1=low risk, 10=high risk)
    risk_factors: List[str]
    
    # Dependencies
    dependencies: List[str]
    required_capabilities: List[str]
    
    # Calculated fields (populated by ROI engine)
    simple_roi: float = 0.0
    npv_3year: float = 0.0
    payback_months: float = 0.0
    risk_adjusted_value: float = 0.0
    impact_score: float = 0.0
    priority_score: float = 0.0
    timeline_phase: str = ""


class ROIEngine:
    """
    Calculates comprehensive ROI metrics for AI use cases
    """
    
    DISCOUNT_RATE = 0.10  # 10% annual discount rate
    ANALYSIS_YEARS = 3  # 3-year analysis period
    
    def __init__(self):
        self.use_cases: List[UseCase] = []
    
    def add_use_case(self, use_case: UseCase) -> UseCase:
        """Add a use case and calculate its ROI metrics"""
        self._calculate_metrics(use_case)
        self.use_cases.append(use_case)
        return use_case
    
    def _calculate_metrics(self, uc: UseCase) -> None:
        """Calculate all ROI metrics for a use case"""
        uc.simple_roi = self._calculate_simple_roi(uc)
        uc.npv_3year = self._calculate_npv(uc)
        uc.payback_months = self._calculate_payback_period(uc)
        uc.risk_adjusted_value = self._calculate_risk_adjusted_value(uc)
        uc.impact_score = self._calculate_impact_score(uc)
        uc.priority_score = self._calculate_priority_score(uc)
        uc.timeline_phase = self._assign_timeline_phase(uc)
    
    def _calculate_simple_roi(self, uc: UseCase) -> float:
        """
        Calculate Simple ROI = (Benefit - Cost) / Cost
        Uses first-year benefits vs total first-year costs
        """
        total_first_year_cost = uc.initial_cost + uc.annual_operating_cost
        if total_first_year_cost <= 0:
            return 0.0
        
        net_benefit = uc.hard_benefits - total_first_year_cost
        roi = (net_benefit / total_first_year_cost) * 100
        return round(roi, 2)
    
    def _calculate_npv(self, uc: UseCase, years: int = None) -> float:
        """
        Calculate Net Present Value at 10% discount rate
        NPV = Σ (Cash Flow / (1 + r)^t) - Initial Investment
        """
        if years is None:
            years = self.ANALYSIS_YEARS
        
        # Initial investment (negative cash flow at t=0)
        npv = -uc.initial_cost
        
        # Annual net cash flows
        annual_net_benefit = uc.hard_benefits - uc.annual_operating_cost
        
        for year in range(1, years + 1):
            # Discount factor for each year
            discount_factor = (1 + self.DISCOUNT_RATE) ** year
            discounted_cash_flow = annual_net_benefit / discount_factor
            npv += discounted_cash_flow
        
        return round(npv, 2)
    
    def _calculate_payback_period(self, uc: UseCase) -> float:
        """
        Calculate payback period in months
        Time to recover initial investment from net benefits
        """
        annual_net_benefit = uc.hard_benefits - uc.annual_operating_cost
        
        if annual_net_benefit <= 0:
            return float('inf')  # Never pays back
        
        monthly_net_benefit = annual_net_benefit / 12
        payback_months = uc.initial_cost / monthly_net_benefit
        
        return round(payback_months, 1)
    
    def _calculate_risk_adjusted_value(self, uc: UseCase) -> float:
        """
        Calculate risk-adjusted value
        RAV = NPV × (1 - Risk Factor)
        where Risk Factor = risk_score / 10
        """
        risk_factor = uc.risk_score / 10.0
        rav = uc.npv_3year * (1 - risk_factor)
        return round(rav, 2)
    
    def _calculate_impact_score(self, uc: UseCase) -> float:
        """
        Calculate impact score (1-10) based on benefits and strategic value
        """
        # Normalize hard benefits (assuming max $5M annual benefit)
        benefit_score = min(10, (uc.hard_benefits / 500000) * 10)
        
        # Soft benefits contribution (each soft benefit adds 0.5)
        soft_benefit_score = min(3, len(uc.soft_benefits) * 0.5)
        
        # NPV contribution
        npv_score = min(3, max(0, uc.npv_3year / 500000) * 3)
        
        impact = (benefit_score * 0.5) + (soft_benefit_score) + (npv_score)
        return round(min(10, max(1, impact)), 1)
    
    def _calculate_priority_score(self, uc: UseCase) -> float:
        """
        Calculate priority score based on impact, effort, and risk
        Priority = (Impact × (11 - Effort) × (11 - Risk)) / 100
        """
        effort_factor = 11 - uc.effort_score
        risk_factor = 11 - uc.risk_score
        
        priority = (uc.impact_score * effort_factor * risk_factor) / 100
        return round(priority, 2)
    
    def _assign_timeline_phase(self, uc: UseCase) -> str:
        """
        Assign project to timeline phase based on priority and implementation time
        - Q1: High priority, quick wins (≤3 months)
        - 1-Year: Medium priority or medium complexity
        - 3-Year: Lower priority or high complexity
        """
        if uc.implementation_months <= 3 and uc.priority_score >= 3:
            return "Q1"
        elif uc.implementation_months <= 12 and uc.priority_score >= 2:
            return "1-Year"
        else:
            return "3-Year"
    
    def get_portfolio_summary(self) -> Dict:
        """Generate portfolio summary statistics"""
        if not self.use_cases:
            return {}
        
        total_initial_cost = sum(uc.initial_cost for uc in self.use_cases)
        total_annual_cost = sum(uc.annual_operating_cost for uc in self.use_cases)
        total_annual_benefit = sum(uc.hard_benefits for uc in self.use_cases)
        total_npv = sum(uc.npv_3year for uc in self.use_cases)
        
        # Portfolio ROI
        if total_initial_cost + total_annual_cost > 0:
            portfolio_roi = ((total_annual_benefit - total_annual_cost) / 
                           (total_initial_cost + total_annual_cost)) * 100
        else:
            portfolio_roi = 0
        
        # Average payback
        valid_paybacks = [uc.payback_months for uc in self.use_cases 
                         if uc.payback_months != float('inf')]
        avg_payback = np.mean(valid_paybacks) if valid_paybacks else 0
        
        return {
            "total_use_cases": len(self.use_cases),
            "total_initial_investment": round(total_initial_cost, 2),
            "total_annual_operating_cost": round(total_annual_cost, 2),
            "total_annual_benefit": round(total_annual_benefit, 2),
            "portfolio_npv": round(total_npv, 2),
            "portfolio_roi_percent": round(portfolio_roi, 2),
            "average_payback_months": round(avg_payback, 1),
            "q1_projects": len([uc for uc in self.use_cases if uc.timeline_phase == "Q1"]),
            "year1_projects": len([uc for uc in self.use_cases if uc.timeline_phase == "1-Year"]),
            "year3_projects": len([uc for uc in self.use_cases if uc.timeline_phase == "3-Year"])
        }
    
    def to_dict(self) -> List[Dict]:
        """Convert all use cases to dictionary format"""
        return [
            {
                "id": uc.id,
                "name": uc.name,
                "description": uc.description,
                "problem_statement": uc.problem_statement,
                "kpis": uc.kpis,
                "hard_benefits": uc.hard_benefits,
                "soft_benefits": uc.soft_benefits,
                "initial_cost": uc.initial_cost,
                "annual_operating_cost": uc.annual_operating_cost,
                "effort_score": uc.effort_score,
                "implementation_months": uc.implementation_months,
                "risk_score": uc.risk_score,
                "risk_factors": uc.risk_factors,
                "dependencies": uc.dependencies,
                "required_capabilities": uc.required_capabilities,
                "simple_roi": uc.simple_roi,
                "npv_3year": uc.npv_3year,
                "payback_months": uc.payback_months,
                "risk_adjusted_value": uc.risk_adjusted_value,
                "impact_score": uc.impact_score,
                "priority_score": uc.priority_score,
                "timeline_phase": uc.timeline_phase
            }
            for uc in self.use_cases
        ]


def create_sample_use_case(index: int) -> Dict:
    """Generate sample use case data for testing"""
    samples = [
        {
            "name": "Customer Service Chatbot",
            "description": "AI-powered chatbot to handle tier-1 customer inquiries",
            "problem_statement": "High call volumes causing long wait times and customer dissatisfaction",
            "kpis": ["Average Handle Time", "Customer Satisfaction Score", "First Contact Resolution"],
            "hard_benefits": 250000,
            "soft_benefits": ["Improved customer experience", "24/7 availability", "Consistent service quality"],
            "initial_cost": 150000,
            "annual_operating_cost": 50000,
            "effort_score": 4,
            "implementation_months": 3,
            "risk_score": 3,
            "risk_factors": ["Integration complexity", "Training data quality"],
            "dependencies": ["CRM system access", "Knowledge base"],
            "required_capabilities": ["NLP expertise", "Cloud infrastructure"]
        },
        {
            "name": "Predictive Maintenance System",
            "description": "ML-based system to predict equipment failures before they occur",
            "problem_statement": "Unplanned downtime costing $2M annually",
            "kpis": ["Downtime Reduction", "Maintenance Cost Savings", "Equipment Lifespan"],
            "hard_benefits": 800000,
            "soft_benefits": ["Improved safety", "Better resource planning", "Extended equipment life"],
            "initial_cost": 400000,
            "annual_operating_cost": 100000,
            "effort_score": 7,
            "implementation_months": 9,
            "risk_score": 5,
            "risk_factors": ["Sensor integration", "Model accuracy", "Change management"],
            "dependencies": ["IoT infrastructure", "Historical maintenance data"],
            "required_capabilities": ["Data engineering", "ML engineering", "IoT expertise"]
        },
        {
            "name": "Invoice Processing Automation",
            "description": "Automated extraction and processing of invoice data using OCR and AI",
            "problem_statement": "Manual invoice processing taking 15 FTE hours weekly",
            "kpis": ["Processing Time", "Error Rate", "Cost per Invoice"],
            "hard_benefits": 180000,
            "soft_benefits": ["Reduced errors", "Faster vendor payments", "Staff reallocation"],
            "initial_cost": 80000,
            "annual_operating_cost": 25000,
            "effort_score": 3,
            "implementation_months": 2,
            "risk_score": 2,
            "risk_factors": ["Document format variability"],
            "dependencies": ["ERP system integration"],
            "required_capabilities": ["OCR technology", "Process automation"]
        },
        {
            "name": "Demand Forecasting Engine",
            "description": "AI-driven demand forecasting to optimize inventory levels",
            "problem_statement": "Excess inventory costs and stockouts affecting revenue",
            "kpis": ["Forecast Accuracy", "Inventory Turnover", "Stockout Rate"],
            "hard_benefits": 500000,
            "soft_benefits": ["Better cash flow", "Improved supplier relationships", "Reduced waste"],
            "initial_cost": 250000,
            "annual_operating_cost": 75000,
            "effort_score": 6,
            "implementation_months": 6,
            "risk_score": 4,
            "risk_factors": ["Data quality", "Market volatility", "Model drift"],
            "dependencies": ["Sales data", "Supply chain system"],
            "required_capabilities": ["Time series modeling", "Data integration"]
        },
        {
            "name": "Employee Onboarding Assistant",
            "description": "AI assistant to guide new employees through onboarding process",
            "problem_statement": "Inconsistent onboarding experience and HR overhead",
            "kpis": ["Time to Productivity", "Onboarding Satisfaction", "HR Hours Saved"],
            "hard_benefits": 120000,
            "soft_benefits": ["Better employee experience", "Consistent training", "Reduced turnover"],
            "initial_cost": 60000,
            "annual_operating_cost": 20000,
            "effort_score": 3,
            "implementation_months": 2,
            "risk_score": 2,
            "risk_factors": ["Content maintenance", "System adoption"],
            "dependencies": ["HRIS integration", "Training content"],
            "required_capabilities": ["Conversational AI", "Integration skills"]
        }
    ]
    
    return samples[index % len(samples)]

