from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ConceptType(str, Enum):
    """Types of concepts that can be extracted from papers."""
    ARCHITECTURE = "architecture"
    TECHNIQUE = "technique"
    ALGORITHM = "algorithm"
    METHODOLOGY = "methodology"
    RESULT = "result"
    INNOVATION = "innovation"


class Concept(BaseModel):
    """Represents a key concept from the research paper."""
    id: str
    title: str
    description: str
    concept_type: ConceptType
    page_numbers: List[int] = Field(default_factory=list)
    related_concepts: List[str] = Field(default_factory=list)
    importance_score: float = Field(ge=0.0, le=1.0, default=0.5)
    slide_url: Optional[str] = Field(default=None, description="URL to the generated Manim slides.")
    
    
class DiagramInfo(BaseModel):
    """Information about a diagram or figure in the paper."""
    figure_number: str
    caption: str
    page_number: int
    description: str
    related_concepts: List[str] = Field(default_factory=list)


class Roadmap(BaseModel):
    """Complete roadmap of the research paper."""
    paper_title: str
    paper_summary: str
    concepts: List[Concept]
    diagrams: List[DiagramInfo] = Field(default_factory=list)
    main_contribution: str
    prerequisites: List[str] = Field(default_factory=list)
    
    
class SlideGenerationRequest(BaseModel):
    """Request to generate slides for a concept."""
    concept_id: str
    concept: Concept
    context: Optional[Dict[str, Any]] = None
    output_format: str = "html"  # html or pdf
    
    
class SlideGenerationResult(BaseModel):
    """Result of slide generation."""
    concept_id: str
    slide_path: str
    status: str  # "success", "error", "processing"
    error_message: Optional[str] = None
    preview_url: Optional[str] = None
