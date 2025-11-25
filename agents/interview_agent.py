"""
Interview Agent

AI-powered conversational agent for capturing AI use cases.
Uses OpenAI GPT for intelligent interviewing and data extraction.
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from models.data_models import AIUseCase, EffortLevel, ImpactLevel, RiskLevel


class InterviewAgent:
    """
    Conversational agent for capturing AI use case details.
    """
    
    SYSTEM_PROMPT = """You are an AI ROI & Roadmap Canvas consultant. Your role is to help organizations capture and analyze AI use cases.

You will interview the user to gather information about potential AI initiatives. For each use case, you need to collect:

1. **Name**: A clear, concise name for the initiative
2. **Problem Statement**: The business problem being addressed
3. **KPIs**: Key performance indicators to measure success
4. **Initial Cost**: One-time implementation cost ($)
5. **Annual Cost**: Ongoing operational costs per year ($)
6. **Annual Benefit**: Expected annual financial benefit ($)
7. **Implementation Time**: Months to implement
8. **Effort Level**: Low, Medium, or High
9. **Impact Level**: Low, Medium, or High
10. **Risk Level**: Low, Medium, or High
11. **Dependencies**: Other projects or prerequisites
12. **Skills Required**: Technical and business skills needed
13. **Technology Required**: Technology stack/tools needed
14. **Soft Benefits**: Non-quantifiable benefits
15. **Risk Factors**: Specific risks to consider

Be conversational and helpful. Ask clarifying questions when needed. Guide users to provide realistic estimates.

When you have collected enough information for a use case, output a JSON block with the data in this format:
```json
{
    "name": "Use Case Name",
    "problem_statement": "Description of the problem",
    "kpis": ["KPI 1", "KPI 2"],
    "initial_cost": 100000,
    "annual_cost": 20000,
    "annual_benefit": 150000,
    "implementation_months": 6,
    "effort_level": "Medium",
    "impact_level": "High",
    "risk_level": "Medium",
    "dependencies": [],
    "skills_required": ["Data Science", "ML Engineering"],
    "technology_required": ["Python", "AWS"],
    "soft_benefits": ["Improved customer satisfaction"],
    "risk_factors": ["Data quality concerns"]
}
```

Start by introducing yourself and asking about the organization and their AI goals."""

    EXTRACTION_PROMPT = """Based on the conversation, extract the AI use case information and return it as a JSON object.

If any field is missing or unclear, use reasonable defaults:
- initial_cost: 50000
- annual_cost: 10000  
- annual_benefit: 75000
- implementation_months: 6
- effort_level: "Medium"
- impact_level: "Medium"
- risk_level: "Medium"

Return ONLY the JSON object, no other text.

Conversation:
{conversation}

