"""
Portfolio Selection Module for AI Initiative Assessment

Implements Impact-Effort matrix analysis and constraint-based portfolio optimization.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from roi_engine import UseCase


@dataclass
class PortfolioConstraints:
    """Defines constraints for portfolio selection"""
    max_budget: float = float('inf')  # Maximum total investment
    max_projects: int = 10  # Maximum number of projects
    min_roi: float = 0  # Minimum acceptable ROI percentage
    max_risk: int = 10  # Maximum acceptable risk score
    required_q1_projects: int = 1  # Minimum quick wins needed


class PortfolioSelector:
    """
    Selects optimal AI initiative portfolio based on Impact-Effort analysis
    and organizational constraints.
    """
    
    # Quadrant definitions for Impact-Effort Matrix
    QUADRANTS = {
        "quick_wins": {"impact_min": 5, "effort_max": 5, "label": "Quick Wins", "priority": 1},
        "strategic": {"impact_min": 5, "effort_min": 6, "label": "Strategic Projects", "priority": 2},
        "fill_ins": {"impact_max": 4, "effort_max": 5, "label": "Fill-Ins", "priority": 3},
        "avoid": {"impact_max": 4, "effort_min": 6, "label": "Reconsider", "priority": 4}
    }
    
    def __init__(self, constraints: Optional[PortfolioConstraints] = None):
        self.constraints = constraints or PortfolioConstraints()
        self.use_cases: List[UseCase] = []
        self.selected_portfolio: List[UseCase] = []
    
    def analyze_use_cases(self, use_cases: List[UseCase]) -> Dict:
        """
        Analyze use cases and categorize by Impact-Effort quadrant
        """
        self.use_cases = use_cases
        
        analysis = {
            "quadrants": {
                "quick_wins": [],
                "strategic": [],
                "fill_ins": [],
                "avoid": []
            },
            "matrix_data": [],
            "recommendations": []
        }
        
        for uc in use_cases:
            quadrant = self._determine_quadrant(uc)
            analysis["quadrants"][quadrant].append(uc)
            
            # Matrix visualization data
            analysis["matrix_data"].append({
                "id": uc.id,
                "name": uc.name,
                "impact": uc.impact_score,
                "effort": uc.effort_score,
                "quadrant": quadrant,
                "size": self._calculate_bubble_size(uc),
                "color": self._get_quadrant_color(quadrant)
            })
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis["quadrants"])
        
        return analysis
    
    def _determine_quadrant(self, uc: UseCase) -> str:
        """Determine which quadrant a use case belongs to"""
        if uc.impact_score >= 5:
            if uc.effort_score <= 5:
                return "quick_wins"
            else:
                return "strategic"
        else:
            if uc.effort_score <= 5:
                return "fill_ins"
            else:
                return "avoid"
    
    def _calculate_bubble_size(self, uc: UseCase) -> int:
        """Calculate bubble size for visualization based on NPV"""
        # Normalize NPV to bubble size (10-50 range)
        if uc.npv_3year <= 0:
            return 10
        size = min(50, max(10, int(uc.npv_3year / 50000) + 10))
        return size
    
    def _get_quadrant_color(self, quadrant: str) -> str:
        """Get color for quadrant visualization"""
        colors = {
            "quick_wins": "#22c55e",  # Green
            "strategic": "#3b82f6",   # Blue
            "fill_ins": "#f59e0b",    # Amber
            "avoid": "#ef4444"        # Red
        }
        return colors.get(quadrant, "#6b7280")
    
    def _generate_recommendations(self, quadrants: Dict) -> List[str]:
        """Generate strategic recommendations based on portfolio analysis"""
        recommendations = []
        
        quick_wins = quadrants["quick_wins"]
        strategic = quadrants["strategic"]
        fill_ins = quadrants["fill_ins"]
        avoid = quadrants["avoid"]
        
        if quick_wins:
            recommendations.append(
                f"🎯 Prioritize {len(quick_wins)} Quick Win(s): "
                f"{', '.join([uc.name for uc in quick_wins[:3]])}. "
                "These offer high impact with low effort."
            )
        
        if strategic:
            recommendations.append(
                f"📊 Plan {len(strategic)} Strategic Project(s): "
                f"{', '.join([uc.name for uc in strategic[:3]])}. "
                "These require significant investment but offer transformational value."
            )
        
        if fill_ins:
            recommendations.append(
                f"📋 Consider {len(fill_ins)} Fill-In Project(s) for capacity: "
                f"{', '.join([uc.name for uc in fill_ins[:3]])}. "
                "Good for building capabilities when resources are available."
            )
        
        if avoid:
            recommendations.append(
                f"⚠️ Reconsider {len(avoid)} Low-Value Project(s): "
                f"{', '.join([uc.name for uc in avoid[:3]])}. "
                "High effort with low impact - seek ways to reduce scope or defer."
            )
        
        return recommendations
    
    def select_optimal_portfolio(self, use_cases: List[UseCase]) -> Tuple[List[UseCase], Dict]:
        """
        Select optimal portfolio based on constraints and prioritization
        Uses a greedy algorithm prioritizing priority_score
        """
        self.use_cases = use_cases
        
        # Filter by constraints
        eligible = [
            uc for uc in use_cases
            if uc.simple_roi >= self.constraints.min_roi
            and uc.risk_score <= self.constraints.max_risk
        ]
        
        # Sort by priority score (descending)
        sorted_cases = sorted(eligible, key=lambda x: x.priority_score, reverse=True)
        
        # Greedy selection within budget
        selected = []
        total_cost = 0
        
        for uc in sorted_cases:
            project_cost = uc.initial_cost + uc.annual_operating_cost
            if (len(selected) < self.constraints.max_projects and
                total_cost + project_cost <= self.constraints.max_budget):
                selected.append(uc)
                total_cost += project_cost
        
        self.selected_portfolio = selected
        
        # Generate selection summary
        summary = {
            "selected_count": len(selected),
            "total_eligible": len(eligible),
            "total_analyzed": len(use_cases),
            "total_investment": sum(uc.initial_cost for uc in selected),
            "total_annual_cost": sum(uc.annual_operating_cost for uc in selected),
            "total_annual_benefit": sum(uc.hard_benefits for uc in selected),
            "portfolio_npv": sum(uc.npv_3year for uc in selected),
            "excluded_projects": [uc.name for uc in use_cases if uc not in selected],
            "exclusion_reasons": self._get_exclusion_reasons(use_cases, eligible, selected)
        }
        
        return selected, summary
    
    def _get_exclusion_reasons(self, all_cases: List[UseCase], 
                               eligible: List[UseCase], 
                               selected: List[UseCase]) -> Dict:
        """Explain why projects were excluded"""
        reasons = {}
        
        for uc in all_cases:
            if uc in selected:
                continue
            
            if uc not in eligible:
                if uc.simple_roi < self.constraints.min_roi:
                    reasons[uc.name] = f"ROI ({uc.simple_roi}%) below minimum ({self.constraints.min_roi}%)"
                elif uc.risk_score > self.constraints.max_risk:
                    reasons[uc.name] = f"Risk score ({uc.risk_score}) exceeds maximum ({self.constraints.max_risk})"
            else:
                reasons[uc.name] = "Excluded due to budget or project count constraints"
        
        return reasons
    
    def generate_roadmap(self, use_cases: List[UseCase] = None) -> Dict:
        """
        Generate phased roadmap based on timeline assignments
        """
        cases = use_cases or self.selected_portfolio
        
        roadmap = {
            "Q1": {
                "title": "Quick Wins (0-3 months)",
                "projects": [],
                "total_investment": 0,
                "expected_benefit": 0
            },
            "1-Year": {
                "title": "Near-Term Initiatives (3-12 months)",
                "projects": [],
                "total_investment": 0,
                "expected_benefit": 0
            },
            "3-Year": {
                "title": "Strategic Initiatives (1-3 years)",
                "projects": [],
                "total_investment": 0,
                "expected_benefit": 0
            }
        }
        
        for uc in cases:
            phase = uc.timeline_phase
            if phase in roadmap:
                roadmap[phase]["projects"].append({
                    "id": uc.id,
                    "name": uc.name,
                    "description": uc.description,
                    "duration_months": uc.implementation_months,
                    "investment": uc.initial_cost,
                    "annual_benefit": uc.hard_benefits,
                    "priority_score": uc.priority_score,
                    "dependencies": uc.dependencies,
                    "milestones": self._generate_milestones(uc)
                })
                roadmap[phase]["total_investment"] += uc.initial_cost
                roadmap[phase]["expected_benefit"] += uc.hard_benefits
        
        # Sort projects within each phase by priority
        for phase in roadmap:
            roadmap[phase]["projects"].sort(key=lambda x: x["priority_score"], reverse=True)
        
        return roadmap
    
    def _generate_milestones(self, uc: UseCase) -> List[Dict]:
        """Generate suggested milestones for a project"""
        duration = uc.implementation_months
        milestones = []
        
        # Standard milestone template
        if duration >= 1:
            milestones.append({
                "name": "Project Kickoff",
                "month": 1,
                "description": "Team formation, requirements gathering"
            })
        
        if duration >= 2:
            milestones.append({
                "name": "Design Complete",
                "month": max(2, int(duration * 0.3)),
                "description": "Architecture and design finalized"
            })
        
        if duration >= 3:
            milestones.append({
                "name": "Development Complete",
                "month": max(3, int(duration * 0.7)),
                "description": "Core functionality built and tested"
            })
        
        milestones.append({
            "name": "Go Live",
            "month": duration,
            "description": "Production deployment and handover"
        })
        
        return milestones
    
    def get_matrix_visualization_data(self) -> Dict:
        """
        Get data formatted for Impact-Effort matrix visualization
        """
        return {
            "x_axis": {"label": "Effort", "min": 0, "max": 10},
            "y_axis": {"label": "Impact", "min": 0, "max": 10},
            "quadrant_labels": {
                "top_left": "Quick Wins ⭐",
                "top_right": "Strategic Projects 📊",
                "bottom_left": "Fill-Ins 📋",
                "bottom_right": "Reconsider ⚠️"
            },
            "points": [
                {
                    "x": uc.effort_score,
                    "y": uc.impact_score,
                    "label": uc.name,
                    "size": self._calculate_bubble_size(uc),
                    "color": self._get_quadrant_color(self._determine_quadrant(uc)),
                    "tooltip": f"{uc.name}\nROI: {uc.simple_roi}%\nNPV: ${uc.npv_3year:,.0f}"
                }
                for uc in self.use_cases
            ]
        }

