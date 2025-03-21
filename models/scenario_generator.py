import os
import json
import logging
import random
from typing import List, Dict, Any, Optional
import pandas as pd

logger = logging.getLogger("EngE-AI.scenario")


class ScenarioGenerator:
    """
    Real-world scenario generator for engineering education
    that creates context-rich problem statements
    """

    def __init__(self, ollama_manager, templates_path="database/scenario_templates"):
        """
        Initialize the scenario generator

        Args:
            ollama_manager: Instance of OllamaManager for LLM interaction
            templates_path (str): Path to scenario templates
        """
        self.ollama = ollama_manager
        self.templates_path = templates_path
        self.scenario_templates = self._load_templates()
        self.generated_scenarios = []

    def _load_templates(self) -> Dict[str, Any]:
        """Load scenario templates from files"""
        templates = {}

        try:
            # Load industry templates
            industry_path = os.path.join(self.templates_path, "industry_contexts.json")
            if os.path.exists(industry_path):
                with open(industry_path, "r") as f:
                    templates["industry"] = json.load(f)

            # Load problem formats
            formats_path = os.path.join(self.templates_path, "problem_formats.json")
            if os.path.exists(formats_path):
                with open(formats_path, "r") as f:
                    templates["formats"] = json.load(f)

            # Load chemical engineering templates
            chem_path = os.path.join(self.templates_path, "chemical_engineering.json")
            if os.path.exists(chem_path):
                with open(chem_path, "r") as f:
                    templates["chemical"] = json.load(f)

            logger.info(f"Loaded scenario templates successfully")
            return templates

        except Exception as e:
            logger.error(f"Error loading scenario templates: {str(e)}")
            return {"industry": [], "formats": [], "chemical": []}

    def generate_scenario(self,
                          topic: str,
                          difficulty: str = "moderate",
                          scenario_type: str = "open_ended",
                          industry_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a context-rich engineering scenario

        Args:
            topic (str): Engineering topic to focus on
            difficulty (str): Difficulty level ("basic", "moderate", "advanced")
            scenario_type (str): Type of scenario ("calculation", "design", "analysis", "open_ended")
            industry_context (str, optional): Specific industry context

        Returns:
            dict: Generated scenario with metadata
        """
        # Select industry context if not specified
        if not industry_context and self.scenario_templates.get("industry"):
            industry_context = random.choice(self.scenario_templates["industry"])

        # Build the scenario generation prompt
        system_prompt = f"""You are an expert Chemical and Biological Engineering educator. 
Create a realistic, context-rich engineering scenario for undergraduate students that:
1. Focuses on the topic: {topic}
2. Has {difficulty} difficulty level
3. Is structured as a {scenario_type} problem
4. Is situated in the {industry_context} industry
5. Requires critical thinking to solve
6. Includes realistic constraints, data, and background information
7. Is structured with: Context, Problem Statement, Available Data, and Expected Deliverables
8. Does NOT include the solution"""

        # User prompt to specify what we want
        user_prompt = f"""Generate a complete engineering scenario for a second-year Chemical Engineering course.
Topic: {topic}
Difficulty: {difficulty}
Type: {scenario_type}
Industry: {industry_context}

Include appropriate technical details, realistic values, and industry-specific terminology.
The scenario should challenge students to apply critical thinking skills while being appropriate for second-year undergraduates.
"""

        # Generate the scenario
        scenario_text = self.ollama.generate_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.8
        )

        # Create scenario object with metadata
        scenario = {
            "scenario_text": scenario_text,
            "metadata": {
                "topic": topic,
                "difficulty": difficulty,
                "type": scenario_type,
                "industry": industry_context,
                "generated_timestamp": pd.Timestamp.now().isoformat(),
            }
        }

        # Add to history
        self.generated_scenarios.append(scenario)

        return scenario

    def generate_variations(self, base_scenario: Dict[str, Any], num_variations: int = 3) -> List[Dict[str, Any]]:
        """
        Generate variations of a base scenario with different parameters

        Args:
            base_scenario (dict): Base scenario to create variations from
            num_variations (int): Number of variations to generate

        Returns:
            list: List of scenario variations
        """
        variations = []

        # Extract base metadata
        metadata = base_scenario.get("metadata", {})
        base_topic = metadata.get("topic", "")
        base_difficulty = metadata.get("difficulty", "moderate")
        base_type = metadata.get("type", "open_ended")

        # Possible variations
        difficulty_levels = ["basic", "moderate", "advanced"]
        scenario_types = ["calculation", "design", "analysis", "open_ended"]

        for i in range(num_variations):
            # Vary the parameters
            if i % 3 == 0:  # Vary difficulty
                new_difficulty = random.choice([d for d in difficulty_levels if d != base_difficulty])
                new_type = base_type
            elif i % 3 == 1:  # Vary type
                new_difficulty = base_difficulty
                new_type = random.choice([t for t in scenario_types if t != base_type])
            else:  # Vary both
                new_difficulty = random.choice([d for d in difficulty_levels if d != base_difficulty])
                new_type = random.choice([t for t in scenario_types if t != base_type])

            # Generate new variant
            variant = self.generate_scenario(
                topic=base_topic,
                difficulty=new_difficulty,
                scenario_type=new_type,
                industry_context=metadata.get("industry")
            )

            # Add variation metadata
            variant["metadata"]["variation_of"] = metadata.get("generated_timestamp")
            variant["metadata"]["variation_type"] = f"Changed difficulty to {new_difficulty} and type to {new_type}"

            variations.append(variant)

        return variations

    def export_scenarios(self, output_file: str = "generated_scenarios.json"):
        """
        Export all generated scenarios to a file

        Args:
            output_file (str): Path to output file
        """
        try:
            with open(output_file, "w") as f:
                json.dump(self.generated_scenarios, f, indent=2)
            logger.info(f"Exported {len(self.generated_scenarios)} scenarios to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting scenarios: {str(e)}")
            return False