Extract and return the use case as JSON:"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the interview agent.
        
        Args:
            api_key: OpenAI API key (optional, uses env var if not provided)
        """
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.conversation_history: List[Dict] = []
        self.captured_use_cases: List[AIUseCase] = []
        self.use_case_counter = 0
        
        # Initialize with system prompt
        self.conversation_history.append({
            "role": "system",
            "content": self.SYSTEM_PROMPT
        })
    
    def chat(self, user_message: str) -> str:
        """
        Send a message and get a response.
        
        Args:
            user_message: The user's message
            
        Returns:
            Agent's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=1500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Check for JSON in response (use case captured)
            use_case = self._extract_use_case_from_response(assistant_message)
            if use_case:
                self.captured_use_cases.append(use_case)
            
            return assistant_message
            
        except Exception as e:
            error_msg = f"Error communicating with AI: {str(e)}"
            return error_msg
    
    def _extract_use_case_from_response(self, response: str) -> Optional[AIUseCase]:
        """
        Extract use case from assistant response if JSON block present.
        """
        # Look for JSON block
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if not json_match:
            json_match = re.search(r'```\s*({\s*"name".*?})\s*```', response, re.DOTALL)
        
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return self._create_use_case_from_dict(data)
            except json.JSONDecodeError:
                return None
        
        return None
    
    def _create_use_case_from_dict(self, data: dict) -> AIUseCase:
        """
        Create AIUseCase from dictionary data.
        """
        self.use_case_counter += 1
        
        # Map string levels to enums
        effort_map = {"low": EffortLevel.LOW, "medium": EffortLevel.MEDIUM, "high": EffortLevel.HIGH}
        impact_map = {"low": ImpactLevel.LOW, "medium": ImpactLevel.MEDIUM, "high": ImpactLevel.HIGH}
        risk_map = {"low": RiskLevel.LOW, "medium": RiskLevel.MEDIUM, "high": RiskLevel.HIGH}
        
        return AIUseCase(
            id=f"UC{self.use_case_counter:03d}",
            name=data.get("name", f"Use Case {self.use_case_counter}"),
            problem_statement=data.get("problem_statement", ""),
            kpis=data.get("kpis", []),
            initial_cost=float(data.get("initial_cost", 50000)),
            annual_cost=float(data.get("annual_cost", 10000)),
            annual_benefit=float(data.get("annual_benefit", 75000)),
            implementation_months=int(data.get("implementation_months", 6)),
            benefit_start_month=int(data.get("benefit_start_month", 1)),
            effort_level=effort_map.get(str(data.get("effort_level", "medium")).lower(), EffortLevel.MEDIUM),
            impact_level=impact_map.get(str(data.get("impact_level", "medium")).lower(), ImpactLevel.MEDIUM),
            risk_level=risk_map.get(str(data.get("risk_level", "medium")).lower(), RiskLevel.MEDIUM),
            dependencies=data.get("dependencies", []),
            skills_required=data.get("skills_required", []),
            technology_required=data.get("technology_required", []),
            soft_benefits=data.get("soft_benefits", []),
            risk_factors=data.get("risk_factors", [])
        )
    
    def extract_use_case_from_conversation(self) -> Optional[AIUseCase]:
        """
        Use AI to extract use case from recent conversation.
        """
        if len(self.conversation_history) < 3:
            return None
        
        # Get recent messages
        recent = self.conversation_history[-10:]
        conversation_text = "\n".join([
            f"{m['role'].upper()}: {m['content']}" 
            for m in recent 
            if m['role'] != 'system'
        ])
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": self.EXTRACTION_PROMPT.format(conversation=conversation_text)
                }],
                temperature=0.3,
                max_tokens=1000
            )
            
            json_str = response.choices[0].message.content
            # Clean up JSON
            json_str = json_str.strip()
            if json_str.startswith("```"):
                json_str = re.sub(r'^```\w*\n?', '', json_str)
                json_str = re.sub(r'\n?```$', '', json_str)
            
            data = json.loads(json_str)
            return self._create_use_case_from_dict(data)
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return None
    
    def get_captured_use_cases(self) -> List[AIUseCase]:
        """Return list of captured use cases."""
        return self.captured_use_cases
    
    def add_use_case_manually(self, use_case: AIUseCase) -> None:
        """Add a use case directly without chat."""
        self.captured_use_cases.append(use_case)
    
    def clear_conversation(self) -> None:
        """Reset conversation history but keep captured use cases."""
        self.conversation_history = [{
            "role": "system",
            "content": self.SYSTEM_PROMPT
        }]
    
    def reset_all(self) -> None:
        """Reset everything."""
        self.clear_conversation()
        self.captured_use_cases = []
        self.use_case_counter = 0
    
    def get_welcome_message(self) -> str:
        """Get initial welcome message."""
        return """👋 Welcome to the AI ROI & Roadmap Canvas Agent!

I'm here to help you capture and analyze your AI initiatives. We'll work together to:

1. 📝 **Capture** at least 5 AI use cases with detailed metrics
2. 📊 **Calculate** ROI, NPV, and payback periods
3. 🎯 **Prioritize** using an Impact-Effort matrix
4. 🗓️ **Generate** a phased roadmap (Q1, Year 1, Year 3)
5. 📄 **Export** your AI ROI & Roadmap Canvas

Let's get started! Tell me about your organization and what AI opportunities you're exploring."""
    
    def get_summary_prompt(self) -> str:
        """Get prompt asking for more use cases or to proceed."""
        count = len(self.captured_use_cases)
        if count < 5:
            return f"""
Great progress! We've captured {count} use case(s) so far.

We need at least 5 use cases for a comprehensive analysis. Would you like to:
1. Add another use case
2. Review what we have so far

What would you like to do?"""
        else:
            return f"""
Excellent! We've captured {count} use cases - that's enough for a solid analysis!

Would you like to:
1. Add more use cases
2. Proceed to ROI analysis and roadmap generation

What would you like to do?"""


