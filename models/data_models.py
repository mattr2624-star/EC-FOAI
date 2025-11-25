"""
Data models for the AI ROI and Roadmap Canvas Agent.
Uses Pydantic for validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from enum import Enum


class EffortLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ImpactLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TimeHorizon(str, Enum):
    Q1 = "Q1 (0-3 months)"
    YEAR_1 = "Year 1 (3-12 months)"
    YEAR_3 = "3-Year (1-3 years)"


class AIUseCase(BaseModel):
    """Represents a single AI use case captured during the interview."""
    id: str
    name: str = Field(..., description="Name of the AI initiative")
    problem_statement: str = Field(..., description="Business problem being addressed")
    kpis: List[str] = Field(default_factory=list, description="Key performance indicators")
    
    # Financial inputs
    initial_cost: float = Field(..., ge=0, description="One-time implementation cost ($)")
    annual_cost: float = Field(default=0, ge=0, description="Annual operating cost ($)")
    annual_benefit: float = Field(..., ge=0, description="Annual expected benefit ($)")
    
    # Timeline
    implementation_months: int = Field(..., ge=1, description="Months to implement")
    benefit_start_month: int = Field(default=1, ge=1, description="Month when benefits begin")
    
    # Qualitative factors
    effort_level: EffortLevel = Field(..., description="Implementation effort")
    impact_level: ImpactLevel = Field(..., description="Business impact potential")
    risk_level: RiskLevel = Field(..., description="Risk assessment")
    
    # Dependencies and requirements
    dependencies: List[str] = Field(default_factory=list, description="Dependencies on other projects")
    skills_required: List[str] = Field(default_factory=list, description="Skills needed")
    technology_required: List[str] = Field(default_factory=list, description="Technology stack needed")
    
    # Soft benefits
    soft_benefits: List[str] = Field(default_factory=list, description="Non-quantifiable benefits")
    
    # Risk details
    risk_factors: List[str] = Field(default_factory=list, description="Specific risk factors")


class ROIMetrics(BaseModel):
    """Computed ROI metrics for a use case."""
    use_case_id: str
    basic_roi_percent: float = Field(..., description="Simple ROI percentage")
    npv: float = Field(..., description="Net Present Value at 10% discount")
    payback_months: float = Field(..., description="Payback period in months")
    risk_adjusted_value: float = Field(..., description="Risk-adjusted expected value")
    three_year_benefit: float = Field(..., description="Total 3-year benefit")
    three_year_cost: float = Field(..., description="Total 3-year cost")
    annual_net_benefit: float = Field(..., description="Net annual benefit")


class PortfolioItem(BaseModel):
    """A use case with its portfolio optimization score."""
    use_case: AIUseCase
    roi_metrics: ROIMetrics
    priority_score: float = Field(..., description="Composite priority score")
    quadrant: str = Field(..., description="Impact-Effort quadrant")
    selected: bool = Field(default=False, description="Selected for portfolio")
    selection_rationale: str = Field(default="", description="Why selected/not selected")


class RoadmapItem(BaseModel):
    """A use case assigned to a roadmap phase."""
    use_case: AIUseCase
    roi_metrics: ROIMetrics
    time_horizon: TimeHorizon
    start_date: date
    end_date: date
    milestones: List[str] = Field(default_factory=list)
    phase_rationale: str = Field(default="", description="Why assigned to this phase")


# Canvas Section Models

class CanvasHeader(BaseModel):
    """Header section of the canvas."""
    canvas_title: str = "AI ROI & Roadmap Canvas"
    organization_name: str
    designed_by: str
    designed_for: str
    date: date
    version: str = "1.0"


class CanvasObjectives(BaseModel):
    """Objectives section of the canvas."""
    primary_goal: str
    strategic_focus: List[str] = Field(default_factory=list)


class CanvasInputs(BaseModel):
    """Inputs section of the canvas."""
    resources: List[str] = Field(default_factory=list)
    personnel: List[str] = Field(default_factory=list)
    external_support: List[str] = Field(default_factory=list)


class CanvasImpacts(BaseModel):
    """Impacts section of the canvas."""
    hard_benefits: List[str] = Field(default_factory=list)
    soft_benefits: List[str] = Field(default_factory=list)


class CanvasTimeline(BaseModel):
    """Timeline section with initiatives."""
    class InitiativeTimeline(BaseModel):
        ai_initiative: str
        start_date: date
        end_date: date
        milestones: List[str] = Field(default_factory=list)
    
    initiatives: List[InitiativeTimeline] = Field(default_factory=list)


class CanvasRisks(BaseModel):
    """Risks section of the canvas."""
    risks: List[str] = Field(default_factory=list)
    mitigations: List[str] = Field(default_factory=list)


class CanvasCapabilities(BaseModel):
    """Capabilities section of the canvas."""
    skills_needed: List[str] = Field(default_factory=list)
    technology: List[str] = Field(default_factory=list)


class CanvasCosts(BaseModel):
    """Costs section of the canvas."""
    near_term: float = Field(default=0, description="Q1 costs")
    long_term: float = Field(default=0, description="1-3 year costs")
    annual_maintenance: float = Field(default=0, description="Ongoing annual costs")


class CanvasBenefits(BaseModel):
    """Benefits section of the canvas."""
    near_term: float = Field(default=0, description="Q1 benefits")
    long_term: float = Field(default=0, description="1-3 year benefits")
    soft_benefits: List[str] = Field(default_factory=list)


class CanvasPortfolioROI(BaseModel):
    """Portfolio ROI section of the canvas."""
    near_term_roi_percent: float = Field(default=0)
    long_term_roi_percent: float = Field(default=0)
    portfolio_note: str = ""


class CanvasFooter(BaseModel):
    """Footer section of the canvas."""
    credit_line: str = "Generated by AI ROI & Roadmap Canvas Agent"


class AIROICanvas(BaseModel):
    """Complete AI ROI & Roadmap Canvas."""
    header: CanvasHeader
    objectives: CanvasObjectives
    inputs: CanvasInputs
    impacts: CanvasImpacts
    timeline: CanvasTimeline
    risks: CanvasRisks
    capabilities: CanvasCapabilities
    costs: CanvasCosts
    benefits: CanvasBenefits
    portfolio_roi: CanvasPortfolioROI
    footer: CanvasFooter
    
    # Additional data for reference
    use_cases: List[AIUseCase] = Field(default_factory=list)
    portfolio_items: List[PortfolioItem] = Field(default_factory=list)
    roadmap_items: List[RoadmapItem] = Field(default_factory=list)

