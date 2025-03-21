class CriticalThinkingFramework:
    """
    Framework for structured critical thinking in engineering education
    """

    def __init__(self):
        # Critical thinking stages
        self.stages = {
            "identify": {
                "name": "Identify and Define",
                "description": "Clearly identify the problem, define objectives, and establish boundaries",
                "prompts": [
                    "What is the core problem or challenge here?",
                    "What are the key variables and parameters involved?",
                    "What are the objectives that need to be achieved?",
                    "What assumptions are being made?",
                    "What constraints or limitations must be considered?"
                ]
            },
            "analyze": {
                "name": "Analyze",
                "description": "Break down the problem, gather relevant information, and explore relationships",
                "prompts": [
                    "What fundamental principles or theories apply to this situation?",
                    "How are the variables related to each other?",
                    "What information is needed vs. what is available?",
                    "What methods could be used to analyze this problem?",
                    "How can the problem be broken down into manageable parts?"
                ]
            },
            "evaluate": {
                "name": "Evaluate",
                "description": "Assess potential solutions, consider alternatives, and evaluate trade-offs",
                "prompts": [
                    "What criteria should be used to evaluate potential solutions?",
                    "What are the advantages and disadvantages of each approach?",
                    "How do different solutions perform under varying conditions?",
                    "What are the potential risks or uncertainties?",
                    "How do the solutions address the original objectives?"
                ]
            },
            "create": {
                "name": "Create and Implement",
                "description": "Develop innovative solutions, synthesize ideas, and form implementation plans",
                "prompts": [
                    "How can existing approaches be combined or modified to create new solutions?",
                    "What novel approaches could address this challenge?",
                    "How would the proposed solution be implemented?",
                    "What resources would be required?",
                    "How would you validate that the solution works as intended?"
                ]
            },
            "reflect": {
                "name": "Reflect",
                "description": "Review the process and outcome, consider improvements, and extract lessons learned",
                "prompts": [
                    "What worked well in the problem-solving process?",
                    "What could be improved in the approach?",
                    "How would you verify the accuracy of your solution?",
                    "What have you learned that could apply to future problems?",
                    "What broader implications does this solution have?"
                ]
            }
        }

        # Engineering-specific critical thinking dimensions
        self.dimensions = {
            "technical": "Applying engineering principles, scientific laws, and mathematical models correctly",
            "practical": "Considering real-world constraints, feasibility, and implementation challenges",
            "analytical": "Breaking down complex problems into components and understanding relationships",
            "creative": "Developing innovative approaches and solutions to engineering challenges",
            "ethical": "Evaluating impacts on safety, society, environment, and ethical implications",
            "metacognitive": "Reflecting on the problem-solving process and one's own thinking"
        }

    def get_stage_prompt(self, stage_key):
        """
        Get prompts for a specific critical thinking stage

        Args:
            stage_key (str): Key for the critical thinking stage

        Returns:
            str: Formatted prompts for the requested stage
        """
        stage = self.stages.get(stage_key.lower())
        if not stage:
            return "Stage not found. Available stages: identify, analyze, evaluate, create, reflect."

        # Format the stage information
        prompt = f"# {stage['name']} Stage\n\n"
        prompt += f"{stage['description']}\n\n"
        prompt += "**Guiding Questions:**\n"

        for question in stage['prompts']:
            prompt += f"- {question}\n"

        return prompt

    def get_enhancement_prompt(self):
        """
        Get a prompt to enhance critical thinking in general interactions

        Returns:
            str: Critical thinking enhancement prompt
        """
        prompt = """To foster critical thinking in your responses:

1. Encourage students to question assumptions and identify constraints
2. Ask students to justify their reasoning and provide evidence
3. Present multiple perspectives or approaches when appropriate
4. Guide students to evaluate trade-offs between different solutions
5. Help students connect theoretical concepts to practical applications
6. Challenge students to reflect on their problem-solving process

When students provide answers, ask them to explain their reasoning rather than simply validating correctness."""

        return prompt

    def get_scaffolded_approach(self, topic):
        """
        Generate a scaffolded critical thinking approach for a specific topic

        Args:
            topic (str): Engineering topic to create framework for

        Returns:
            dict: Structured critical thinking framework for the topic
        """
        # This would normally integrate with the LLM to generate
        # topic-specific critical thinking frameworks, but for now
        # we'll return a placeholder

        framework = {
            "topic": topic,
            "stages": []
        }

        # Add each stage with topic context
        for key, stage in self.stages.items():
            framework["stages"].append({
                "name": stage["name"],
                "description": stage["description"],
                "topic_context": f"For {topic}, this means...",
                "prompts": stage["prompts"]
            })

        return framework