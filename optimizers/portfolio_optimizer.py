"""
Portfolio Optimizer using Impact-Effort Matrix

Implements:
1. Impact-Effort quadrant classification
2. Priority scoring algorithm
3. Constraint-based portfolio selection
"""

from typing import List, Dict, Optional, Tuple
from models.data_models import (
    AIUseCase, ROIMetrics, PortfolioItem,
    EffortLevel, ImpactLevel, RiskLevel
)


class PortfolioOptimizer:
    """
    Optimizes AI use case portfolio using Impact-Effort matrix.
    
    Quadrants:
    - Quick Wins: High Impact, Low Effort → Priority 1
    - Major Projects: High Impact, High Effort → Priority 2
    - Fill-ins: Low Impact, Low Effort → Priority 3
    - Thankless Tasks: Low Impact, High Effort → Priority 4
    """
    
    # Quadrant definitions
    QUADRANTS = {
        (ImpactLevel.HIGH, EffortLevel.LOW): ("Quick Wins", 1, "🚀"),
        (ImpactLevel.HIGH, EffortLevel.MEDIUM): ("Strategic Projects", 2, "⭐"),
        (ImpactLevel.HIGH, EffortLevel.HIGH): ("Major Projects", 3, "🏗️"),
        (ImpactLevel.MEDIUM, EffortLevel.LOW): ("Easy Wins", 2, "✅"),
        (ImpactLevel.MEDIUM, EffortLevel.MEDIUM): ("Balanced Projects", 3, "⚖️"),
        (ImpactLevel.MEDIUM, EffortLevel.HIGH): ("Resource Heavy", 4, "⚠️"),
        (ImpactLevel.LOW, EffortLevel.LOW): ("Fill-ins", 3, "📝"),
        (ImpactLevel.LOW, EffortLevel.MEDIUM): ("Low Priority", 4, "📉"),
        (ImpactLevel.LOW, EffortLevel.HIGH): ("Avoid", 5, "🚫"),
    }
    
    # Scoring weights
    WEIGHTS = {
        "roi": 0.30,           # ROI percentage weight
        "npv": 0.25,           # NPV weight
        "risk_adjusted": 0.20, # Risk-adjusted value weight
        "payback": 0.15,       # Payback period weight
        "strategic": 0.10     # Strategic alignment weight
    }
    
    def __init__(self, 
                 budget_constraint: Optional[float] = None,
                 max_projects: Optional[int] = None,
                 min_roi_threshold: float = 0):
        """
        Initialize optimizer with constraints.
        
        Args:
            budget_constraint: Maximum total budget for selected projects
            max_projects: Maximum number of projects to select
            min_roi_threshold: Minimum ROI percentage to consider
        """
        self.budget_constraint = budget_constraint
        self.max_projects = max_projects
        self.min_roi_threshold = min_roi_threshold
    
    def optimize(self, 
                 use_cases: List[AIUseCase], 
                 metrics: List[ROIMetrics]) -> List[PortfolioItem]:
        """
        Optimize portfolio and return prioritized items.
        
        Args:
            use_cases: List of AI use cases
            metrics: Corresponding ROI metrics
            
        Returns:
            List of PortfolioItems with scores and selection status
        """
        # Create metrics lookup
        metrics_map = {m.use_case_id: m for m in metrics}
        
        # Build portfolio items with scores
        portfolio_items = []
        for uc in use_cases:
            roi_metrics = metrics_map.get(uc.id)
            if not roi_metrics:
                continue
            
            # Calculate priority score
            score = self._calculate_priority_score(uc, roi_metrics)
            
            # Determine quadrant
            quadrant_info = self._get_quadrant(uc.impact_level, uc.effort_level)
            
            portfolio_items.append(PortfolioItem(
                use_case=uc,
                roi_metrics=roi_metrics,
                priority_score=score,
                quadrant=quadrant_info[0],
                selected=False,
                selection_rationale=""
            ))
        
        # Sort by priority score (descending)
        portfolio_items.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Apply selection with constraints
        portfolio_items = self._apply_selection(portfolio_items)
        
        return portfolio_items
    
    def _calculate_priority_score(self, 
                                   use_case: AIUseCase, 
                                   metrics: ROIMetrics) -> float:
        """
        Calculate composite priority score (0-100 scale).
        """
        scores = {}
        
        # ROI Score (normalized, cap at 500% for scoring)
        roi_normalized = min(metrics.basic_roi_percent, 500) / 500
        scores["roi"] = roi_normalized * 100
        
        # NPV Score (positive NPV is good, normalized)
        # Assume max NPV of $5M for normalization
        npv_normalized = min(max(metrics.npv, 0), 5_000_000) / 5_000_000
        scores["npv"] = npv_normalized * 100
        
        # Risk-Adjusted Score
        risk_adj_normalized = min(max(metrics.risk_adjusted_value, 0), 5_000_000) / 5_000_000
        scores["risk_adjusted"] = risk_adj_normalized * 100
        
        # Payback Score (shorter is better, max 36 months)
        if metrics.payback_months == float('inf'):
            scores["payback"] = 0
        else:
            payback_score = max(0, (36 - metrics.payback_months) / 36)
            scores["payback"] = payback_score * 100
        
        # Strategic Score based on impact/effort quadrant
        quadrant_info = self._get_quadrant(use_case.impact_level, use_case.effort_level)
        quadrant_priority = quadrant_info[1]
        scores["strategic"] = (6 - quadrant_priority) / 5 * 100  # Convert 1-5 to 100-20
        
        # Weighted composite score
        total_score = sum(
            scores[key] * self.WEIGHTS[key] 
            for key in self.WEIGHTS
        )
        
        return round(total_score, 2)
    
    def _get_quadrant(self, 
                      impact: ImpactLevel, 
                      effort: EffortLevel) -> Tuple[str, int, str]:
        """Get quadrant name, priority rank, and emoji."""
        return self.QUADRANTS.get(
            (impact, effort), 
            ("Unknown", 3, "❓")
        )
    
    def _apply_selection(self, items: List[PortfolioItem]) -> List[PortfolioItem]:
        """
        Apply constraints to select portfolio items.
        """
        selected_count = 0
        total_cost = 0.0
        
        for item in items:
            # Check ROI threshold
            if item.roi_metrics.basic_roi_percent < self.min_roi_threshold:
                item.selection_rationale = f"ROI ({item.roi_metrics.basic_roi_percent:.1f}%) below threshold ({self.min_roi_threshold}%)"
                continue
            
            # Check budget constraint
            project_cost = item.use_case.initial_cost + (item.use_case.annual_cost * 3)
            if self.budget_constraint and (total_cost + project_cost > self.budget_constraint):
                item.selection_rationale = f"Exceeds budget constraint (${self.budget_constraint:,.0f})"
                continue
            
            # Check project count constraint
            if self.max_projects and selected_count >= self.max_projects:
                item.selection_rationale = f"Exceeds max project limit ({self.max_projects})"
                continue
            
            # Select this project
            item.selected = True
            item.selection_rationale = f"Selected - Rank #{selected_count + 1}, Score: {item.priority_score:.1f}"
            selected_count += 1
            total_cost += project_cost
        
        return items
    
    def get_quadrant_summary(self, items: List[PortfolioItem]) -> Dict[str, List[PortfolioItem]]:
        """
        Group portfolio items by quadrant.
        """
        summary = {}
        for item in items:
            if item.quadrant not in summary:
                summary[item.quadrant] = []
            summary[item.quadrant].append(item)
        return summary
    
    def get_selection_summary(self, items: List[PortfolioItem]) -> Dict:
        """
        Generate summary statistics for selected portfolio.
        """
        selected = [i for i in items if i.selected]
        
        if not selected:
            return {
                "count": 0,
                "total_investment": 0,
                "total_npv": 0,
                "average_roi": 0,
                "items": []
            }
        
        return {
            "count": len(selected),
            "total_investment": sum(
                i.use_case.initial_cost + (i.use_case.annual_cost * 3) 
                for i in selected
            ),
            "total_npv": sum(i.roi_metrics.npv for i in selected),
            "average_roi": sum(i.roi_metrics.basic_roi_percent for i in selected) / len(selected),
            "total_risk_adjusted_value": sum(i.roi_metrics.risk_adjusted_value for i in selected),
            "items": [
                {
                    "name": i.use_case.name,
                    "quadrant": i.quadrant,
                    "score": i.priority_score,
                    "roi": i.roi_metrics.basic_roi_percent,
                    "npv": i.roi_metrics.npv
                }
                for i in selected
            ]
        }
    
    def generate_impact_effort_matrix(self, items: List[PortfolioItem]) -> str:
        """
        Generate a text-based Impact-Effort matrix visualization.
        """
        # Map items to grid positions
        effort_map = {EffortLevel.LOW: 0, EffortLevel.MEDIUM: 1, EffortLevel.HIGH: 2}
        impact_map = {ImpactLevel.HIGH: 0, ImpactLevel.MEDIUM: 1, ImpactLevel.LOW: 2}
        
        grid = [[[] for _ in range(3)] for _ in range(3)]
        
        for item in items:
            effort_idx = effort_map.get(item.use_case.effort_level, 1)
            impact_idx = impact_map.get(item.use_case.impact_level, 1)
            marker = "●" if item.selected else "○"
            grid[impact_idx][effort_idx].append(f"{marker} {item.use_case.name[:15]}")
        
        # Build matrix display
        lines = [
            "┌─────────────────────────────────────────────────────────────────┐",
            "│                    IMPACT-EFFORT MATRIX                         │",
            "├─────────────────┬─────────────────┬─────────────────┬───────────┤",
            "│                 │    LOW EFFORT   │  MEDIUM EFFORT  │HIGH EFFORT│",
            "├─────────────────┼─────────────────┼─────────────────┼───────────┤",
        ]
        
        labels = ["HIGH IMPACT  ", "MEDIUM IMPACT", "LOW IMPACT   "]
        quadrant_names = [
            ["🚀 Quick Wins", "⭐ Strategic", "🏗️ Major"],
            ["✅ Easy Wins", "⚖️ Balanced", "⚠️ Resource"],
            ["📝 Fill-ins", "📉 Low Priority", "🚫 Avoid"]
        ]
        
        for i, (label, row, names) in enumerate(zip(labels, grid, quadrant_names)):
            # Quadrant name row
            lines.append(f"│ {label} │ {names[0]:^15} │ {names[1]:^15} │{names[2]:^11}│")
            
            # Items in each cell
            max_items = max(len(cell) for cell in row) or 1
            for j in range(max_items):
                cells = []
                for cell in row:
                    if j < len(cell):
                        cells.append(f"{cell[j]:^15}"[:15])
                    else:
                        cells.append(" " * 15)
                lines.append(f"│               │ {cells[0]} │ {cells[1]} │{cells[2][:11]:^11}│")
            
            if i < 2:
                lines.append("├─────────────────┼─────────────────┼─────────────────┼───────────┤")
        
        lines.append("└─────────────────┴─────────────────┴─────────────────┴───────────┘")
        lines.append("● = Selected  ○ = Not Selected")
        
        return "\n".join(lines)