class MockInterviewAgent:
    """
    Mock agent for testing without OpenAI API.
    Provides sample use cases and canned responses.
    """
    
    def __init__(self):
        self.captured_use_cases: List[AIUseCase] = []
        self.use_case_counter = 0
        self.interaction_count = 0
    
    def chat(self, user_message: str) -> str:
        """Provide canned responses based on interaction count."""
        self.interaction_count += 1
        
        if self.interaction_count == 1:
            return self.get_welcome_message()
        
        # Simple keyword detection for adding sample use cases
        lower_msg = user_message.lower()
        
        if any(word in lower_msg for word in ["sample", "example", "demo", "test"]):
            self._add_sample_use_cases()
            return f"""I've added 5 sample AI use cases for demonstration:

1. **Customer Churn Prediction** - ML model to predict customer attrition
2. **Intelligent Document Processing** - Automate document extraction and classification
3. **Predictive Maintenance** - ML system for equipment failure prediction
4. **AI Chatbot** - Customer service automation
5. **Demand Forecasting** - ML-powered inventory optimization

You now have {len(self.captured_use_cases)} use cases ready for analysis!

Would you like to proceed to ROI analysis and roadmap generation?"""
        
        return f"""I understand you're interested in AI initiatives.

To add a use case, please provide:
- Name and problem statement
- Estimated costs and benefits
- Implementation timeline
- Effort and impact levels

Or say "add sample" to load demonstration use cases."""
    
    def _add_sample_use_cases(self) -> None:
        """Add 5 sample use cases for demo."""
        samples = [
            AIUseCase(
                id="UC001",
                name="Customer Churn Prediction",
                problem_statement="High customer attrition rate costing $2M annually in lost revenue",
                kpis=["Churn rate reduction", "Customer lifetime value", "Prediction accuracy"],
                initial_cost=150000,
                annual_cost=30000,
                annual_benefit=400000,
                implementation_months=4,
                benefit_start_month=1,
                effort_level=EffortLevel.MEDIUM,
                impact_level=ImpactLevel.HIGH,
                risk_level=RiskLevel.LOW,
                dependencies=[],
                skills_required=["Data Science", "ML Engineering", "Python"],
                technology_required=["Python", "Scikit-learn", "AWS SageMaker"],
                soft_benefits=["Improved customer relationships", "Proactive retention"],
                risk_factors=["Data quality", "Model accuracy"]
            ),
            AIUseCase(
                id="UC002",
                name="Intelligent Document Processing",
                problem_statement="Manual document processing consuming 20 FTE hours daily",
                kpis=["Processing time", "Accuracy rate", "Cost per document"],
                initial_cost=200000,
                annual_cost=40000,
                annual_benefit=500000,
                implementation_months=6,
                benefit_start_month=1,
                effort_level=EffortLevel.HIGH,
                impact_level=ImpactLevel.HIGH,
                risk_level=RiskLevel.MEDIUM,
                dependencies=[],
                skills_required=["NLP", "Computer Vision", "Cloud Architecture"],
                technology_required=["Azure AI", "OCR", "Python"],
                soft_benefits=["Employee satisfaction", "Faster turnaround"],
                risk_factors=["Document variety", "Integration complexity"]
            ),
            AIUseCase(
                id="UC003",
                name="Predictive Maintenance",
                problem_statement="Unexpected equipment failures causing $500K in annual downtime",
                kpis=["Downtime reduction", "Maintenance cost", "Equipment lifespan"],
                initial_cost=300000,
                annual_cost=50000,
                annual_benefit=350000,
                implementation_months=9,
                benefit_start_month=2,
                effort_level=EffortLevel.HIGH,
                impact_level=ImpactLevel.MEDIUM,
                risk_level=RiskLevel.MEDIUM,
                dependencies=["IoT Sensor Deployment"],
                skills_required=["IoT", "ML Engineering", "Industrial Engineering"],
                technology_required=["IoT Platform", "Time Series ML", "Edge Computing"],
                soft_benefits=["Safety improvements", "Better planning"],
                risk_factors=["Sensor reliability", "Model drift"]
            ),
            AIUseCase(
                id="UC004",
                name="AI Customer Service Chatbot",
                problem_statement="High call center costs and long wait times affecting satisfaction",
                kpis=["Call deflection rate", "Customer satisfaction", "Resolution time"],
                initial_cost=100000,
                annual_cost=25000,
                annual_benefit=300000,
                implementation_months=3,
                benefit_start_month=1,
                effort_level=EffortLevel.LOW,
                impact_level=ImpactLevel.HIGH,
                risk_level=RiskLevel.LOW,
                dependencies=[],
                skills_required=["NLP", "Conversation Design", "Integration"],
                technology_required=["Dialogflow", "API Integration", "Analytics"],
                soft_benefits=["24/7 availability", "Consistent responses"],
                risk_factors=["User adoption", "Edge cases"]
            ),
            AIUseCase(
                id="UC005",
                name="Demand Forecasting",
                problem_statement="Inventory inefficiencies causing $1M in carrying costs and stockouts",
                kpis=["Forecast accuracy", "Inventory turnover", "Stockout rate"],
                initial_cost=180000,
                annual_cost=35000,
                annual_benefit=450000,
                implementation_months=5,
                benefit_start_month=1,
                effort_level=EffortLevel.MEDIUM,
                impact_level=ImpactLevel.HIGH,
                risk_level=RiskLevel.LOW,
                dependencies=[],
                skills_required=["Data Science", "Supply Chain", "Statistics"],
                technology_required=["Python", "Time Series Models", "BI Tools"],
                soft_benefits=["Better supplier relationships", "Reduced waste"],
                risk_factors=["Market volatility", "Data availability"]
            )
        ]
        
        self.captured_use_cases = samples
        self.use_case_counter = 5
    
    def get_captured_use_cases(self) -> List[AIUseCase]:
        return self.captured_use_cases
    
    def add_use_case_manually(self, use_case: AIUseCase) -> None:
        self.use_case_counter += 1
        use_case.id = f"UC{self.use_case_counter:03d}"
        self.captured_use_cases.append(use_case)
    
    def get_welcome_message(self) -> str:
        return """👋 Welcome to the AI ROI & Roadmap Canvas Agent! (Demo Mode)

I'm here to help you build your AI strategy. In this demo:

1. Say **"add sample"** to load 5 example AI use cases
2. Or describe your own AI initiatives

Once we have use cases, we'll:
📊 Calculate ROI metrics
🎯 Create an Impact-Effort portfolio
🗓️ Generate a phased roadmap
📄 Export your AI ROI Canvas

What would you like to do?"""
    
    def reset_all(self) -> None:
        self.captured_use_cases = []
        self.use_case_counter = 0
        self.interaction_count = 0

