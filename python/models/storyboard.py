from typing import List
from pydantic import BaseModel, Field

class SlideStep(BaseModel):
    step_number: int
    visual_description: str = Field(description="Detailed description of what objects appear and how they move.")
    text_content: str = Field(description="The actual text or labels to be shown on screen.")
    layout_logic: str = Field(description="Instructions on positioning (e.g., 'Flowchart on left, bullet points on right').")
    transition_type: str = Field(description="How to move from the previous step (e.g., FadeIn, Transform, Create).")

class Storyboard(BaseModel):
    concept_title: str
    overall_theme: str
    steps: List[SlideStep]