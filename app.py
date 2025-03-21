import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import time
from datetime import datetime

# Import EngE-AI components
from ollama_setup import OllamaManager
from models.tutor_model import EngineeringTutor
from models.scenario_generator import ScenarioGenerator

# Set up page configuration
st.set_page_config(
    page_title="EngE-AI Dashboard",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css = """
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 1rem;
        }

        .sub-header {
            font-size: 1.5rem;
            font-weight: 600;
            color: #2563EB;
        }

        .card {
            border-radius: 10px;
            padding: 1.5rem;
            background-color: #F8FAFC;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }

        .metric-card {
            text-align: center;
            padding: 1rem;
            border-radius: 10px;
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            color: white;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
        }

        .metric-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }

        .tab-content {
            padding: 1rem 0;
        }

        .chat-message {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.8rem;
        }

        .user-message {
            background-color: #4e76fc;
            margin-left: 2rem;
        }

        .ai-message {
            background-color: #3b8ef7;
            margin-right: 2rem;
        }

        /* Custom button styles */
        .stButton>button {
            border-radius: 5px;
            background-color: #2563EB;
            color: white;
            font-weight: 600;
            padding: 0.5rem 1rem;
            transition: all 0.3s;
        }

        .stButton>button:hover {
            background-color: #1E40AF;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'scenarios' not in st.session_state:
        st.session_state.scenarios = []
    if 'selected_course' not in st.session_state:
        st.session_state.selected_course = "CHBE 220 - Chemical Engineering Thermodynamics"
    if 'usage_data' not in st.session_state:
        # Sample usage data for initial visualization
        st.session_state.usage_data = {
            'daily_queries': [12, 18, 25, 15, 22, 30, 27],
            'engagement_hours': [5.2, 8.4, 10.1, 6.8, 9.3, 12.5, 11.2],
            'satisfaction': [4.2, 4.3, 4.5, 4.3, 4.6, 4.7, 4.5]
        }
    if 'critical_thinking_scores' not in st.session_state:
        # Sample critical thinking assessment data
        st.session_state.critical_thinking_scores = {
            'before': [65, 70, 58, 75, 62, 68, 72, 60, 73, 67],
            'after': [78, 82, 75, 85, 76, 80, 84, 73, 86, 79]
        }
    if 'model_loaded' not in st.session_state:
        st.session_state.model_loaded = False
    if 'assessment_questions' not in st.session_state:
        # Sample critical thinking assessment questions
        st.session_state.assessment_questions = [
            {
                "id": 1,
                "question": "A chemical plant is experiencing irregular pressure drops in a heat exchanger. What are the possible causes of this issue and how would you systematically investigate them?",
                "dimension": "Problem Analysis",
                "points": 10
            },
            {
                "id": 2,
                "question": "Compare and contrast the environmental impacts of using fossil fuels versus biofuels in industrial processes. What assumptions are you making in your comparison?",
                "dimension": "Evaluation of Evidence",
                "points": 10
            },
            {
                "id": 3,
                "question": "A startup claims their new catalyst improves reaction efficiency by 40%. How would you verify this claim and what additional information would you need?",
                "dimension": "Inference and Reasoning",
                "points": 10
            },
            {
                "id": 4,
                "question": "Design an experiment to determine the optimal operating temperature for a batch reactor. What control variables would you include and why?",
                "dimension": "Experimental Design",
                "points": 10
            },
            {
                "id": 5,
                "question": "How might advances in AI impact the role of chemical engineers in process design over the next decade? Support your answer with evidence.",
                "dimension": "Future Implications",
                "points": 10
            }
        ]
    if 'student_assessments' not in st.session_state:
        # Sample student assessment results
        st.session_state.student_assessments = [
            {
                "student_id": "S001",
                "name": "Alex Johnson",
                "pre_score": 65,
                "post_score": 78,
                "improvement": 13,
                "strongest_dimension": "Problem Analysis",
                "weakest_dimension": "Future Implications",
                "date_completed": "2025-02-15"
            },
            {
                "student_id": "S002",
                "name": "Taylor Smith",
                "pre_score": 70,
                "post_score": 82,
                "improvement": 12,
                "strongest_dimension": "Experimental Design",
                "weakest_dimension": "Evaluation of Evidence",
                "date_completed": "2025-02-16"
            },
            {
                "student_id": "S003",
                "name": "Jordan Williams",
                "pre_score": 58,
                "post_score": 75,
                "improvement": 17,
                "strongest_dimension": "Inference and Reasoning",
                "weakest_dimension": "Problem Analysis",
                "date_completed": "2025-02-18"
            }
        ]
    if 'system_settings' not in st.session_state:
        # Default system settings
        st.session_state.system_settings = {
            "ai_model": "llama3.2",
            "temperature": 0.7,
            "max_tokens": 1024,
            "critical_thinking_dimensions": [
                "Problem Analysis",
                "Evaluation of Evidence",
                "Inference and Reasoning",
                "Experimental Design",
                "Future Implications"
            ],
            "database_connection": "mongodb://localhost:27017/",
            "api_key": "sk-engai-xxxxxxxxxxxxxxxxxxxxx",
            "backup_frequency": "Daily",
            "feedback_collection": True
        }

# Initialize Ollama models
@st.cache_resource
def init_models():
    with st.spinner("Loading AI models... This may take a moment."):
        ollama_manager = OllamaManager()
        tutor = EngineeringTutor(ollama_manager)
        scenario_gen = ScenarioGenerator(ollama_manager)
        return ollama_manager, tutor, scenario_gen

# Dashboard layout
def main():
    load_css()
    init_session_state()

    # Header with logo
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("assets/images/logo.png", width=100)
    with col2:
        st.markdown("<div class='main-header'>EngE-AI Dashboard</div>", unsafe_allow_html=True)
        st.markdown("Engineering Education AI Tool for Critical Thinking Development")

    # Initialize models
    if not st.session_state.model_loaded:
        ollama_manager, tutor, scenario_gen = init_models()
        st.session_state.ollama_manager = ollama_manager
        st.session_state.tutor = tutor
        st.session_state.scenario_gen = scenario_gen
        st.session_state.model_loaded = True
    else:
        ollama_manager = st.session_state.ollama_manager
        tutor = st.session_state.tutor
        scenario_gen = st.session_state.scenario_gen

    # Sidebar for navigation and settings
    with st.sidebar:
        st.markdown("<div class='sub-header'>Navigation</div>", unsafe_allow_html=True)
        page = st.radio("", ["Dashboard", "Virtual Tutor", "Scenario Generator", "Critical Thinking Assessment",
                             "Settings"])

        st.markdown("<div class='sub-header'>Course Selection</div>", unsafe_allow_html=True)
        course_options = [
            "CHBE 220 - Chemical Engineering Thermodynamics",
            "CHBE 241 - Material and Energy Balances",
            "CHBE 262 - Environmental Engineering",
            "CHBE 344 - Unit Operations",
            "CHBE 351 - Transport Phenomena"
        ]
        st.session_state.selected_course = st.selectbox("", course_options)

        # Model selection
        st.markdown("<div class='sub-header'>Model Settings</div>", unsafe_allow_html=True)
        model_options = ollama_manager.list_available_models()
        selected_model = st.selectbox("AI Model", model_options, index=0)

        if st.button("Apply Settings"):
            with st.spinner("Updating model settings..."):
                ollama_manager.set_model(selected_model)
                st.success(f"Settings updated! Now using {selected_model}")

        st.markdown("---")
        st.markdown("© Made with ❤️ by Aditya Varma")

    # Main content area based on navigation
    if page == "Dashboard":
        display_dashboard()
    elif page == "Virtual Tutor":
        display_virtual_tutor(tutor)
    elif page == "Scenario Generator":
        display_scenario_generator(scenario_gen)
    elif page == "Critical Thinking Assessment":
        display_critical_thinking()
    else:  # Settings
        display_settings()

# Dashboard overview page
def display_dashboard():
    st.markdown("<div class='sub-header'>EngE-AI System Overview</div>", unsafe_allow_html=True)

    # Key metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">254</div>
            <div class="metric-label">Student Users</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">1,423</div>
            <div class="metric-label">Tutor Interactions</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">87</div>
            <div class="metric-label">Scenarios Generated</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">4.7</div>
            <div class="metric-label">Avg. Satisfaction (1-5)</div>
        </div>
        """, unsafe_allow_html=True)

    # Usage charts
    st.markdown("<div class='sub-header'>System Usage Analytics</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        dates = [datetime.now().strftime("%b %d") for _ in range(7)]

        # Daily usage chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=st.session_state.usage_data['daily_queries'],
            mode='lines+markers',
            name='Queries',
            line=dict(color='#2563EB', width=3),
            marker=dict(size=8, color='#1E40AF')
        ))

        fig.update_layout(
            title="Daily Tutor Interactions",
            xaxis_title="Date",
            yaxis_title="Number of Queries",
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1E293B')
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # Critical thinking improvement chart
        fig = go.Figure()

        before = st.session_state.critical_thinking_scores['before']
        after = st.session_state.critical_thinking_scores['after']

        # Calculate average improvement
        avg_before = sum(before) / len(before)
        avg_after = sum(after) / len(after)
        improvement = round(((avg_after - avg_before) / avg_before) * 100, 1)

        fig.add_trace(go.Box(
            y=before,
            name='Before EngE-AI',
            marker_color='#BFDBFE',
            boxmean=True
        ))

        fig.add_trace(go.Box(
            y=after,
            name='After EngE-AI',
            marker_color='#3B82F6',
            boxmean=True
        ))

        fig.update_layout(
            title=f"Critical Thinking Assessment Scores (↑ {improvement}%)",
            yaxis_title="Score",
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1E293B')
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Course engagement section
    st.markdown("<div class='sub-header'>Course Engagement by Module</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # Course modules and their engagement data
    modules = [
        "Module 1: Fundamentals",
        "Module 2: First Law",
        "Module 3: Second Law",
        "Module 4: Phase Equilibria",
        "Module 5: Reaction Equilibria"
    ]

    engagement = [85, 92, 78, 65, 70]
    tutor_usage = [120, 145, 105, 90, 80]
    scenarios = [12, 15, 8, 7, 6]

    # Create course engagement chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=modules,
        y=engagement,
        name='Student Engagement (%)',
        marker_color='#3B82F6'
    ))

    fig.add_trace(go.Bar(
        x=modules,
        y=tutor_usage,
        name='Tutor Interactions',
        marker_color='#60A5FA',
        visible='legendonly'
    ))

    fig.add_trace(go.Bar(
        x=modules,
        y=scenarios,
        name='Scenarios Generated',
        marker_color='#93C5FD',
        visible='legendonly'
    ))

    fig.update_layout(
        barmode='group',
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1E293B'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Recent activity and system status
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<div class='sub-header'>Recent Activity</div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # Sample recent activities
        activities = [
            {"time": "10:23 AM", "user": "Student 173", "action": "Completed a critical thinking exercise in Module 3"},
            {"time": "09:48 AM", "user": "Prof. Johnson", "action": "Generated 3 new scenario problems for Module 2"},
            {"time": "09:15 AM", "user": "Student 042", "action": "Asked 5 questions about phase equilibria concepts"},
            {"time": "Yesterday", "user": "Student 108", "action": "Improved critical thinking score by 18%"},
            {"time": "Yesterday", "user": "Prof. Chen", "action": "Updated system prompts for thermodynamics tutor"}
        ]

        for activity in activities:
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <div style="color: #64748B; width: 80px;">{activity['time']}</div>
                <div style="font-weight: 500; width: 120px;">{activity['user']}</div>
                <div style="flex-grow: 1;">{activity['action']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='sub-header'>System Status</div>", unsafe_allow_html=True)
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # System status metrics
        st.markdown("""
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between;">
                <div>AI Model</div>
                <div style="font-weight: 500; color: #10B981;">Active</div>
            </div>
            <div style="font-size: 0.9rem; color: #64748B;">llama2-7b</div>
        </div>

        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between;">
                <div>Response Time</div>
                <div style="font-weight: 500; color: #10B981;">2.4s avg</div>
            </div>
            <div style="font-size: 0.9rem; color: #64748B;">Last 24 hours</div>
        </div>

        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between;">
                <div>System Load</div>
                <div style="font-weight: 500; color: #10B981;">32%</div>
            </div>
            <div style="font-size: 0.9rem; color: #64748B;">Normal operation</div>
        </div>

        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between;">
                <div>Database</div>
                <div style="font-weight: 500; color: #10B981;">Connected</div>
            </div>
            <div style="font-size: 0.9rem; color: #64748B;">Last sync: 5 min ago</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# Virtual Tutor interface
def display_virtual_tutor(tutor):
    st.markdown("<div class='sub-header'>Virtual Engineering Tutor</div>", unsafe_allow_html=True)

    # Course information
    st.markdown(f"""
    <div class="card">
        <h3 style="margin-top: 0;">{st.session_state.selected_course}</h3>
        <p>Ask questions about course concepts, problem-solving strategies, or request help with specific topics. The AI tutor adapts to your learning style and promotes critical thinking.</p>
    </div>
    """, unsafe_allow_html=True)

    # Chat interface
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <div style="font-weight: 500; margin-bottom: 5px;">You</div>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message ai-message">
                <div style="font-weight: 500; margin-bottom: 5px;">EngE-AI Tutor</div>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

    # Input area
    user_input = st.text_area("Your question:", height=100)

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("Send", use_container_width=True):
            if user_input:
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": user_input})

                # Get response from tutor model
                with st.spinner("EngE-AI is thinking..."):
                    response = tutor.answer_question(
                        user_input,
                        mode="general"  # Removed the 'course' parameter
                    )

                # Add AI response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})

                # Rerun to refresh the chat display
                st.rerun()

    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    # Suggested questions
    st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight: 500; margin-bottom: 10px;'>Suggested questions:</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    sample_questions = [
        "Explain the second law of thermodynamics with real-world examples",
        "How do I solve problems involving phase equilibria?",
        "What's the relationship between Gibbs free energy and spontaneity?",
        "Can you explain entropy in simple terms?",
        "How do I apply the first law to open systems?",
        "What are practical applications of the Carnot cycle?"
    ]

    with col1:
        for q in sample_questions[:2]:
            if st.button(q, key=f"q_{sample_questions.index(q)}", use_container_width=True):
                # Set as user input and trigger the same flow as pressing Send
                st.session_state.chat_history.append({"role": "user", "content": q})
                with st.spinner("EngE-AI is thinking..."):
                    response = tutor.answer_question(
                        q,
                        mode="general"  # Removed the 'course' parameter
                    )
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

    with col2:
        for q in sample_questions[2:4]:
            if st.button(q, key=f"q_{sample_questions.index(q)}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": q})
                with st.spinner("EngE-AI is thinking..."):
                    response = tutor.answer_question(
                        q,
                        mode="general"  # Removed the 'course' parameter
                    )
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

    with col3:
        for q in sample_questions[4:]:
            if st.button(q, key=f"q_{sample_questions.index(q)}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": q})
                with st.spinner("EngE-AI is thinking..."):
                    response = tutor.answer_question(
                        q,
                        mode="general"  # Removed the 'course' parameter
                    )
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Scenario Generator interface
def display_scenario_generator(scenario_gen):
    st.markdown("<div class='sub-header'>Engineering Scenario Generator</div>", unsafe_allow_html=True)

    # Introduction card
    st.markdown("""
    <div class="card">
        <h3 style="margin-top: 0;">Create Real-World Engineering Scenarios</h3>
        <p>Generate contextually rich, realistic engineering problems that promote critical thinking and connect abstract concepts to practical applications. These scenarios can be directly incorporated into course materials, assignments, or exams.</p>
    </div>
    """, unsafe_allow_html=True)

    # Scenario generator controls
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<p style='font-weight: 500;'>Scenario Parameters</p>", unsafe_allow_html=True)

        # Topic selection
        topic_options = {
            "CHBE 220 - Chemical Engineering Thermodynamics": [
                "First Law of Thermodynamics",
                "Second Law of Thermodynamics",
                "Thermodynamic Cycles",
                "Phase Equilibria",
                "Chemical Reaction Equilibria"
            ],
            "CHBE 241 - Material and Energy Balances": [
                "Mass Balances",
                "Energy Balances",
                "Reactive Systems",
                "Multiple Unit Operations",
                "Recycle Streams"
            ],
            "CHBE 262 - Environmental Engineering": [
                "Air Pollution Control",
                "Water Treatment",
                "Solid Waste Management",
                "Environmental Impact Assessment",
                "Sustainability Analysis"
            ]
        }

        # Get topics based on selected course
        selected_course = st.session_state.selected_course
        topics = topic_options.get(selected_course, topic_options["CHBE 220 - Chemical Engineering Thermodynamics"])

        topic = st.selectbox("Topic Area", topics)

        # Difficulty level
        difficulty = st.select_slider(
            "Difficulty Level",
            options=["Introductory", "Intermediate", "Challenging", "Advanced"],
            value="Intermediate"
        )

        # Problem type
        problem_type = st.radio(
            "Problem Type",
            ["Conceptual Understanding", "Numerical Analysis", "Design Challenge", "Case Study"]
        )

        # Industry context
        industry = st.selectbox(
            "Industry Context",
            ["Oil & Gas", "Pharmaceuticals", "Food Processing", "Environmental", "Materials Science", "Biotechnology"]
        )

    with col2:
        st.markdown("<p style='font-weight: 500;'>Learning Objectives</p>", unsafe_allow_html=True)

        # Learning objectives and skills to target
        critical_thinking = st.checkbox("Promote Critical Thinking", value=True)
        problem_solving = st.checkbox("Enhance Problem-Solving", value=True)
        real_world = st.checkbox("Connect to Real-World Applications", value=True)
        interdisciplinary = st.checkbox("Encourage Interdisciplinary Thinking", value=False)

        st.markdown("<p style='font-weight: 500; margin-top: 20px;'>Output Format</p>", unsafe_allow_html=True)

        # Output format options
        include_solution = st.checkbox("Include Detailed Solution", value=True)
        include_rubric = st.checkbox("Include Grading Rubric", value=False)
        include_variations = st.checkbox("Generate Problem Variations", value=False)

        st.markdown("<p style='font-weight: 500; margin-top: 20px;'>Additional Instructions (Optional)</p>",
                    unsafe_allow_html=True)

        # Custom instructions
        custom_instructions = st.text_area("",
                                           placeholder="Any specific requirements or constraints for the scenario...")

    # Generate button
    if st.button("Generate Engineering Scenario", use_container_width=True):
        with st.spinner("Creating engineering scenario... This may take a moment."):
            # Construct prompt from all parameters
            prompt = f"""
            Generate a {difficulty} level {problem_type} for {topic} in {st.session_state.selected_course}.
            Industry Context: {industry}

            Learning Objectives:
            {', '.join([obj for obj, checked in zip(["Promote Critical Thinking", "Enhance Problem-Solving", "Connect to Real-World Applications", "Encourage Interdisciplinary Thinking"], [critical_thinking, problem_solving, real_world, interdisciplinary]) if checked])}

            Include:
            {', '.join([item for item, checked in zip(["Detailed Solution", "Grading Rubric", "Problem Variations"], [include_solution, include_rubric, include_variations]) if checked])}

            Additional Instructions:
            {custom_instructions}
            """

            # Generate scenario with the model
            scenario = scenario_gen.generate_scenario(prompt)

            # Add to session state
            st.session_state.scenarios.append({
                "topic": topic,
                "difficulty": difficulty,
                "type": problem_type,
                "industry": industry,
                "content": scenario,
                "created": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

    # Display previously generated scenarios
    if st.session_state.scenarios:
        st.markdown("<div style='margin-top: 30px;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-weight: 500; font-size: 1.2rem;'>Generated Scenarios</p>", unsafe_allow_html=True)

        for i, scenario in enumerate(st.session_state.scenarios):
            with st.expander(f"{scenario['topic']} - {scenario['difficulty']} ({scenario['created']})"):
                st.markdown(f"**Industry Context:** {scenario['industry']}")
                st.markdown(f"**Problem Type:** {scenario['type']}")
                st.markdown(scenario['content'])

                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("Export as PDF", key=f"export_{i}"):
                        st.info("Export functionality would be implemented here.")
                with col2:
                    if st.button("Save to Database", key=f"save_{i}"):
                        st.success("Scenario saved to database.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Critical Thinking Assessment interface
def display_critical_thinking():
    st.markdown("<div class='sub-header'>Critical Thinking Assessment</div>", unsafe_allow_html=True)

    # Introduction card
    st.markdown("""
    <div class="card">
        <h3 style="margin-top: 0;">Measure Critical Thinking Development</h3>
        <p>Track and assess students' critical thinking skills across multiple dimensions. This tool helps measure the impact of EngE-AI on developing higher-order cognitive abilities.</p>
    </div>
    """, unsafe_allow_html=True)

    # Assessment tabs
    tab1, tab2, tab3 = st.tabs(["Assessment Overview", "Question Bank", "Student Results"])

    with tab1:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

        # Summary metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">15.2%</div>
                <div class="metric-label">Average Score Improvement</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">78.5</div>
                <div class="metric-label">Average Post-Assessment Score</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">82%</div>
                <div class="metric-label">Students Showing Improvement</div>
            </div>
            """, unsafe_allow_html=True)

        # Score distribution chart
        st.markdown("<div class='card' style='margin-top: 20px;'>", unsafe_allow_html=True)

        # Create data frame for pre and post scores
        scores_df = pd.DataFrame({
            'Student': [f'S{i:03d}' for i in range(1, 11)],
            'Pre-Assessment': st.session_state.critical_thinking_scores['before'],
            'Post-Assessment': st.session_state.critical_thinking_scores['after']
        })

        # Calculate improvement
        scores_df['Improvement'] = scores_df['Post-Assessment'] - scores_df['Pre-Assessment']

        # Melt the dataframe for easier plotting
        scores_long = pd.melt(
            scores_df,
            id_vars=['Student'],
            value_vars=['Pre-Assessment', 'Post-Assessment'],
            var_name='Assessment',
            value_name='Score'
        )

        # Plot score distribution
        fig = px.bar(
            scores_long,
            x='Student',
            y='Score',
            color='Assessment',
            barmode='group',
            color_discrete_map={'Pre-Assessment': '#BFDBFE', 'Post-Assessment': '#3B82F6'},
            labels={'Score': 'Critical Thinking Score', 'Student': 'Student ID'},
            height=400
        )

        fig.update_layout(
            title="Pre & Post Assessment Score Comparison",
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1E293B'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Dimension breakdown chart
        st.markdown("<div class='card' style='margin-top: 20px;'>", unsafe_allow_html=True)

        # Sample data for dimension breakdown
        dimensions = st.session_state.system_settings['critical_thinking_dimensions']
        pre_scores = [65, 62, 70, 64, 68]
        post_scores = [78, 75, 82, 76, 80]

        # Create dataframe for dimensions
        dim_df = pd.DataFrame({
            'Dimension': dimensions,
            'Pre-Assessment': pre_scores,
            'Post-Assessment': post_scores
        })

        # Calculate improvement for each dimension
        dim_df['Improvement'] = dim_df['Post-Assessment'] - dim_df['Pre-Assessment']

        # Create radar chart
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=dim_df['Pre-Assessment'],
            theta=dim_df['Dimension'],
            fill='toself',
            name='Pre-Assessment',
            line_color='#BFDBFE',
            fillcolor='rgba(191, 219, 254, 0.5)'
        ))

        fig.add_trace(go.Scatterpolar(
            r=dim_df['Post-Assessment'],
            theta=dim_df['Dimension'],
            fill='toself',
            name='Post-Assessment',
            line_color='#3B82F6',
            fillcolor='rgba(59, 130, 246, 0.5)'
        ))

        fig.update_layout(
            title="Critical Thinking by Dimension",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[50, 100]
                )
            ),
            height=450,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1E293B'),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

        # Question bank display
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # Add new question form
        with st.expander("Add New Assessment Question"):
            col1, col2 = st.columns(2)

            with col1:
                new_question = st.text_area("Question", placeholder="Enter question text...")
                dimension = st.selectbox("Critical Thinking Dimension", st.session_state.system_settings["critical_thinking_dimensions"])

            with col2:
                points = st.number_input("Points", min_value=1, max_value=20, value=10)
                st.text_area("Grading Criteria", placeholder="Enter grading criteria...")

            if st.button("Add Question to Bank"):
                st.success("Question added successfully!")

        # Display existing questions
        st.markdown("<p style='font-weight: 500; font-size: 1.1rem; margin-top: 20px;'>Existing Assessment Questions</p>", unsafe_allow_html=True)

        for q in st.session_state.assessment_questions:
            st.markdown(f"""
            <div style="border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between;">
                    <div style="font-weight: 500;">Question {q['id']}</div>
                    <div style="color: #3B82F6;">{q['dimension']} • {q['points']} points</div>
                </div>
                <div style="margin-top: 10px;">{q['question']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Assessment creation
        st.markdown("<div style='margin-top: 30px;'>", unsafe_allow_html=True)
        st.markdown("<p style='font-weight: 500; font-size: 1.1rem;'>Create Assessment</p>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            assessment_name = st.text_input("Assessment Name", "Critical Thinking Assessment - March 2025")
            st.multiselect("Select Questions", [f"Q{q['id']}: {q['question'][:50]}..." for q in st.session_state.assessment_questions], default=[f"Q{q['id']}: {q['question'][:50]}..." for q in st.session_state.assessment_questions[:3]])

        with col2:
            st.selectbox("Target Course", [st.session_state.selected_course] + ["CHBE 241 - Material and Energy Balances", "CHBE 262 - Environmental Engineering"])
            st.number_input("Time Limit (minutes)", min_value=30, max_value=180, value=60, step=15)

        if st.button("Create Assessment", use_container_width=True):
            st.success("Assessment created successfully!")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

        # Student results display
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # Create a DataFrame for student results
        student_df = pd.DataFrame(st.session_state.student_assessments)

        # Display as a table
        st.dataframe(
            student_df,
            column_config={
                "student_id": "Student ID",
                "name": "Name",
                "pre_score": "Pre-Score",
                "post_score": "Post-Score",
                "improvement": st.column_config.NumberColumn(
                    "Improvement",
                    format="%.1f ↑",
                ),
                "strongest_dimension": "Strongest Area",
                "weakest_dimension": "Needs Improvement",
                "date_completed": "Completed"
            },
            hide_index=True,
            use_container_width=True
        )

        # Individual student detailed view
        st.markdown("<p style='font-weight: 500; font-size: 1.1rem; margin-top: 20px;'>Student Detailed View</p>", unsafe_allow_html=True)

        selected_student = st.selectbox("Select Student", [f"{s['student_id']} - {s['name']}" for s in st.session_state.student_assessments])

        # Get student details
        student_id = selected_student.split(" - ")[0]
        student_data = next((s for s in st.session_state.student_assessments if s["student_id"] == student_id), None)

        if student_data:
            # Student performance chart
            dimensions = st.session_state.system_settings["critical_thinking_dimensions"]

            # Sample dimension scores for the selected student
            pre_dim_scores = [65, 60, 70, 62, 68]
            post_dim_scores = [78, 75, 80, 76, 82]

            # Create a dataframe for the student's dimension scores
            student_dims = pd.DataFrame({
                "Dimension": dimensions,
                "Pre-Assessment": pre_dim_scores,
                "Post-Assessment": post_dim_scores
            })

            # Calculate improvement
            student_dims["Improvement"] = student_dims["Post-Assessment"] - student_dims["Pre-Assessment"]

            # Create bar chart
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=student_dims["Dimension"],
                y=student_dims["Pre-Assessment"],
                name="Pre-Assessment",
                marker_color="#BFDBFE"
            ))

            fig.add_trace(go.Bar(
                x=student_dims["Dimension"],
                y=student_dims["Post-Assessment"],
                name="Post-Assessment",
                marker_color="#3B82F6"
            ))

            fig.update_layout(
                title=f"Critical Thinking Development: {student_data['name']}",
                barmode="group",
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#1E293B'),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            # Student feedback and recommendations
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("<div style='border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px;'>", unsafe_allow_html=True)
                st.markdown("<p style='font-weight: 500; margin-bottom: 10px;'>Strengths</p>", unsafe_allow_html=True)
                st.markdown(f"""
                <ul style='margin-top: 0; padding-left: 20px;'>
                    <li>Strong performance in {student_data['strongest_dimension']} with score improvement of {max(student_dims['Improvement']):.1f} points</li>
                    <li>Overall score improvement of {student_data['improvement']} points (20% increase)</li>
                    <li>Effective application of theoretical concepts to practical scenarios</li>
                </ul>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("<div style='border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px;'>", unsafe_allow_html=True)
                st.markdown("<p style='font-weight: 500; margin-bottom: 10px;'>Areas for Growth</p>", unsafe_allow_html=True)
                st.markdown(f"""
                <ul style='margin-top: 0; padding-left: 20px;'>
                    <li>Additional practice needed in {student_data['weakest_dimension']}</li>
                    <li>More focus on identifying assumptions and biases in problem statements</li>
                    <li>Further development of interdisciplinary connections</li>
                </ul>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # Recommendations
            st.markdown("<div style='margin-top: 15px; border: 1px solid #E2E8F0; border-radius: 8px; padding: 15px;'>", unsafe_allow_html=True)
            st.markdown("<p style='font-weight: 500; margin-bottom: 10px;'>Recommended Activities</p>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <div style="font-weight: 500;">Virtual Tutor Sessions</div>
                    <div style="font-size: 0.9rem; color: #64748B;">3 sessions focused on {student_data['weakest_dimension']}</div>
                </div>

                <div style="margin-bottom: 10px;">
                    <div style="font-weight: 500;">Interactive Case Studies</div>
                    <div style="font-size: 0.9rem; color: #64748B;">Waste heat recovery in chemical plants</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <div style="font-weight: 500;">Practice Scenarios</div>
                    <div style="font-size: 0.9rem; color: #64748B;">4 scenarios with focused feedback</div>
                </div>

                <div>
                    <div style="font-weight: 500;">Peer Collaboration</div>
                    <div style="font-size: 0.9rem; color: #64748B;">Group problem-solving with other students</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Settings page
def display_settings():
    st.markdown("<div class='sub-header'>System Settings</div>", unsafe_allow_html=True)

    # Settings card
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # Tabs for different settings categories
    tab1, tab2, tab3, tab4 = st.tabs(["AI Model Settings", "Assessment Configuration", "System Integration", "User Management"])

    with tab1:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

        # AI model settings
        col1, col2 = st.columns(2)

        with col1:
            st.selectbox("Default AI Model", ["llama3.2", "mistral"], index=0)
            st.slider("Temperature", min_value=0.1, max_value=1.0, value=0.7, step=0.1)
            st.slider("Max Tokens", min_value=256, max_value=4096, value=1024, step=256)

        with col2:
            st.selectbox("Backup Model (Fallback)", ["llama3.2", "mistral"], index=1)
            st.number_input("Response Timeout (seconds)", min_value=10, max_value=120, value=30, step=5)
            st.selectbox("Model Hosting", ["Local (Ollama)", "API Service", "Hybrid"], index=0)

        # Advanced settings
        st.markdown("<p style='font-weight: 500; margin-top: 20px;'>Advanced Settings</p>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.text_area("System Prompt Prefix",
                         """You are EngE-AI, an engineering education assistant designed to help students develop critical thinking skills. Focus on guiding students to solutions rather than providing answers directly.""",
                         height=100)
            st.checkbox("Use Chain-of-Thought Prompting", value=True)

        with col2:
            st.number_input("Rate Limit (queries per minute)", min_value=5, max_value=60, value=20, step=5)
            st.checkbox("Enforce Content Safety Filters", value=True)
            st.checkbox("Log All Interactions", value=True)

        if st.button("Save AI Model Settings", use_container_width=True):
            st.success("AI model settings saved successfully!")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

        # Critical thinking dimensions
        st.markdown("<p style='font-weight: 500;'>Critical Thinking Dimensions</p>", unsafe_allow_html=True)

        dimensions = st.session_state.system_settings["critical_thinking_dimensions"]
        for i, dim in enumerate(dimensions):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text_input(f"Dimension {i+1}", dim, key=f"dim_{i}")
            with col2:
                st.selectbox("Weight", ["High", "Medium", "Low"], index=0, key=f"weight_{i}")

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("+ Add", use_container_width=True):
                st.info("New dimension would be added here.")

        # Assessment settings
        st.markdown("<p style='font-weight: 500; margin-top: 20px;'>Assessment Settings</p>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.selectbox("Assessment Frequency", ["Weekly", "Bi-weekly", "Monthly", "Start/End of Term"], index=3)
            st.number_input("Minimum Questions per Assessment", min_value=3, max_value=15, value=5)

        with col2:
            st.selectbox("Scoring Method", ["Numeric (0-100)", "Rubric Based", "Dimensional Analysis"], index=0)
            st.checkbox("Require Written Justification", value=True)

        st.markdown("<p style='font-weight: 500; margin-top: 20px;'>Rubric Configuration</p>", unsafe_allow_html=True)

        rubric_levels = [
            {"name": "Exemplary", "description": "Demonstrates exceptional critical thinking with comprehensive analysis and creative solutions", "score_range": "85-100"},
            {"name": "Proficient", "description": "Shows solid critical thinking with good analysis and reasonable solutions", "score_range": "70-84"},
            {"name": "Developing", "description": "Shows basic critical thinking with partial analysis and some viable solutions", "score_range": "60-69"},
            {"name": "Beginning", "description": "Shows minimal critical thinking with superficial analysis and limited solutions", "score_range": "0-59"}
        ]

        for level in rubric_levels:
            st.markdown(f"""
            <div style="display: flex; margin-bottom: 10px; border: 1px solid #E2E8F0; border-radius: 5px; padding: 10px;">
                <div style="font-weight: 500; width: 120px;">{level['name']}</div>
                <div style="flex-grow: 1;">{level['description']}</div>
                <div style="width: 80px; text-align: right;">{level['score_range']}</div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("Save Assessment Configuration", use_container_width=True):
            st.success("Assessment configuration saved successfully!")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

        # System integration settings
        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Database Connection String", st.session_state.system_settings["database_connection"])
            st.selectbox("Database Type", ["MongoDB", "PostgreSQL", "SQLite", "MySQL"], index=0)
            st.text_input("API Key", st.session_state.system_settings["api_key"], type="password")

        with col2:
            st.selectbox("Backup Frequency", ["Hourly", "Daily", "Weekly", "Monthly"], index=1)
            st.text_input("Backup Location", "/srv/data/engai/backups")
            st.selectbox("Integration Mode", ["Standalone", "LMS Integration", "API Service"], index=0)

        # LMS integration
        st.markdown("<p style='font-weight: 500; margin-top: 20px;'>Learning Management System Integration</p>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.selectbox("LMS Platform", ["Canvas", "Moodle", "Blackboard", "D2L Brightspace", "None"], index=4)
            st.text_input("LMS API Endpoint", "https://canvas.ubc.ca/api/v1")

        with col2:
            st.text_input("LMS API Key", "lms_api_xxxxxxxxxxxxx", type="password")
            st.multiselect("Data to Sync", ["Grades", "Assignments", "Student Roster", "Course Materials"], default=[])

        # Analytics & logging
        st.markdown("<p style='font-weight: 500; margin-top: 20px;'>Analytics & Logging</p>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.checkbox("Collect Usage Analytics", value=True)
            st.checkbox("Log Student Interactions", value=True)
            st.checkbox("Performance Monitoring", value=True)

        with col2:
            st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"], index=1)
            st.text_input("Log File Path", "/var/log/engai/")
            st.checkbox("Enable GDPR Compliance Mode", value=True)

        if st.button("Save System Integration Settings", use_container_width=True):
            st.success("System integration settings saved successfully!")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)

        # User management
        st.markdown("<p style='font-weight: 500;'>User Roles & Permissions</p>", unsafe_allow_html=True)

        roles = [
            {"role": "Administrator", "description": "Full system access", "users": 2},
            {"role": "Instructor", "description": "Course management, scenario creation, assessment access", "users": 5},
            {"role": "Teaching Assistant", "description": "Student assistance, limited assessment access", "users": 12},
            {"role": "Student", "description": "Virtual tutor access, scenario practice", "users": 254}
        ]

        # Role management
        for role in roles:
            col1, col2, col3 = st.columns([2, 5, 1])
            with col1:
                st.markdown(f"""<div style="font-weight: 500;">{role['role']}</div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""{role['description']}""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""{role['users']} users""", unsafe_allow_html=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # User import/export
        col1, col2 = st.columns(2)
        with col1:
            st.file_uploader("Import Users from CSV", type=["csv"])
        with col2:
            st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
            st.button("Export Users", use_container_width=True)

        # Single user management
        st.markdown("<p style='font-weight: 500; margin-top: 20px;'>User Management</p>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.text_input("Email", "user@example.com")
        with col2:
            st.selectbox("Role", ["Administrator", "Instructor", "Teaching Assistant", "Student"], index=3)
        with col3:
            st.button("Add User", use_container_width=True)

        # Security settings
        st.markdown("<p style='font-weight: 500; margin-top: 20px;'>Security Settings</p>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Require Two-Factor Authentication for Admins", value=True)
            st.number_input("Session Timeout (minutes)", min_value=15, max_value=240, value=60, step=15)
        with col2:
            st.checkbox("Enforce Strong Password Policy", value=True)
            st.checkbox("Allow Single Sign-On (SSO)", value=True)

        if st.button("Save User Management Settings", use_container_width=True):
            st.success("User management settings saved successfully!")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
