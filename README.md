# AI ROI and Roadmap Canvas Agent

An intelligent agent that helps organizations capture AI use cases, compute ROI metrics, build optimized portfolios, and generate comprehensive roadmaps.

## Features

- **Interactive Interview**: Conversational AI captures problem statements, KPIs, benefits, costs, effort, risk, and dependencies
- **ROI Computation**: Calculates (Benefit - Cost)/Cost, NPV (10% discount rate), payback period, and risk-adjusted value
- **Portfolio Selection**: Uses Impact–Effort matrix with constraints to prioritize initiatives
- **Roadmap Generation**: Assigns projects to Q1, 1-year, or 3-year timelines
- **Canvas Export**: Generates single-page AI ROI & Roadmap Canvas in JSON, Markdown, or HTML formats

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Start the Agent**: Launch the application and begin the interview process
2. **Input Use Cases**: Describe at least 5 AI use cases with their details
3. **Review Analysis**: See ROI calculations and portfolio recommendations
4. **Generate Roadmap**: View the optimized timeline
5. **Export Canvas**: Download your single-page canvas in your preferred format

## Canvas Sections

The generated canvas includes:
- Header (Title, Name, Designer, Target Audience, Date, Version)
- Objectives (Primary Goal, Strategic Focus)
- Inputs (Resources, Personnel, External Support)
- Impacts (Hard Benefits, Soft Benefits)
- Timeline (AI Initiatives, Start/End Dates, Milestones)
- Risks
- Capabilities (Skills Needed, Technology)
- Costs (Near-Term, Long-Term, Annual Maintenance)
- Benefits (Near-Term, Long-Term, Soft Benefits)
- Portfolio ROI (Near-Term ROI%, Long-Term ROI%, Portfolio Notes)
- Footer (Credit Line)

## Project Structure

```
├── app.py                  # Main Streamlit application
├── models/
│   └── data_models.py      # Pydantic data models
├── calculators/
│   └── roi_calculator.py   # ROI computation engine
├── optimizers/
│   └── portfolio_optimizer.py  # Impact-Effort matrix optimization
├── generators/
│   └── roadmap_generator.py    # Timeline assignment logic
├── exporters/
│   └── canvas_exporter.py      # Multi-format export
├── agents/
│   └── interview_agent.py      # OpenAI-powered conversational agent
├── templates/
│   └── canvas_template.html    # HTML template for styled export
├── requirements.txt
└── README.md
```

## ROI Formulas

1. **Basic ROI**: `(Total Benefits - Total Costs) / Total Costs × 100%`
2. **NPV (10% discount)**: `Σ(Cash Flow_t / (1 + 0.10)^t)`
3. **Payback Period**: Time to recover initial investment
4. **Risk-Adjusted Value**: `Expected Value × (1 - Risk Factor)`

## License

MIT License - Created for Academic Purposes
