"""
Canvas Exporter

Exports AI ROI & Roadmap Canvas to multiple formats:
1. JSON - Structured data export
2. Markdown - Human-readable document
3. HTML - Styled single-page canvas
"""

import json
from typing import List, Optional
from datetime import date, datetime
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
from models.data_models import (
    AIROICanvas, AIUseCase, PortfolioItem, RoadmapItem,
    CanvasHeader, CanvasObjectives, CanvasInputs, CanvasImpacts,
    CanvasTimeline, CanvasRisks, CanvasCapabilities, CanvasCosts,
    CanvasBenefits, CanvasPortfolioROI, CanvasFooter, TimeHorizon
)


class CanvasExporter:
    """
    Exports AI ROI & Roadmap Canvas to various formats.
    """
    
    def __init__(self, template_dir: str = "templates"):
        """Initialize exporter with template directory."""
        self.template_dir = Path(template_dir)
    
    def build_canvas(self,
                     use_cases: List[AIUseCase],
                     portfolio_items: List[PortfolioItem],
                     roadmap_items: List[RoadmapItem],
                     organization_name: str,
                     designed_by: str,
                     designed_for: str,
                     primary_goal: str,
                     strategic_focus: List[str]) -> AIROICanvas:
        """
        Build complete canvas from components.
        """
        selected_items = [p for p in portfolio_items if p.selected]
        
        # Calculate aggregated metrics
        near_term_cost = sum(
            r.use_case.initial_cost 
            for r in roadmap_items 
            if r.time_horizon == TimeHorizon.Q1
        )
        long_term_cost = sum(
            r.use_case.initial_cost + (r.use_case.annual_cost * 3)
            for r in roadmap_items
            if r.time_horizon in [TimeHorizon.YEAR_1, TimeHorizon.YEAR_3]
        )
        annual_maintenance = sum(
            r.use_case.annual_cost 
            for r in roadmap_items
        )
        
        near_term_benefit = sum(
            r.roi_metrics.annual_net_benefit * 0.25  # Q1 = ~3 months
            for r in roadmap_items
            if r.time_horizon == TimeHorizon.Q1
        )
        long_term_benefit = sum(
            r.roi_metrics.three_year_benefit
            for r in roadmap_items
        )
        
        # Calculate ROI percentages
        total_near_cost = near_term_cost if near_term_cost > 0 else 1
        total_long_cost = (long_term_cost + near_term_cost) if (long_term_cost + near_term_cost) > 0 else 1
        
        near_term_roi = ((near_term_benefit - near_term_cost) / total_near_cost) * 100
        long_term_roi = ((long_term_benefit - long_term_cost - near_term_cost) / total_long_cost) * 100
        
        # Aggregate inputs
        all_skills = []
        all_tech = []
        all_risks = []
        all_soft_benefits = []
        
        for uc in use_cases:
            all_skills.extend(uc.skills_required)
            all_tech.extend(uc.technology_required)
            all_risks.extend(uc.risk_factors)
            all_soft_benefits.extend(uc.soft_benefits)
        
        # Build timeline
        timeline_initiatives = []
        for r in roadmap_items:
            timeline_initiatives.append(
                CanvasTimeline.InitiativeTimeline(
                    ai_initiative=r.use_case.name,
                    start_date=r.start_date,
                    end_date=r.end_date,
                    milestones=r.milestones
                )
            )
        
        canvas = AIROICanvas(
            header=CanvasHeader(
                canvas_title="AI ROI & Roadmap Canvas",
                organization_name=organization_name,
                designed_by=designed_by,
                designed_for=designed_for,
                date=date.today(),
                version="1.0"
            ),
            objectives=CanvasObjectives(
                primary_goal=primary_goal,
                strategic_focus=strategic_focus
            ),
            inputs=CanvasInputs(
                resources=["Budget allocation", "Computing infrastructure", "Data assets"],
                personnel=list(set(all_skills))[:10],
                external_support=["AI/ML consultants", "Technology vendors", "Training providers"]
            ),
            impacts=CanvasImpacts(
                hard_benefits=[
                    f"${sum(p.roi_metrics.three_year_benefit for p in selected_items):,.0f} total 3-year benefit",
                    f"${sum(p.roi_metrics.npv for p in selected_items):,.0f} total NPV",
                    f"{sum(p.roi_metrics.basic_roi_percent for p in selected_items)/len(selected_items) if selected_items else 0:.1f}% average ROI"
                ],
                soft_benefits=list(set(all_soft_benefits))[:8]
            ),
            timeline=CanvasTimeline(initiatives=timeline_initiatives),
            risks=CanvasRisks(
                risks=list(set(all_risks))[:8],
                mitigations=[
                    "Phased implementation approach",
                    "Regular progress reviews",
                    "Change management program",
                    "Technical proof-of-concepts"
                ]
            ),
            capabilities=CanvasCapabilities(
                skills_needed=list(set(all_skills))[:10],
                technology=list(set(all_tech))[:10]
            ),
            costs=CanvasCosts(
                near_term=near_term_cost,
                long_term=long_term_cost,
                annual_maintenance=annual_maintenance
            ),
            benefits=CanvasBenefits(
                near_term=near_term_benefit,
                long_term=long_term_benefit,
                soft_benefits=list(set(all_soft_benefits))[:5]
            ),
            portfolio_roi=CanvasPortfolioROI(
                near_term_roi_percent=near_term_roi,
                long_term_roi_percent=long_term_roi,
                portfolio_note=f"Portfolio of {len(selected_items)} initiatives with risk-adjusted value of ${sum(p.roi_metrics.risk_adjusted_value for p in selected_items):,.0f}"
            ),
            footer=CanvasFooter(
                credit_line="Generated by AI ROI & Roadmap Canvas Agent"
            ),
            use_cases=use_cases,
            portfolio_items=portfolio_items,
            roadmap_items=roadmap_items
        )
        
        return canvas
    
    def export_json(self, canvas: AIROICanvas, filepath: Optional[str] = None) -> str:
        """
        Export canvas to JSON format.
        """
        def json_serializer(obj):
            if isinstance(obj, date):
                return obj.isoformat()
            if isinstance(obj, datetime):
                return obj.isoformat()
            if hasattr(obj, 'value'):  # Enum
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        json_str = json.dumps(
            canvas.model_dump(), 
            indent=2, 
            default=json_serializer
        )
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
        
        return json_str
    
    def export_markdown(self, canvas: AIROICanvas, filepath: Optional[str] = None) -> str:
        """
        Export canvas to Markdown format.
        """
        selected = [p for p in canvas.portfolio_items if p.selected]
        
        md = f"""# {canvas.header.canvas_title}

## Header Information
| Field | Value |
|-------|-------|
| Organization | {canvas.header.organization_name} |
| Designed By | {canvas.header.designed_by} |
| Designed For | {canvas.header.designed_for} |
| Date | {canvas.header.date.strftime('%B %d, %Y')} |
| Version | {canvas.header.version} |

---

## Objectives

**Primary Goal:** {canvas.objectives.primary_goal}

**Strategic Focus Areas:**
{chr(10).join(f'- {s}' for s in canvas.objectives.strategic_focus)}

---

## Inputs

### Resources
{chr(10).join(f'- {r}' for r in canvas.inputs.resources)}

### Personnel & Skills
{chr(10).join(f'- {p}' for p in canvas.inputs.personnel)}

### External Support
{chr(10).join(f'- {e}' for e in canvas.inputs.external_support)}

---

## Impacts

### Hard Benefits (Quantifiable)
{chr(10).join(f'- {h}' for h in canvas.impacts.hard_benefits)}

### Soft Benefits (Qualitative)
{chr(10).join(f'- {s}' for s in canvas.impacts.soft_benefits)}

---

## Timeline

| Initiative | Start Date | End Date | Key Milestones |
|------------|------------|----------|----------------|
"""
        for init in canvas.timeline.initiatives:
            milestones = ", ".join(init.milestones[:3]) + ("..." if len(init.milestones) > 3 else "")
            md += f"| {init.ai_initiative} | {init.start_date} | {init.end_date} | {milestones} |\n"
        
        md += f"""
---

## Risks

### Identified Risks
{chr(10).join(f'- {r}' for r in canvas.risks.risks)}

### Mitigations
{chr(10).join(f'- {m}' for m in canvas.risks.mitigations)}

---

## Capabilities Required

### Skills Needed
{chr(10).join(f'- {s}' for s in canvas.capabilities.skills_needed)}

### Technology Stack
{chr(10).join(f'- {t}' for t in canvas.capabilities.technology)}

---

## Costs

| Category | Amount |
|----------|--------|
| Near-Term (Q1) | ${canvas.costs.near_term:,.0f} |
| Long-Term (1-3 Years) | ${canvas.costs.long_term:,.0f} |
| Annual Maintenance | ${canvas.costs.annual_maintenance:,.0f}/year |

---

## Benefits

| Category | Value |
|----------|-------|
| Near-Term (Q1) | ${canvas.benefits.near_term:,.0f} |
| Long-Term (3-Year) | ${canvas.benefits.long_term:,.0f} |

### Soft Benefits
{chr(10).join(f'- {s}' for s in canvas.benefits.soft_benefits)}

---

## Portfolio ROI Summary

| Metric | Value |
|--------|-------|
| Near-Term ROI | {canvas.portfolio_roi.near_term_roi_percent:.1f}% |
| Long-Term ROI | {canvas.portfolio_roi.long_term_roi_percent:.1f}% |

**Portfolio Note:** {canvas.portfolio_roi.portfolio_note}

---

## Selected Initiatives Detail

"""
        for item in selected:
            md += f"""### {item.use_case.name}
- **Problem:** {item.use_case.problem_statement}
- **Investment:** ${item.use_case.initial_cost:,.0f} initial + ${item.use_case.annual_cost:,.0f}/year
- **Annual Benefit:** ${item.use_case.annual_benefit:,.0f}
- **ROI:** {item.roi_metrics.basic_roi_percent:.1f}%
- **NPV:** ${item.roi_metrics.npv:,.0f}
- **Payback:** {item.roi_metrics.payback_months:.1f} months
- **Priority Score:** {item.priority_score:.1f}
- **Quadrant:** {item.quadrant}

"""
        
        md += f"""---

*{canvas.footer.credit_line}*
"""
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(md)
        
        return md
    
    def export_html(self, canvas: AIROICanvas, filepath: Optional[str] = None) -> str:
        """
        Export canvas to styled HTML format.
        """
        selected = [p for p in canvas.portfolio_items if p.selected]
        
        # Group roadmap by horizon
        q1_items = [r for r in canvas.roadmap_items if r.time_horizon == TimeHorizon.Q1]
        y1_items = [r for r in canvas.roadmap_items if r.time_horizon == TimeHorizon.YEAR_1]
        y3_items = [r for r in canvas.roadmap_items if r.time_horizon == TimeHorizon.YEAR_3]
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{canvas.header.canvas_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e8e8e8;
            padding: 20px;
        }}
        
        .canvas {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            overflow: hidden;
            backdrop-filter: blur(10px);
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header-meta {{
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            margin-top: 15px;
        }}
        
        .header-meta span {{
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
        }}
        
        .content {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1px;
            background: rgba(255,255,255,0.1);
            padding: 1px;
        }}
        
        .section {{
            background: rgba(15, 23, 42, 0.8);
            padding: 20px;
        }}
        
        .section h2 {{
            color: #a78bfa;
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .section h2::before {{
            content: '';
            width: 4px;
            height: 20px;
            background: linear-gradient(to bottom, #667eea, #764ba2);
            border-radius: 2px;
        }}
        
        .section.span-2 {{
            grid-column: span 2;
        }}
        
        .section.span-4 {{
            grid-column: span 4;
        }}
        
        .section ul {{
            list-style: none;
        }}
        
        .section li {{
            padding: 6px 0;
            padding-left: 20px;
            position: relative;
            font-size: 0.9rem;
            color: #cbd5e1;
        }}
        
        .section li::before {{
            content: '→';
            position: absolute;
            left: 0;
            color: #818cf8;
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}
        
        .metric {{
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #a78bfa;
        }}
        
        .metric-label {{
            font-size: 0.75rem;
            color: #94a3b8;
            margin-top: 5px;
            text-transform: uppercase;
        }}
        
        .timeline-section {{
            background: rgba(15, 23, 42, 0.95);
        }}
        
        .timeline {{
            display: flex;
            gap: 20px;
            overflow-x: auto;
            padding-bottom: 10px;
        }}
        
        .timeline-phase {{
            flex: 1;
            min-width: 250px;
            background: rgba(139, 92, 246, 0.05);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 16px;
            padding: 20px;
        }}
        
        .timeline-phase h3 {{
            color: #c4b5fd;
            font-size: 0.9rem;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(139, 92, 246, 0.2);
        }}
        
        .initiative {{
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
        }}
        
        .initiative-name {{
            font-weight: 600;
            color: #e2e8f0;
            margin-bottom: 5px;
        }}
        
        .initiative-dates {{
            font-size: 0.8rem;
            color: #64748b;
        }}
        
        .roi-banner {{
            grid-column: span 4;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(236, 72, 153, 0.2) 100%);
            padding: 30px;
            display: flex;
            justify-content: space-around;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        
        .roi-item {{
            text-align: center;
        }}
        
        .roi-value {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .roi-label {{
            color: #94a3b8;
            font-size: 0.9rem;
            margin-top: 5px;
        }}
        
        .footer {{
            background: rgba(0,0,0,0.3);
            padding: 20px;
            text-align: center;
            color: #64748b;
            font-size: 0.85rem;
        }}
        
        @media (max-width: 1200px) {{
            .content {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .section.span-4 {{
                grid-column: span 2;
            }}
        }}
        
        @media (max-width: 768px) {{
            .content {{
                grid-template-columns: 1fr;
            }}
            .section.span-2, .section.span-4 {{
                grid-column: span 1;
            }}
        }}

        @media print {{
            body {{
                background: white;
                color: #1a1a2e;
                padding: 0;
            }}
            .canvas {{
                background: white;
                border: 1px solid #e2e8f0;
            }}
            .section {{
                background: white;
            }}
            .section h2 {{
                color: #667eea;
            }}
            .section li {{
                color: #334155;
            }}
        }}
    </style>
</head>
<body>
    <div class="canvas">
        <div class="header">
            <h1>🎯 {canvas.header.canvas_title}</h1>
            <div class="header-meta">
                <span>📍 {canvas.header.organization_name}</span>
                <span>👤 By: {canvas.header.designed_by}</span>
                <span>🎯 For: {canvas.header.designed_for}</span>
                <span>📅 {canvas.header.date.strftime('%B %d, %Y')}</span>
                <span>v{canvas.header.version}</span>
            </div>
        </div>
        
        <div class="content">
            <!-- Objectives -->
            <div class="section span-2">
                <h2>Objectives</h2>
                <p style="font-weight: 600; color: #e2e8f0; margin-bottom: 10px;">{canvas.objectives.primary_goal}</p>
                <ul>
                    {''.join(f'<li>{s}</li>' for s in canvas.objectives.strategic_focus)}
                </ul>
            </div>
            
            <!-- Inputs -->
            <div class="section span-2">
                <h2>Inputs & Resources</h2>
                <ul>
                    {''.join(f'<li>{p}</li>' for p in (canvas.inputs.personnel[:5] + canvas.inputs.resources[:3]))}
                </ul>
            </div>
            
            <!-- Costs -->
            <div class="section">
                <h2>Costs</h2>
                <div class="metric-grid">
                    <div class="metric">
                        <div class="metric-value">${canvas.costs.near_term:,.0f}</div>
                        <div class="metric-label">Near-Term</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${canvas.costs.long_term:,.0f}</div>
                        <div class="metric-label">Long-Term</div>
                    </div>
                    <div class="metric" style="grid-column: span 2;">
                        <div class="metric-value">${canvas.costs.annual_maintenance:,.0f}/yr</div>
                        <div class="metric-label">Annual Maintenance</div>
                    </div>
                </div>
            </div>
            
            <!-- Benefits -->
            <div class="section">
                <h2>Benefits</h2>
                <div class="metric-grid">
                    <div class="metric">
                        <div class="metric-value">${canvas.benefits.near_term:,.0f}</div>
                        <div class="metric-label">Near-Term</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${canvas.benefits.long_term:,.0f}</div>
                        <div class="metric-label">3-Year Total</div>
                    </div>
                </div>
                <ul style="margin-top: 15px;">
                    {''.join(f'<li>{s}</li>' for s in canvas.benefits.soft_benefits[:4])}
                </ul>
            </div>
            
            <!-- Capabilities -->
            <div class="section">
                <h2>Capabilities</h2>
                <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 10px;">Skills & Technology</p>
                <ul>
                    {''.join(f'<li>{s}</li>' for s in canvas.capabilities.skills_needed[:5])}
                </ul>
            </div>
            
            <!-- Risks -->
            <div class="section">
                <h2>Risks & Mitigations</h2>
                <ul>
                    {''.join(f'<li>{r}</li>' for r in canvas.risks.risks[:4])}
                </ul>
            </div>
            
            <!-- ROI Banner -->
            <div class="roi-banner">
                <div class="roi-item">
                    <div class="roi-value">{canvas.portfolio_roi.near_term_roi_percent:.0f}%</div>
                    <div class="roi-label">Near-Term ROI</div>
                </div>
                <div class="roi-item">
                    <div class="roi-value">{canvas.portfolio_roi.long_term_roi_percent:.0f}%</div>
                    <div class="roi-label">Long-Term ROI</div>
                </div>
                <div class="roi-item">
                    <div class="roi-value">{len(selected)}</div>
                    <div class="roi-label">Initiatives Selected</div>
                </div>
                <div class="roi-item">
                    <div class="roi-value">${sum(p.roi_metrics.npv for p in selected):,.0f}</div>
                    <div class="roi-label">Total NPV</div>
                </div>
            </div>
            
            <!-- Timeline -->
            <div class="section span-4 timeline-section">
                <h2>Roadmap Timeline</h2>
                <div class="timeline">
                    <div class="timeline-phase">
                        <h3>📅 Q1 (0-3 Months)</h3>
                        {''.join(f'''
                        <div class="initiative">
                            <div class="initiative-name">{r.use_case.name}</div>
                            <div class="initiative-dates">{r.start_date.strftime('%b %Y')} → {r.end_date.strftime('%b %Y')}</div>
                        </div>
                        ''' for r in q1_items) or '<p style="color: #64748b;">No initiatives in this phase</p>'}
                    </div>
                    <div class="timeline-phase">
                        <h3>📆 Year 1 (3-12 Months)</h3>
                        {''.join(f'''
                        <div class="initiative">
                            <div class="initiative-name">{r.use_case.name}</div>
                            <div class="initiative-dates">{r.start_date.strftime('%b %Y')} → {r.end_date.strftime('%b %Y')}</div>
                        </div>
                        ''' for r in y1_items) or '<p style="color: #64748b;">No initiatives in this phase</p>'}
                    </div>
                    <div class="timeline-phase">
                        <h3>🗓️ Years 1-3</h3>
                        {''.join(f'''
                        <div class="initiative">
                            <div class="initiative-name">{r.use_case.name}</div>
                            <div class="initiative-dates">{r.start_date.strftime('%b %Y')} → {r.end_date.strftime('%b %Y')}</div>
                        </div>
                        ''' for r in y3_items) or '<p style="color: #64748b;">No initiatives in this phase</p>'}
                    </div>
                </div>
            </div>
            
            <!-- Impacts -->
            <div class="section span-4">
                <h2>Portfolio Impact Summary</h2>
                <div style="display: flex; gap: 40px; flex-wrap: wrap;">
                    <div>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 10px;">Hard Benefits</p>
                        <ul>
                            {''.join(f'<li>{h}</li>' for h in canvas.impacts.hard_benefits)}
                        </ul>
                    </div>
                    <div>
                        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 10px;">Soft Benefits</p>
                        <ul>
                            {''.join(f'<li>{s}</li>' for s in canvas.impacts.soft_benefits[:6])}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>{canvas.footer.credit_line}</p>
            <p style="margin-top: 5px;">{canvas.portfolio_roi.portfolio_note}</p>
        </div>
    </div>
</body>
</html>"""
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
        
        return html
    
    def export_all(self, canvas: AIROICanvas, base_filename: str = "ai_roi_canvas") -> dict:
        """
        Export canvas to all formats.
        
        Returns dict with filepaths.
        """
        results = {}
        
        # JSON
        json_path = f"{base_filename}.json"
        self.export_json(canvas, json_path)
        results['json'] = json_path
        
        # Markdown
        md_path = f"{base_filename}.md"
        self.export_markdown(canvas, md_path)
        results['markdown'] = md_path
        
        # HTML
        html_path = f"{base_filename}.html"
        self.export_html(canvas, html_path)
        results['html'] = html_path
        
        return results

