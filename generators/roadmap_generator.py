"""
Roadmap Generator

Assigns projects to time horizons based on:
1. Priority score
2. Implementation complexity
3. Dependencies
4. Resource availability
"""

from typing import List, Dict, Optional
from datetime import date, timedelta
from models.data_models import (
    PortfolioItem, RoadmapItem, TimeHorizon,
    EffortLevel, ImpactLevel, AIUseCase
)


class RoadmapGenerator:
    """
    Generates time-phased roadmap for AI initiatives.
    
    Time Horizons:
    - Q1 (0-3 months): Quick wins, low effort, high priority
    - Year 1 (3-12 months): Medium complexity strategic projects
    - Year 3 (1-3 years): Major transformational initiatives
    """
    
    def __init__(self, start_date: Optional[date] = None):
        """
        Initialize roadmap generator.
        
        Args:
            start_date: Roadmap start date (defaults to today)
        """
        self.start_date = start_date or date.today()
    
    def generate_roadmap(self, 
                         portfolio_items: List[PortfolioItem],
                         selected_only: bool = True) -> List[RoadmapItem]:
        """
        Generate roadmap from portfolio items.
        
        Args:
            portfolio_items: List of portfolio items with priorities
            selected_only: Only include selected items
            
        Returns:
            List of RoadmapItems with time assignments
        """
        items = portfolio_items
        if selected_only:
            items = [i for i in portfolio_items if i.selected]
        
        # Sort by priority score
        items = sorted(items, key=lambda x: x.priority_score, reverse=True)
        
        roadmap_items = []
        phase_slots = {
            TimeHorizon.Q1: 0,
            TimeHorizon.YEAR_1: 0,
            TimeHorizon.YEAR_3: 0
        }
        
        for item in items:
            # Determine time horizon based on effort and score
            horizon = self._determine_horizon(item, phase_slots)
            
            # Calculate start and end dates
            start, end = self._calculate_dates(item, horizon, phase_slots)
            
            # Generate milestones
            milestones = self._generate_milestones(item, horizon)
            
            # Create roadmap item
            roadmap_item = RoadmapItem(
                use_case=item.use_case,
                roi_metrics=item.roi_metrics,
                time_horizon=horizon,
                start_date=start,
                end_date=end,
                milestones=milestones,
                phase_rationale=self._get_phase_rationale(item, horizon)
            )
            
            roadmap_items.append(roadmap_item)
            phase_slots[horizon] += 1
        
        return roadmap_items
    
    def _determine_horizon(self, 
                           item: PortfolioItem, 
                           slots: Dict[TimeHorizon, int]) -> TimeHorizon:
        """
        Determine appropriate time horizon for a project.
        
        Logic:
        - Quick wins (High impact, Low effort) → Q1
        - High effort projects → Year 3
        - Everything else → Year 1
        - Also considers implementation time and score
        """
        uc = item.use_case
        
        # Check implementation duration
        impl_months = uc.implementation_months
        
        # Quick wins: Low effort, high score, short implementation
        if (uc.effort_level == EffortLevel.LOW and 
            impl_months <= 3 and 
            item.priority_score >= 50):
            return TimeHorizon.Q1
        
        # Major projects: High effort or long implementation
        if (uc.effort_level == EffortLevel.HIGH or 
            impl_months > 12):
            return TimeHorizon.YEAR_3
        
        # Medium effort with good score → Year 1
        if uc.effort_level == EffortLevel.MEDIUM:
            if item.priority_score >= 40:
                return TimeHorizon.YEAR_1
            else:
                return TimeHorizon.YEAR_3
        
        # Low effort but not quick wins → Year 1
        if uc.effort_level == EffortLevel.LOW:
            return TimeHorizon.YEAR_1
        
        # Default to Year 1
        return TimeHorizon.YEAR_1
    
    def _calculate_dates(self, 
                         item: PortfolioItem, 
                         horizon: TimeHorizon,
                         slots: Dict[TimeHorizon, int]) -> tuple:
        """
        Calculate start and end dates for a project.
        """
        impl_months = item.use_case.implementation_months
        slot_num = slots[horizon]
        
        if horizon == TimeHorizon.Q1:
            # Q1: Start immediately or stagger by slot
            start_offset = slot_num * 30  # Stagger by ~1 month
            start = self.start_date + timedelta(days=start_offset)
            end = start + timedelta(days=impl_months * 30)
            
        elif horizon == TimeHorizon.YEAR_1:
            # Year 1: Start after Q1 (3 months)
            start_offset = 90 + (slot_num * 45)  # Stagger by ~1.5 months
            start = self.start_date + timedelta(days=start_offset)
            end = start + timedelta(days=impl_months * 30)
            
        else:  # YEAR_3
            # Year 3: Start after Year 1 (12 months)
            start_offset = 365 + (slot_num * 90)  # Stagger by ~3 months
            start = self.start_date + timedelta(days=start_offset)
            end = start + timedelta(days=impl_months * 30)
        
        return start, end
    
    def _generate_milestones(self, 
                             item: PortfolioItem, 
                             horizon: TimeHorizon) -> List[str]:
        """
        Generate milestone list for a project.
        """
        uc = item.use_case
        impl_months = uc.implementation_months
        
        milestones = ["Project Kickoff"]
        
        if impl_months >= 2:
            milestones.append("Requirements Complete")
        
        if impl_months >= 3:
            milestones.append("Design & Architecture Complete")
        
        if impl_months >= 4:
            milestones.append("Development Phase Complete")
        
        if impl_months >= 6:
            milestones.append("Integration Testing Complete")
        
        milestones.append("UAT & Validation")
        milestones.append("Production Deployment")
        milestones.append("Benefits Realization Review")
        
        return milestones
    
    def _get_phase_rationale(self, 
                             item: PortfolioItem, 
                             horizon: TimeHorizon) -> str:
        """
        Generate rationale for phase assignment.
        """
        uc = item.use_case
        
        if horizon == TimeHorizon.Q1:
            return (f"Quick Win - {uc.effort_level.value} effort with "
                   f"{uc.impact_level.value} impact, {uc.implementation_months} month implementation")
        
        elif horizon == TimeHorizon.YEAR_1:
            return (f"Strategic Initiative - {uc.effort_level.value} effort, "
                   f"score {item.priority_score:.1f}, targeting Year 1 value delivery")
        
        else:
            return (f"Transformational Project - {uc.effort_level.value} effort, "
                   f"{uc.implementation_months} month timeline, long-term strategic value")
    
    def get_roadmap_by_horizon(self, 
                                items: List[RoadmapItem]) -> Dict[TimeHorizon, List[RoadmapItem]]:
        """
        Group roadmap items by time horizon.
        """
        grouped = {
            TimeHorizon.Q1: [],
            TimeHorizon.YEAR_1: [],
            TimeHorizon.YEAR_3: []
        }
        
        for item in items:
            grouped[item.time_horizon].append(item)
        
        return grouped
    
    def get_roadmap_summary(self, items: List[RoadmapItem]) -> Dict:
        """
        Generate roadmap summary statistics.
        """
        grouped = self.get_roadmap_by_horizon(items)
        
        summary = {}
        for horizon, horizon_items in grouped.items():
            if horizon_items:
                summary[horizon.value] = {
                    "count": len(horizon_items),
                    "total_investment": sum(
                        i.use_case.initial_cost + (i.use_case.annual_cost * 3) 
                        for i in horizon_items
                    ),
                    "total_npv": sum(i.roi_metrics.npv for i in horizon_items),
                    "projects": [i.use_case.name for i in horizon_items]
                }
            else:
                summary[horizon.value] = {
                    "count": 0,
                    "total_investment": 0,
                    "total_npv": 0,
                    "projects": []
                }
        
        return summary
    
    def generate_gantt_text(self, items: List[RoadmapItem]) -> str:
        """
        Generate a text-based Gantt chart visualization.
        """
        if not items:
            return "No roadmap items to display."
        
        # Find date range
        min_date = min(i.start_date for i in items)
        max_date = max(i.end_date for i in items)
        
        # Calculate total months
        total_months = ((max_date - min_date).days // 30) + 1
        total_months = max(total_months, 36)  # At least 3 years
        
        # Header with quarters
        quarters = []
        for i in range(0, total_months, 3):
            quarter_num = (i // 3) % 4 + 1
            year_offset = i // 12
            quarters.append(f"Q{quarter_num}Y{year_offset + 1}")
        
        lines = [
            "=" * 80,
            "AI ROADMAP TIMELINE",
            "=" * 80,
            "",
            "Quarter:  " + "  ".join(f"{q:^6}" for q in quarters[:12]),
            "-" * 80
        ]
        
        # Group by horizon
        grouped = self.get_roadmap_by_horizon(items)
        
        horizon_labels = {
            TimeHorizon.Q1: "📅 Q1 INITIATIVES (0-3 months)",
            TimeHorizon.YEAR_1: "📆 YEAR 1 INITIATIVES (3-12 months)",
            TimeHorizon.YEAR_3: "🗓️ YEAR 3 INITIATIVES (1-3 years)"
        }
        
        for horizon in [TimeHorizon.Q1, TimeHorizon.YEAR_1, TimeHorizon.YEAR_3]:
            horizon_items = grouped[horizon]
            if horizon_items:
                lines.append("")
                lines.append(horizon_labels[horizon])
                lines.append("-" * 40)
                
                for item in horizon_items:
                    # Calculate bar position
                    start_month = (item.start_date - min_date).days // 30
                    duration_months = max(1, (item.end_date - item.start_date).days // 30)
                    
                    # Create bar
                    bar = " " * start_month + "█" * duration_months
                    bar = bar[:36]  # Limit to 3 years
                    
                    name = item.use_case.name[:25].ljust(25)
                    lines.append(f"  {name} |{bar}|")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("█ = Active development period")
        
        return "\n".join(lines)
    
    def get_dependencies_order(self, items: List[RoadmapItem]) -> List[RoadmapItem]:
        """
        Reorder roadmap items considering dependencies.
        """
        # Build dependency graph
        name_to_item = {i.use_case.name: i for i in items}
        
        # Simple topological sort considering dependencies
        ordered = []
        processed = set()
        
        def process(item):
            if item.use_case.name in processed:
                return
            
            # Process dependencies first
            for dep_name in item.use_case.dependencies:
                if dep_name in name_to_item and dep_name not in processed:
                    process(name_to_item[dep_name])
            
            processed.add(item.use_case.name)
            ordered.append(item)
        
        for item in items:
            process(item)
        
        return ordered

