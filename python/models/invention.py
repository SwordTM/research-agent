"""Pydantic models for the Invention Breakdown structure."""

from typing import List, Optional
from pydantic import BaseModel, Field


class InventionBreakdown(BaseModel):
    """A structured breakdown of a research paper's main invention."""
    
    invention_title: str = Field(
        description="The name or title of the core invention/contribution of the paper."
    )
    
    problem_statement: str = Field(
        description="What problem does this invention solve? What gap does it address?"
    )
    
    solution_steps: List[str] = Field(
        description="A sequential list of 3-5 VISUAL steps. Describe what happens geometrically or mathematically (e.g., 'Matrix A is multiplied by vector v', 'Points project onto a manifold'). Avoid abstract text.",
        min_length=3,
        max_length=10
    )
    
    visual_metaphor: Optional[str] = Field(
        default=None,
        description="A core visual analogy to explain the concept (e.g., 'Projecting a shadow', 'Filtering water', 'Balancing a scale', 'Traffic flow')."
    )
    
    key_insight: str = Field(
        description="The core novelty or 'aha' moment of the invention. What makes it unique?"
    )
    
    results_summary: Optional[str] = Field(
        default=None,
        description="Brief summary of the paper's key results or improvements."
    )
