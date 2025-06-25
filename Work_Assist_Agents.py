import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json
from datetime import datetime, timedelta
import re
from typing import Dict, List, Any
import base64
import requests

# Configure page
st.set_page_config(
    page_title="🤖 Multi-Agent Workplace Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .agent-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .task-status {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-pending { background-color: #fff3cd; color: #856404; }
    .status-processing { background-color: #d1ecf1; color: #0c5460; }
    .status-completed { background-color: #d4edda; color: #155724; }
</style>
""", unsafe_allow_html=True)

class MultiAgentAssistant:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agents = {
            "📋 Checksheet Specialist": {
                "description": "Creates comprehensive checklists, audit forms, and quality control sheets",
                "prompt_prefix": "You are a Checksheet Specialist expert in creating detailed, professional checklists and audit forms. Focus on completeness, clarity, and actionability.",
                "color": "#FF6B6B"
            },
            "📊 Data Analyst": {
                "description": "Analyzes data, creates visualizations, and provides insights",
                "prompt_prefix": "You are a Data Analyst expert in statistical analysis, data visualization, and business intelligence. Provide clear insights with actionable recommendations.",
                "color": "#4ECDC4"
            },
            "📈 Spreadsheet Expert": {
                "description": "Designs and optimizes spreadsheets with formulas and automation",
                "prompt_prefix": "You are a Spreadsheet Expert specialized in Excel/Google Sheets optimization, complex formulas, and data organization. Create efficient, user-friendly solutions.",
                "color": "#45B7D1"
            },
            "💡 Strategic Advisor": {
                "description": "Provides strategic business advice and decision-making support",
                "prompt_prefix": "You are a Strategic Business Advisor with expertise in business strategy, decision-making frameworks, and organizational development. Provide thoughtful, actionable advice.",
                "color": "#96CEB4"
            },
            "👥 Leadership Coach": {
                "description": "Offers leadership development and team management guidance",
                "prompt_prefix": "You are a Leadership Coach specializing in team development, communication, and leadership effectiveness. Provide practical, empathetic guidance.",
                "color": "#FFEAA7"
            },
            "🎯 Six Sigma Black Belt": {
                "description": "Applies Six Sigma methodology for process improvement",
                "prompt_prefix": "You are a Six Sigma Black Belt expert in DMAIC methodology, statistical process control, and quality improvement. Focus on data-driven solutions.",
                "color": "#DDA0DD"
            },
            "⚡ Lean Manufacturing Expert": {
                "description": "Implements lean principles and waste reduction strategies",
                "prompt_prefix": "You are a Lean Manufacturing Expert specializing in waste elimination, value stream mapping, and continuous improvement. Focus on efficiency and value creation.",
                "color": "#98D8C8"
            },
            "🎯 Productivity Coach": {
                "description": "Helps with task management, prioritization, and productivity optimization",
                "prompt_prefix": "You are a Productivity Coach expert in time management, goal setting, and workflow optimization. Help users stay focused and achieve their objectives.",
                "color": "#F7DC6F"
            },
            "🤖 General Assistant": {
                "description": "Handles diverse tasks and provides comprehensive support",
                "prompt_prefix": "You are a versatile General Assistant capable of handling various business tasks. Adapt your expertise to the specific needs presented.",
                "color": "#BB8FCE"
            }
        }
        
    def get_agent_response(self, agent_name: str, problem_description: str, additional_context: str = "") -> str:
        agent_info = self.agents[agent_name]
        
        full_prompt = f"""
        {agent_info['prompt_prefix']}
        
        Problem/Task: {problem_description}
        
        Additional Context: {additional_context}
        
        Please provide a comprehensive response that includes:
        1. Analysis of the situation
        2. Specific recommendations or solutions
        3. Step-by-step action items where applicable
        4. Expected outcomes or benefits
        5. Any templates, examples, or tools that would be helpful
        
        Format your response clearly with headers and bullet points where appropriate.
        """
        
        try:
            # Use Claude API via requests since anthropic package might not be available
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4000,
                "temperature": 0.7,
                "messages": [{"role": "user", "content": full_prompt}]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["content"][0]["text"]
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error getting response from {agent_name}: {str(e)}"

def create_sample_data():
    """Create sample data for demonstration"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    data = {
        'Date': dates,
        'Production': [100 + i*0.5 + (i%30)*2 for i in range(len(dates))],
        'Quality_Score': [95 + (i%10)*0.5 - (i%50)*0.1 for i in range(len(dates))],
        'Defects': [5 - (i%20)*0.2 + (i%15)*0.3 for i in range(len(dates))],
        'Efficiency': [85 + (i%25)*0.8 + (i%40)*0.3 for i in range(len(dates))]
    }
    return pd.DataFrame(data)

def create_dashboard():
    """Create a sample dashboard"""
    df = create_sample_data()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Avg Production</h3>
            <h2>245.6</h2>
            <p style="color: green;">↗️ +12.3%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>⭐ Quality Score</h3>
            <h2>94.8%</h2>
            <p style="color: green;">↗️ +2.1%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Efficiency</h3>
            <h2>87.3%</h2>
            <p style="color: orange;">↔️ -0.5%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🚫 Defect Rate</h3>
            <h2>3.2%</h2>
            <p style="color: red;">↗️ +0.8%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.line(df.tail(30), x='Date', y='Production', 
                      title='Production Trend (Last 30 Days)')
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.scatter(df.tail(30), x='Production', y='Quality_Score', 
                         size='Efficiency', color='Defects',
                         title='Production vs Quality')
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 Multi-Agent Workplace Assistant</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key input
        api_key = st.text_input("Claude API Key:", type="password", 
                               help="Enter your Anthropic Claude API key")
        
        if not api_key:
            st.warning("⚠️ Please enter your Claude API key to use the agents")
            # Don't stop the app, just disable agent functionality
            agent_available = False
        else:
            try:
                if st.session_state.assistant is None or st.session_state.assistant.api_key != api_key:
                    st.session_state.assistant = MultiAgentAssistant(api_key)
                st.success("✅ API Key provided")
                agent_available = True
            except Exception as e:
                st.error(f"❌ Error with API key: {str(e)}")
                agent_available = False
        
        st.divider()
        
        # Agent selection
        st.header("🤖 Select Agent")
        if agent_available:
            selected_agent = st.selectbox(
                "Choose an agent:",
                list(st.session_state.assistant.agents.keys()),
                help="Select the most appropriate agent for your task"
            )
            
            # Display agent info
            agent_info = st.session_state.assistant.agents[selected_agent]
            st.markdown(f"""
            <div class="agent-card">
                <h4>{selected_agent}</h4>
                <p>{agent_info['description']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Enter API key to select agents")
            selected_agent = None
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Problem Solver", "📊 Dashboard", "📋 Task Manager", "💡 Knowledge Base"])
    
    with tab1:
        st.header("🎯 Problem Solver")
        
        if not agent_available:
            st.warning("⚠️ Please enter your Claude API key in the sidebar to use the Problem Solver")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Problem description
            problem_description = st.text_area(
                "Describe your problem or task:",
                height=150,
                placeholder="Example: I need to improve our quality control process. We're seeing a 5% defect rate and want to reduce it to under 2%..."
            )
            
            # Additional context
            additional_context = st.text_area(
                "Additional context (optional):",
                height=100,
                placeholder="Budget constraints, timeline, team size, current tools, etc."
            )
            
            # Priority and urgency
            col_priority, col_urgency = st.columns(2)
            with col_priority:
                priority = st.selectbox("Priority:", ["Low", "Medium", "High", "Critical"])
            with col_urgency:
                urgency = st.selectbox("Urgency:", ["Low", "Medium", "High", "Immediate"])
            
            # Submit button
            if st.button("🚀 Get Agent Assistance", type="primary"):
                if problem_description and selected_agent:
                    with st.spinner(f"🤖 {selected_agent} is analyzing your problem..."):
                        response = st.session_state.assistant.get_agent_response(
                            selected_agent, 
                            problem_description, 
                            f"Priority: {priority}, Urgency: {urgency}. {additional_context}"
                        )
                    
                    st.success("✅ Analysis Complete!")
                    st.markdown("### 📝 Agent Response:")
                    st.markdown(response)
                    
                    # Save to session state for task manager
                    task = {
                        'id': len(st.session_state.tasks) + 1,
                        'title': problem_description[:50] + "..." if len(problem_description) > 50 else problem_description,
                        'agent': selected_agent,
                        'priority': priority,
                        'urgency': urgency,
                        'status': 'Completed',
                        'created': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'response': response
                    }
                    st.session_state.tasks.append(task)
                    
                elif not problem_description:
                    st.warning("⚠️ Please describe your problem or task")
                elif not selected_agent:
                    st.warning("⚠️ Please select an agent")
        
        with col2:
            st.markdown("### 🎯 Quick Actions")
            
            quick_actions = [
                "Create quality checklist",
                "Analyze production data",
                "Design KPI dashboard",
                "Develop training plan",
                "Process improvement project",
                "Cost reduction analysis",
                "Team performance review",
                "Risk assessment"
            ]
            
            for action in quick_actions:
                if st.button(action, key=f"quick_{action}"):
                    # Auto-fill the problem description with the quick action
                    st.session_state[f"quick_action_{action}"] = action
                    st.rerun()
    
    with tab2:
        st.header("📊 Performance Dashboard")
        st.markdown("*Sample dashboard showing key metrics and visualizations*")
        create_dashboard()
    
    with tab3:
        st.header("📋 Task Manager")
        
        if st.session_state.tasks:
            st.markdown("### 📝 Recent Tasks")
            
            for task in reversed(st.session_state.tasks[-10:]):  # Show last 10 tasks
                with st.expander(f"#{task['id']} - {task['title']} ({task['agent']})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Priority:** {task['priority']}")
                        st.markdown(f"**Urgency:** {task['urgency']}")
                    with col2:
                        st.markdown(f"**Status:** {task['status']}")
                        st.markdown(f"**Created:** {task['created']}")
                    with col3:
                        st.markdown(f"**Agent:** {task['agent']}")
                    
                    st.markdown("**Response:**")
                    st.markdown(task['response'][:500] + "..." if len(task['response']) > 500 else task['response'])
            
            if st.button("🗑️ Clear All Tasks"):
                st.session_state.tasks = []
                st.rerun()
        else:
            st.info("📝 No tasks yet. Use the Problem Solver tab to create your first task!")
    
    with tab4:
        st.header("💡 Knowledge Base")
        
        if agent_available:
            st.markdown("### 🤖 Available Agents")
            
            for agent_name, agent_info in st.session_state.assistant.agents.items():
                with st.expander(agent_name):
                    st.markdown(f"**Description:** {agent_info['description']}")
                    st.markdown(f"**Specialization:** {agent_info['prompt_prefix']}")
        
        st.markdown("### 📚 Best Practices")
        
        best_practices = {
            "Problem Description": [
                "Be specific about the current situation",
                "Include quantifiable metrics when possible",
                "Mention constraints and limitations",
                "Specify desired outcomes"
            ],
            "Agent Selection": [
                "Choose the agent that best matches your problem domain",
                "Consider using multiple agents for complex problems",
                "Start with the General Assistant if unsure",
                "Review agent descriptions before selecting"
            ],
            "Context Provision": [
                "Include budget and timeline constraints",
                "Mention team size and capabilities",
                "Specify current tools and systems",
                "Note any regulatory requirements"
            ]
        }
        
        for category, practices in best_practices.items():
            st.markdown(f"**{category}:**")
            for practice in practices:
                st.markdown(f"• {practice}")
            st.markdown("")

if __name__ == "__main__":
    main()
