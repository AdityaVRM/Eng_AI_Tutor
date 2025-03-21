# EngE-AI: Engineering Education Artificial Intelligence

![EngE-AI Logo](assets/images/logo.png)

## 🧪 Project Overview

EngE-AI (Engineering Education Artificial Intelligence) is a versatile GenAI tool designed to foster critical thinking in undergraduate engineering students. This project focuses on Chemical and Biological Engineering education, with three distinct features:

1. **Virtual Tutor and Chatbot** - Providing course support anywhere, anytime
2. **Real-world Scenario Generator** - Creating context-rich engineering problems
3. **Guided Critical Thinking Framework** - Developing analytical skills systematically

This implementation uses [Ollama](https://github.com/ollama/ollama) to run open-source LLMs locally, ensuring privacy and customization for educational environments.

## 🚀 Features

### Virtual Tutor (Student-Facing)
- Interactive Q&A on chemical engineering concepts
- Step-by-step problem-solving guidance
- Critical thinking prompts based on cognitive frameworks
- Multi-turn conversations with context awareness

### Scenario Generator (Instructor-Facing)
- Creates realistic, context-rich engineering problems
- Customizable difficulty levels and focus areas
- Industry-specific scenarios with authentic constraints
- Variation generation for assignment diversity

### Critical Thinking Framework
- Structured approach to engineering problem-solving
- Progressive stages: Identify, Analyze, Evaluate, Create, Reflect
- Dimension-based assessment: Technical, Practical, Analytical, Creative, Ethical
- Scaffolded questioning techniques

## 📊 Interactive Dashboard

The project includes a Streamlit dashboard with:
- Tutor interface for student interactions
- Scenario generator with customization options
- Analytics on usage patterns and student engagement
- Administrative controls for instructors

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.ai/) installed locally

### Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/enge-ai.git
cd enge-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure Ollama is running and pull the required model:
```bash
ollama pull llama3
```

## 🚦 Usage

1. Start the Streamlit dashboard:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

3. Use the sidebar to navigate between the Tutor and Scenario Generator interfaces

## 📁 Project Structure

```
project_structure/
├── README.md
├── requirements.txt
├── app.py                      # Main Streamlit dashboard
├── ollama_setup.py             # Ollama configuration
├── models/
│   ├── __init__.py
│   ├── tutor_model.py          # Virtual tutor implementation
│   └── scenario_generator.py   # Real-world scenario generator
├── utils/
│   ├── __init__.py
│   ├── prompt_templates.py     # Templates for different use cases
│   ├── critical_thinking.py    # Critical thinking frameworks
│   └── data_processing.py      # Data handling utilities
├── database/
│   ├── __init__.py
│   ├── db_setup.py             # Database initialization
│   └── query_manager.py        # Database operations
├── assets/
│   ├── css/
│   │   └── style.css           # Custom styling
│   └── images/
│       ├── logo.png
│       └── icons/
└── tests/
    ├── __init__.py
    ├── test_tutor.py
    └── test_scenario_gen.py
```

## 🔧 Configuration

The application can be configured through:
- Environment variables (create a `.env` file)
- Command-line arguments
- The admin panel in the Streamlit interface

## 📝 Development Roadmap

**Current Phase (Year 1):**
- ✅ Virtual Tutor implementation
- ✅ Scenario Generator for instructors
- ✅ Basic critical thinking framework
- ✅ Interactive dashboard

**Future Phase (Year 2):**
- Enhanced critical thinking assessment
- Integration with LMS platforms
- Personalized learning paths
- Expanded subject coverage beyond ChemE

## 📚 References

- UBC Chemical and Biological Engineering: [Project Funding Application](https://blogs.ubc.ca/abagherzadeh/summer-job-postings/2025-summer-job-posting/)
- Literature on GenAI in Engineering Education
- Critical Thinking Assessment Frameworks

## 👥 Contributors

- [Your Name](https://github.com/yourusername)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.