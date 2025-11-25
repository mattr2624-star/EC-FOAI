"""
AI ROI & Roadmap Canvas Agent

Main Streamlit Application

This application helps organizations:
1. Capture AI use cases through conversational interview
2. Compute ROI metrics (Basic ROI, NPV, Payback, Risk-Adjusted)
3. Optimize portfolio using Impact-Effort matrix
4. Generate phased roadmap (Q1, Year 1, Year 3)
5. Export single-page AI ROI Canvas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from models.data_models import (
    AIUseCase, EffortLevel, ImpactLevel, RiskLevel, TimeHorizon
)
from calculators.roi_calculator import ROICalculator
from optimizers.portfolio_optimizer import PortfolioOptimizer
from generators.roadmap_generator import RoadmapGenerator
from exporters.canvas_exporter import CanvasExporter
from agents.interview_agent import InterviewAgent, MockInterviewAgent

# Page configuration
st.set_page_config(
    page_title="AI ROI & Roadmap Canvas Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
    
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    
    .user-message {
        background-color: #e8f4fd;
        margin-left: 20%;
    }
    
    .assistant-message {
        background-color: #f0f2f6;
        margin-right: 20%;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'use_cases' not in st.session_state:
        st.session_state.use_cases = []
    if 'roi_metrics' not in st.session_state:
        st.session_state.roi_metrics = []
    if 'portfolio_items' not in st.session_state:
        st.session_state.portfolio_items = []
    if 'roadmap_items' not in st.session_state:
        st.session_state.roadmap_items = []
    if 'canvas' not in st.session_state:
        st.session_state.canvas = None
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'agent' not in st.session_state:
        # Use mock agent if no API key
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            st.session_state.agent = InterviewAgent(api_key)
        else:
            st.session_state.agent = MockInterviewAgent()
    if 'canvas_config' not in st.session_state:
        st.session_state.canvas_config = {
            'organization_name': '',
            'designed_by': '',
            'designed_for': '',
            'primary_goal': '',
            'strategic_focus': []
        }


def render_sidebar():
    """Render the sidebar with configuration options."""
    st.sidebar.markdown("## 🎯 AI ROI Canvas Agent")
    st.sidebar.markdown("---")
    
    # Canvas Configuration
    st.sidebar.markdown("### 📝 Canvas Configuration")
    
    st.session_state.canvas_config['organization_name'] = st.sidebar.text_input(
        "Organization Name",
        value=st.session_state.canvas_config.get('organization_name', ''),
        placeholder="Acme Corporation"
    )
    
    st.session_state.canvas_config['designed_by'] = st.sidebar.text_input(
        "Designed By",
        value=st.session_state.canvas_config.get('designed_by', ''),
        placeholder="AI Strategy Team"
    )
    
    st.session_state.canvas_config['designed_for'] = st.sidebar.text_input(
        "Designed For",
        value=st.session_state.canvas_config.get('designed_for', ''),
        placeholder="Executive Leadership"
    )
    
    st.session_state.canvas_config['primary_goal'] = st.sidebar.text_area(
        "Primary Goal",
        value=st.session_state.canvas_config.get('primary_goal', ''),
        placeholder="Transform business operations through strategic AI adoption",
        height=80
    )
    
    st.sidebar.markdown("---")
    
    # Portfolio Constraints
    st.sidebar.markdown("### 🎚️ Portfolio Constraints")
    
    budget = st.sidebar.number_input(
        "Budget Limit ($)",
        min_value=0,
        value=1000000,
        step=50000,
        format="%d"
    )
    
    max_projects = st.sidebar.slider(
        "Max Projects",
        min_value=1,
        max_value=10,
        value=5
    )
    
    min_roi = st.sidebar.slider(
        "Min ROI Threshold (%)",
        min_value=0,
        max_value=100,
        value=20
    )
    
    st.sidebar.markdown("---")
    
    # Status
    st.sidebar.markdown("### 📊 Status")
    st.sidebar.metric("Use Cases Captured", len(st.session_state.use_cases))
    
    if st.sidebar.button("🗑️ Reset All", use_container_width=True):
        st.session_state.use_cases = []
        st.session_state.roi_metrics = []
        st.session_state.portfolio_items = []
        st.session_state.roadmap_items = []
        st.session_state.canvas = None
        st.session_state.chat_messages = []
        st.session_state.agent.reset_all()
        st.rerun()
    
    return budget, max_projects, min_roi


def render_chat_tab():
    """Render the conversational interview tab."""
    st.markdown("### 💬 AI Interview Assistant")
    st.markdown("Chat with the AI to capture your AI use cases, or add them manually below.")
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        if not st.session_state.chat_messages:
            # Show welcome message
            welcome = st.session_state.agent.get_welcome_message()
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": welcome
            })
        
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.chat_message("user").markdown(msg["content"])
            else:
                st.chat_message("assistant").markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Get agent response
        response = st.session_state.agent.chat(prompt)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        # Sync captured use cases
        st.session_state.use_cases = st.session_state.agent.get_captured_use_cases()
        
        st.rerun()
    
    # Quick actions
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Load Sample Data", use_container_width=True):
            # Trigger sample load through agent
            response = st.session_state.agent.chat("add sample use cases for demo")
            st.session_state.chat_messages.append({"role": "user", "content": "Add sample use cases"})
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.session_state.use_cases = st.session_state.agent.get_captured_use_cases()
            st.rerun()
    
    with col2:
        if st.button("📋 Extract from Chat", use_container_width=True):
            if hasattr(st.session_state.agent, 'extract_use_case_from_conversation'):
                use_case = st.session_state.agent.extract_use_case_from_conversation()
                if use_case:
                    st.session_state.use_cases.append(use_case)
                    st.success(f"Extracted: {use_case.name}")
                else:
                    st.warning("Could not extract use case from conversation")
    
    with col3:
        st.metric("Use Cases Captured", len(st.session_state.use_cases))


def render_manual_input_tab():
    """Render manual use case input form."""
    st.markdown("### ➕ Add Use Case Manually")
    
    with st.form("use_case_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Initiative Name*", placeholder="Customer Churn Prediction")
            problem = st.text_area("Problem Statement*", placeholder="Describe the business problem...")
            kpis = st.text_input("KPIs (comma-separated)", placeholder="Accuracy, Cost savings, Time reduction")
            
            st.markdown("#### 💰 Financial Estimates")
            initial_cost = st.number_input("Initial Cost ($)*", min_value=0, value=100000, step=10000)
            annual_cost = st.number_input("Annual Operating Cost ($)*", min_value=0, value=20000, step=5000)
            annual_benefit = st.number_input("Annual Benefit ($)*", min_value=0, value=150000, step=10000)
        
        with col2:
            impl_months = st.slider("Implementation Months*", 1, 24, 6)
            
            st.markdown("#### 📊 Assessment")
            effort = st.selectbox("Effort Level*", ["Low", "Medium", "High"])
            impact = st.selectbox("Impact Level*", ["Low", "Medium", "High"])
            risk = st.selectbox("Risk Level*", ["Low", "Medium", "High"])
            
            st.markdown("#### 🔗 Requirements")
            skills = st.text_input("Skills Required (comma-separated)", placeholder="Data Science, Python")
            tech = st.text_input("Technology Required (comma-separated)", placeholder="AWS, Python, SQL")
            dependencies = st.text_input("Dependencies (comma-separated)", placeholder="Data Pipeline Project")
            
            soft_benefits = st.text_input("Soft Benefits (comma-separated)", placeholder="Employee satisfaction")
            risk_factors = st.text_input("Risk Factors (comma-separated)", placeholder="Data quality concerns")
        
        submitted = st.form_submit_button("➕ Add Use Case", use_container_width=True)
        
        if submitted and name and problem:
            # Create use case
            effort_map = {"Low": EffortLevel.LOW, "Medium": EffortLevel.MEDIUM, "High": EffortLevel.HIGH}
            impact_map = {"Low": ImpactLevel.LOW, "Medium": ImpactLevel.MEDIUM, "High": ImpactLevel.HIGH}
            risk_map = {"Low": RiskLevel.LOW, "Medium": RiskLevel.MEDIUM, "High": RiskLevel.HIGH}
            
            use_case = AIUseCase(
                id=f"UC{len(st.session_state.use_cases) + 1:03d}",
                name=name,
                problem_statement=problem,
                kpis=[k.strip() for k in kpis.split(",") if k.strip()],
                initial_cost=initial_cost,
                annual_cost=annual_cost,
                annual_benefit=annual_benefit,
                implementation_months=impl_months,
                benefit_start_month=1,
                effort_level=effort_map[effort],
                impact_level=impact_map[impact],
                risk_level=risk_map[risk],
                dependencies=[d.strip() for d in dependencies.split(",") if d.strip()],
                skills_required=[s.strip() for s in skills.split(",") if s.strip()],
                technology_required=[t.strip() for t in tech.split(",") if t.strip()],
                soft_benefits=[b.strip() for b in soft_benefits.split(",") if b.strip()],
                risk_factors=[r.strip() for r in risk_factors.split(",") if r.strip()]
            )
            
            st.session_state.use_cases.append(use_case)
            st.session_state.agent.add_use_case_manually(use_case)
            st.success(f"Added: {name}")
            st.rerun()
    
    # Display current use cases
    if st.session_state.use_cases:
        st.markdown("---")
        st.markdown("### 📋 Current Use Cases")
        
        for i, uc in enumerate(st.session_state.use_cases):
            with st.expander(f"**{uc.name}** | ${uc.initial_cost:,.0f} | {uc.effort_level.value} Effort | {uc.impact_level.value} Impact"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Problem:** {uc.problem_statement[:200]}...")
                with col2:
                    st.markdown(f"**Annual Benefit:** ${uc.annual_benefit:,.0f}")
                    st.markdown(f"**Timeline:** {uc.implementation_months} months")
                with col3:
                    st.markdown(f"**Risk:** {uc.risk_level.value}")
                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        st.session_state.use_cases.pop(i)
                        st.rerun()


def render_analysis_tab(budget, max_projects, min_roi):
    """Render ROI analysis and portfolio optimization."""
    st.markdown("### 📊 ROI Analysis & Portfolio Optimization")
    
    if len(st.session_state.use_cases) < 1:
        st.warning("Please add at least 1 use case to perform analysis. Recommended: 5+ use cases.")
        return
    
    # Run analysis
    calculator = ROICalculator()
    optimizer = PortfolioOptimizer(
        budget_constraint=budget,
        max_projects=max_projects,
        min_roi_threshold=min_roi
    )
    
    # Calculate ROI metrics
    st.session_state.roi_metrics = calculator.calculate_batch(st.session_state.use_cases)
    
    # Optimize portfolio
    st.session_state.portfolio_items = optimizer.optimize(
        st.session_state.use_cases,
        st.session_state.roi_metrics
    )
    
    # Display summary metrics
    st.markdown("#### 📈 Portfolio Summary")
    summary = optimizer.get_selection_summary(st.session_state.portfolio_items)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Selected Projects", summary['count'])
    with col2:
        st.metric("Total Investment", f"${summary['total_investment']:,.0f}")
    with col3:
        st.metric("Total NPV", f"${summary['total_npv']:,.0f}")
    with col4:
        st.metric("Average ROI", f"{summary['average_roi']:.1f}%")
    
    st.markdown("---")
    
    # ROI Details Table
    st.markdown("#### 💰 ROI Metrics by Initiative")
    
    roi_data = []
    for item in st.session_state.portfolio_items:
        roi_data.append({
            "Initiative": item.use_case.name,
            "Initial Cost": f"${item.use_case.initial_cost:,.0f}",
            "Annual Benefit": f"${item.use_case.annual_benefit:,.0f}",
            "ROI %": f"{item.roi_metrics.basic_roi_percent:.1f}%",
            "NPV": f"${item.roi_metrics.npv:,.0f}",
            "Payback (months)": f"{item.roi_metrics.payback_months:.1f}" if item.roi_metrics.payback_months != float('inf') else "N/A",
            "Risk-Adjusted": f"${item.roi_metrics.risk_adjusted_value:,.0f}",
            "Quadrant": item.quadrant,
            "Score": f"{item.priority_score:.1f}",
            "Selected": "✅" if item.selected else "❌"
        })
    
    df = pd.DataFrame(roi_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Impact-Effort Matrix")
        
        # Create scatter plot
        effort_map = {EffortLevel.LOW: 1, EffortLevel.MEDIUM: 2, EffortLevel.HIGH: 3}
        impact_map = {ImpactLevel.LOW: 1, ImpactLevel.MEDIUM: 2, ImpactLevel.HIGH: 3}
        
        scatter_data = []
        for item in st.session_state.portfolio_items:
            scatter_data.append({
                "name": item.use_case.name,
                "effort": effort_map[item.use_case.effort_level],
                "impact": impact_map[item.use_case.impact_level],
                "npv": abs(item.roi_metrics.npv),
                "selected": "Selected" if item.selected else "Not Selected",
                "quadrant": item.quadrant
            })
        
        scatter_df = pd.DataFrame(scatter_data)
        
        fig = px.scatter(
            scatter_df,
            x="effort",
            y="impact",
            size="npv",
            color="selected",
            hover_name="name",
            text="name",
            color_discrete_map={"Selected": "#667eea", "Not Selected": "#e2e8f0"},
            labels={"effort": "Effort", "impact": "Impact"}
        )
        
        fig.update_traces(textposition="top center", textfont_size=10)
        fig.update_layout(
            xaxis=dict(tickvals=[1, 2, 3], ticktext=["Low", "Medium", "High"]),
            yaxis=dict(tickvals=[1, 2, 3], ticktext=["Low", "Medium", "High"]),
            showlegend=True,
            height=400
        )
        
        # Add quadrant labels
        fig.add_annotation(x=1, y=3, text="🚀 Quick Wins", showarrow=False, font=dict(size=12, color="green"))
        fig.add_annotation(x=3, y=3, text="🏗️ Major Projects", showarrow=False, font=dict(size=12, color="orange"))
        fig.add_annotation(x=1, y=1, text="📝 Fill-ins", showarrow=False, font=dict(size=12, color="gray"))
        fig.add_annotation(x=3, y=1, text="🚫 Avoid", showarrow=False, font=dict(size=12, color="red"))
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 ROI Comparison")
        
        roi_chart_data = []
        for item in st.session_state.portfolio_items:
            roi_chart_data.append({
                "Initiative": item.use_case.name[:20],
                "ROI %": item.roi_metrics.basic_roi_percent,
                "Selected": "Selected" if item.selected else "Not Selected"
            })
        
        roi_df = pd.DataFrame(roi_chart_data)
        
        fig2 = px.bar(
            roi_df,
            x="Initiative",
            y="ROI %",
            color="Selected",
            color_discrete_map={"Selected": "#667eea", "Not Selected": "#e2e8f0"}
        )
        
        fig2.add_hline(y=min_roi, line_dash="dash", line_color="red", 
                       annotation_text=f"Min ROI: {min_roi}%")
        fig2.update_layout(height=400)
        
        st.plotly_chart(fig2, use_container_width=True)


def render_roadmap_tab():
    """Render the roadmap generation tab."""
    st.markdown("### 🗓️ AI Roadmap")
    
    if not st.session_state.portfolio_items:
        st.warning("Please run the analysis first to generate the roadmap.")
        return
    
    # Generate roadmap
    generator = RoadmapGenerator(start_date=date.today())
    st.session_state.roadmap_items = generator.generate_roadmap(
        st.session_state.portfolio_items,
        selected_only=True
    )
    
    if not st.session_state.roadmap_items:
        st.warning("No projects selected for roadmap. Adjust constraints and re-run analysis.")
        return
    
    # Roadmap summary
    summary = generator.get_roadmap_summary(st.session_state.roadmap_items)
    
    # Phase cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📅 Q1 (0-3 Months)")
        q1_data = summary.get(TimeHorizon.Q1.value, {"count": 0, "projects": [], "total_npv": 0})
        st.metric("Projects", q1_data["count"])
        st.metric("Total NPV", f"${q1_data['total_npv']:,.0f}")
        if q1_data["projects"]:
            for p in q1_data["projects"]:
                st.markdown(f"• {p}")
    
    with col2:
        st.markdown("#### 📆 Year 1 (3-12 Months)")
        y1_data = summary.get(TimeHorizon.YEAR_1.value, {"count": 0, "projects": [], "total_npv": 0})
        st.metric("Projects", y1_data["count"])
        st.metric("Total NPV", f"${y1_data['total_npv']:,.0f}")
        if y1_data["projects"]:
            for p in y1_data["projects"]:
                st.markdown(f"• {p}")
    
    with col3:
        st.markdown("#### 🗓️ Years 1-3")
        y3_data = summary.get(TimeHorizon.YEAR_3.value, {"count": 0, "projects": [], "total_npv": 0})
        st.metric("Projects", y3_data["count"])
        st.metric("Total NPV", f"${y3_data['total_npv']:,.0f}")
        if y3_data["projects"]:
            for p in y3_data["projects"]:
                st.markdown(f"• {p}")
    
    st.markdown("---")
    
    # Gantt Chart
    st.markdown("#### 📊 Timeline Visualization")
    
    gantt_data = []
    for item in st.session_state.roadmap_items:
        gantt_data.append({
            "Task": item.use_case.name,
            "Start": item.start_date,
            "Finish": item.end_date,
            "Phase": item.time_horizon.value,
            "NPV": item.roi_metrics.npv
        })
    
    gantt_df = pd.DataFrame(gantt_data)
    
    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Phase",
        hover_data=["NPV"],
        color_discrete_map={
            TimeHorizon.Q1.value: "#10b981",
            TimeHorizon.YEAR_1.value: "#667eea",
            TimeHorizon.YEAR_3.value: "#8b5cf6"
        }
    )
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=max(300, len(gantt_data) * 50))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed roadmap table
    st.markdown("#### 📋 Detailed Roadmap")
    
    roadmap_table = []
    for item in st.session_state.roadmap_items:
        roadmap_table.append({
            "Initiative": item.use_case.name,
            "Phase": item.time_horizon.value,
            "Start": item.start_date.strftime("%Y-%m-%d"),
            "End": item.end_date.strftime("%Y-%m-%d"),
            "Milestones": ", ".join(item.milestones[:3]),
            "Rationale": item.phase_rationale
        })
    
    roadmap_df = pd.DataFrame(roadmap_table)
    st.dataframe(roadmap_df, use_container_width=True, hide_index=True)


def render_export_tab():
    """Render the canvas export tab."""
    st.markdown("### 📄 Export AI ROI & Roadmap Canvas")
    
    if not st.session_state.roadmap_items:
        st.warning("Please complete the analysis and roadmap generation first.")
        return
    
    # Validate config
    config = st.session_state.canvas_config
    if not all([config['organization_name'], config['designed_by'], config['primary_goal']]):
        st.warning("Please fill in the Canvas Configuration in the sidebar before exporting.")
    
    # Build canvas
    exporter = CanvasExporter()
    
    strategic_focus = st.text_area(
        "Strategic Focus Areas (one per line)",
        value="Operational efficiency\nCustomer experience\nRevenue growth\nRisk reduction",
        height=100
    )
    
    if st.button("🔄 Generate Canvas", use_container_width=True, type="primary"):
        canvas = exporter.build_canvas(
            use_cases=st.session_state.use_cases,
            portfolio_items=st.session_state.portfolio_items,
            roadmap_items=st.session_state.roadmap_items,
            organization_name=config['organization_name'] or "Organization",
            designed_by=config['designed_by'] or "AI Strategy Team",
            designed_for=config['designed_for'] or "Executive Leadership",
            primary_goal=config['primary_goal'] or "Strategic AI adoption",
            strategic_focus=[s.strip() for s in strategic_focus.split("\n") if s.strip()]
        )
        st.session_state.canvas = canvas
        st.success("Canvas generated successfully!")
    
    if st.session_state.canvas:
        st.markdown("---")
        
        # Export buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📥 JSON Export")
            json_content = exporter.export_json(st.session_state.canvas)
            st.download_button(
                "⬇️ Download JSON",
                data=json_content,
                file_name="ai_roi_canvas.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            st.markdown("#### 📝 Markdown Export")
            md_content = exporter.export_markdown(st.session_state.canvas)
            st.download_button(
                "⬇️ Download Markdown",
                data=md_content,
                file_name="ai_roi_canvas.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col3:
            st.markdown("#### 🌐 HTML Export")
            html_content = exporter.export_html(st.session_state.canvas)
            st.download_button(
                "⬇️ Download HTML",
                data=html_content,
                file_name="ai_roi_canvas.html",
                mime="text/html",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Preview
        st.markdown("#### 👁️ Canvas Preview")
        
        tab1, tab2 = st.tabs(["📝 Markdown View", "🌐 HTML Preview"])
        
        with tab1:
            st.markdown(exporter.export_markdown(st.session_state.canvas))
        
        with tab2:
            st.components.v1.html(
                exporter.export_html(st.session_state.canvas),
                height=800,
                scrolling=True
            )


def main():
    """Main application entry point."""
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🎯 AI ROI & Roadmap Canvas Agent</h1>', unsafe_allow_html=True)
    
    # Sidebar
    budget, max_projects, min_roi = render_sidebar()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Interview",
        "➕ Manual Input", 
        "📊 Analysis",
        "🗓️ Roadmap",
        "📄 Export"
    ])
    
    with tab1:
        render_chat_tab()
    
    with tab2:
        render_manual_input_tab()
    
    with tab3:
        render_analysis_tab(budget, max_projects, min_roi)
    
    with tab4:
        render_roadmap_tab()
    
    with tab5:
        render_export_tab()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #666;'>AI ROI & Roadmap Canvas Agent | "
        "Built for Strategic AI Planning</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

