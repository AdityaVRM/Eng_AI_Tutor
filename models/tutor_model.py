import os
import logging
import json
from typing import List, Dict, Any, Optional
import pandas as pd
from utils.prompt_templates import TutorPromptTemplates
from utils.prompt_templates import ScenarioPromptTemplates

logger = logging.getLogger("EngE-AI.tutor")


class EngineeringTutor:
    """
    Virtual tutor implementation for engineering education
    focused on Chemical and Biological Engineering concepts
    """

    def __init__(self, ollama_manager, course_data_path="database/course_data"):
        """
        Initialize the engineering tutor with course-specific knowledge

        Args:
            ollama_manager: Instance of OllamaManager for LLM interaction
            course_data_path (str): Path to course data files
        """
        self.ollama = ollama_manager
        self.course_data_path = course_data_path
        self.templates = TutorPromptTemplates()
        self.ct_framework = CriticalThinkingFramework()
        self.course_data = self._load_course_data()
        self.conversation_history = []

    def _load_course_data(self) -> Dict[str, Any]:
        """Load course-specific data from files"""
        course_data = {}

        try:
            # Load course topics and concepts
            topics_path = os.path.join(self.course_data_path, "topics.json")
            if os.path.exists(topics_path):
                with open(topics_path, "r") as f:
                    course_data["topics"] = json.load(f)

            # Load problem sets
            problems_path = os.path.join(self.course_data_path, "problems.json")
            if os.path.exists(problems_path):
                with open(problems_path, "r") as f:
                    course_data["problems"] = json.load(f)

            # Load learning objectives
            objectives_path = os.path.join(self.course_data_path, "learning_objectives.json")
            if os.path.exists(objectives_path):
                with open(objectives_path, "r") as f:
                    course_data["objectives"] = json.load(f)

            logger.info(f"Loaded course data with {len(course_data.get('topics', []))} topics")
            return course_data

        except Exception as e:
            logger.error(f"Error loading course data: {str(e)}")
            return {"topics": [], "problems": [], "objectives": []}

    def get_system_prompt(self, mode="general") -> str:
        """
        Get appropriate system prompt based on interaction mode

        Args:
            mode (str): Interaction mode ('general', 'concept_explanation',
                        'problem_solving', 'critical_thinking')

        Returns:
            str: System prompt for the LLM
        """
        if mode == "concept_explanation":
            return self.templates.concept_explanation_prompt
        elif mode == "problem_solving":
            return self.templates.problem_solving_prompt
        elif mode == "critical_thinking":
            return self.templates.critical_thinking_prompt
        else:  # general mode
            return self.templates.general_tutor_prompt

    def answer_question(self, question: str, mode="general",
                        include_critical_thinking=True) -> str:
        """
        Answer a student's question using the appropriate mode

        Args:
            question (str): The student's question
            mode (str): Interaction mode
            include_critical_thinking (bool): Whether to incorporate critical thinking prompts

        Returns:
            str: Tutor's response
        """
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": question})

        # Get appropriate system prompt
        system_prompt = self.get_system_prompt(mode)

        # If critical thinking is enabled, enhance the system prompt
        if include_critical_thinking and mode != "critical_thinking":
            ct_enhancement = self.ct_framework.get_enhancement_prompt()
            system_prompt = f"{system_prompt}\n\n{ct_enhancement}"

        # Prepare full conversation history for context
        messages = [{"role": "system", "content": system_prompt}] + self.conversation_history

        # Generate response
        response = self.ollama.chat(messages)

        # Add to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    def guide_critical_thinking(self, problem: str, thinking_stage: str) -> str:
        """
        Guide students through critical thinking stages

        Args:
            problem (str): The problem or scenario to analyze
            thinking_stage (str): Current stage of critical thinking
                                 ('identify', 'analyze', 'evaluate', 'create')

        Returns:
            str: Guidance appropriate for the current thinking stage
        """
        # Get critical thinking prompt for specific stage
        ct_prompt = self.ct_framework.get_stage_prompt(thinking_stage)

        # Prepare the problem context with stage-specific prompt
        context = f"Problem: {problem}\n\nStage: {thinking_stage}\n\n{ct_prompt}"

        # Get general critical thinking system prompt
        system_prompt = self.get_system_prompt(mode="critical_thinking")

        # Generate guidance
        response = self.ollama.generate_response(
            prompt=context,
            system_prompt=system_prompt
        )

        return response

    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
        logger.info("Conversation history reset")