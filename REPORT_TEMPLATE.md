# AI ROI & Roadmap Canvas Agent - Design Report

## 1. Executive Summary

This report documents the design, implementation, and functionality of the AI ROI & Roadmap Canvas Agent - an intelligent system that helps organizations capture, analyze, and prioritize AI initiatives.

## 2. System Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Web Interface                       │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────┐ │
│   │Interview│  │ Manual  │  │Analysis │  │Roadmap  │  │Export│ │
│   │   Tab   │  │  Input  │  │   Tab   │  │  Tab    │  │ Tab  │ │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └──┬───┘ │
└────────┼────────────┼───────────┼───────────┼───────────┼──────┘
         │            │           │           │           │
    ┌────▼────┐  ┌────▼────┐  ┌───▼────┐  ┌──▼───┐  ┌───▼────┐
    │Interview│  │  Data   │  │  ROI   │  │Roadmap│ │ Canvas │
    │  Agent  │  │ Models  │  │Calculat│  │Generat│ │Exporter│
    │(OpenAI) │  │(Pydantic│  │  or    │  │  or   │ │        │
    └─────────┘  └─────────┘  └────────┘  └───────┘ └────────┘
                                   │
                             ┌─────▼─────┐
                             │ Portfolio │
                             │ Optimizer │
                             └───────────┘
```

### 2.2 Key Modules

| Module | Purpose | Key Files |
|--------|---------|-----------|
| **Models** | Data structures using Pydantic | `models/data_models.py` |
| **Calculators** | ROI computation engine | `calculators/roi_calculator.py` |
| **Optimizers** | Impact-Effort portfolio selection | `optimizers/portfolio_optimizer.py` |
| **Generators** | Roadmap timeline assignment | `generators/roadmap_generator.py` |
| **Exporters** | Multi-format canvas export | `exporters/canvas_exporter.py` |
| **Agents** | OpenAI-powered interview | `agents/interview_agent.py` |

## 3. ROI Calculation Methodology

### 3.1 Basic ROI Formula

```
ROI% = ((Total Benefits - Total Costs) / Total Costs) × 100
```

Where:
- Total Benefits = Sum of annual benefits over 3-year period (adjusted for implementation delay)
- Total Costs = Initial cost + (Annual operating cost × 3 years)

### 3.2 Net Present Value (NPV)

```
NPV = Σ(CFₜ / (1 + r)ᵗ)
```

Where:
- CFₜ = Cash flow at time t (monthly)
- r = Monthly discount rate (derived from 10% annual rate)
- t = Time period (months 0-35)

**Implementation:**
```python
monthly_rate = (1 + 0.10) ** (1/12) - 1  # ~0.797% monthly
npv = sum(cf / ((1 + monthly_rate) ** t) for t, cf in enumerate(cash_flows))
```

### 3.3 Payback Period

```
Payback = Implementation Time + (Initial Investment / Monthly Net Benefit)
```

Where:
- Monthly Net Benefit = (Annual Benefit - Annual Cost) / 12

### 3.4 Risk-Adjusted Value

```
Risk-Adjusted Value = NPV × Risk Multiplier
```

| Risk Level | Multiplier |
|------------|------------|
| Low | 0.95 (5% discount) |
| Medium | 0.80 (20% discount) |
| High | 0.60 (40% discount) |

## 4. Portfolio Selection Logic

### 4.1 Impact-Effort Matrix

| | Low Effort | Medium Effort | High Effort |
|---|---|---|---|
| **High Impact** | 🚀 Quick Wins (P1) | ⭐ Strategic (P2) | 🏗️ Major (P3) |
| **Medium Impact** | ✅ Easy Wins (P2) | ⚖️ Balanced (P3) | ⚠️ Resource Heavy (P4) |
| **Low Impact** | 📝 Fill-ins (P3) | 📉 Low Priority (P4) | 🚫 Avoid (P5) |

### 4.2 Priority Scoring Algorithm

```python
Score = (0.30 × ROI_Score) + (0.25 × NPV_Score) + 
        (0.20 × Risk_Adj_Score) + (0.15 × Payback_Score) + 
        (0.10 × Strategic_Score)
```

### 4.3 Constraint Application

1. Filter by minimum ROI threshold
2. Sort by priority score (descending)
3. Select projects until budget limit reached
4. Respect maximum project count

## 5. Roadmap Generation Logic

### 5.1 Time Horizon Assignment

| Criteria | Assignment |
|----------|------------|
| Low effort + High score + ≤3 months implementation | **Q1** |
| High effort OR >12 months implementation | **Year 3** |
| Medium effort with score ≥40 | **Year 1** |
| Default | **Year 1** |

### 5.2 Date Calculation

- **Q1**: Start immediately, stagger by ~1 month per project
- **Year 1**: Start after Q1 (month 4+), stagger by ~1.5 months
- **Year 3**: Start after Year 1 (month 13+), stagger by ~3 months

## 6. Canvas Export Specifications

### 6.1 Required Sections

| Section | Contents |
|---------|----------|
| Header | Title, Organization, Designer, Date, Version |
| Objectives | Primary Goal, Strategic Focus Areas |
| Inputs | Resources, Personnel, External Support |
| Impacts | Hard Benefits, Soft Benefits |
| Timeline | Initiatives with Start/End Dates, Milestones |
| Risks | Risk Factors, Mitigations |
| Capabilities | Skills Needed, Technology Stack |
| Costs | Near-Term, Long-Term, Annual Maintenance |
| Benefits | Near-Term, Long-Term, Soft Benefits |
| Portfolio ROI | Near-Term ROI%, Long-Term ROI%, Notes |
| Footer | Credit Line |

### 6.2 Export Formats

1. **JSON** - Structured data for programmatic use
2. **Markdown** - Human-readable documentation
3. **HTML** - Styled single-page canvas for presentation

## 7. Grounding Documents & References

- Value-Effort Prioritization Frameworks
- NPV and ROI calculation standards
- Project portfolio management best practices
- AI strategy canvas methodologies

## 8. Usage Instructions

### 8.1 Installation

```bash
pip install -r requirements.txt
```

### 8.2 Configuration

Set OpenAI API key (optional - runs in demo mode without):
```bash
set OPENAI_API_KEY=your-key-here  # Windows
export OPENAI_API_KEY=your-key-here  # Linux/Mac
```

### 8.3 Running the Application

```bash
streamlit run app.py
```

### 8.4 Workflow

1. **Interview Tab**: Chat with AI or use "Load Sample Data" for demo
2. **Manual Input Tab**: Add/edit use cases manually
3. **Analysis Tab**: View ROI metrics and portfolio optimization
4. **Roadmap Tab**: See timeline visualization
5. **Export Tab**: Download canvas in JSON/Markdown/HTML

## 9. Sample Output Screenshots

[Include screenshots from your demo video here]

## 10. Conclusion

The AI ROI & Roadmap Canvas Agent provides a comprehensive solution for AI strategy planning, combining conversational AI for data capture with rigorous financial analysis and visual roadmap generation.

---

*Report prepared for: Fundamentals of Operationalizing AI - Extra Credit Assignment*

