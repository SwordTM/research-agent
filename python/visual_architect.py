from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models.storyboard import Storyboard

class VisualArchitectTool:
    def __init__(self, api_key: str = None):
        self.parser = PydanticOutputParser(pydantic_object=Storyboard)
        self.llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1"
        )

    def plan_visuals(self, concept_title: str, concept_description: str) -> Storyboard:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional Motion Graphics Designer and Math Educator.
            Your job is to take a complex research concept and create a step-by-step Storyboard for a Manim animation.
            
            RULES:
            1. Break the concept into 3-5 logical steps.
            2. **LAYOUT REGIONS:** Always specify which region an object belongs to:
                * **Header Zone:** Top 20% (for titles).
                * **Stage Zone:** Center 60% (for the primary diagram or content).
                * **Footer Zone:** Bottom 20% (for captions or secondary labels).
            3. **STAGE SETUP:** For each step, define a "Stage Setup" (e.g., '4 Rectangles representing tokens arranged horizontally in the Stage Zone').
            4. **RELATIVE POSITIONING:** Use instructions like 'Label A placed directly beneath Rectangle A' or 'Arrow originating from the top of Token B'.
            5. Use analogies (e.g., 'Represent neurons as glowing circles').
            6. Ensure each step flows logically into the next.
            
            Example Layout Logic:
            "Position 4 rectangles in a Row in the Stage Zone using relative spacing. Place labels for each rectangle in the Footer Zone, aligned with their respective rectangles."
            
            {format_instructions}"""),
            ("user", "Concept: {title}\nDescription: {description}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "title": concept_title,
            "description": concept_description,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        return self.parser.parse(response.content)