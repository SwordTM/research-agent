"""Invention Summarizer Tool - Extracts a structured breakdown of the main invention from a research paper."""

import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# Add parent to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.invention import InventionBreakdown


class InventionSummarizerTool:
    """Extracts a structured breakdown of the main invention from a research paper."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API Key (OPENROUTER_API_KEY or GEMINI_API_KEY) is required")
        
        self.parser = PydanticOutputParser(pydantic_object=InventionBreakdown)
        self.llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            openai_api_key=self.api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://research-agent.com",
                "X-Title": "Research Agent"
            }
        )
    
    def summarize(self, paper_text: str) -> Optional[InventionBreakdown]:
        """
        Analyze a research paper and extract a structured breakdown of its main invention.
        
        Args:
            paper_text: The full extracted text of the research paper.
            
        Returns:
            InventionBreakdown object containing the structured analysis.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Visual Explainer and Science Communicator specializing in Geometric Deep Learning and Neural Architectures.
Your goal is to translate complex research papers into a VISUAL STORYBOARD that can be animated.

Your task is to read the paper and extract a STRUCTURED BREAKDOWN focused exclusively on the MAIN INVENTION (e.g., "Manifold Constrained Hyper-Connections").

CRITICAL RULES:
1. **FOCUS ON THE ONE MAIN TECHNIQUE**: Ignore secondary or auxiliary techniques. Concentrated all narrative energy on the core mechanism that makes the paper unique.
2. **THINK IN PICTURES**: Do not just summarize the text. Describe what we should SEE.
    - BAD: "The model improves stability."
    - GOOD: "The residual vector 'x' projects onto a doubly stochastic manifold 'M'."
    - BAD: "Efficiency is increased."
    - GOOD: "Multiple small matrices merge into one large kernel matrix."

3. **USE VISUAL METAPHORS**: Find a core analogy that represents the transformation (e.g., "Projecting a shadow," "Filtering water," "Balancing a scale," "Traffic flow").

4. **STRUCTURE THE NARRATIVE**:
    - **Step 1 (Problem)**: Visual representation of the issue (e.g., a signal getting lost in noise, gradients exploding).
    - **Step 2 (The Core Transformation)**: The primary geometric or mathematical innovation (e.g., constraining a vector to a manifold). This is the HEART of the animation.
    - **Step 3 (The Flow)**: How data traverses this new mechanism.
    - **Step 4 (The Convergence/Result)**: The final stable or optimized state.

5. **BE CONCRETE**: Use terms like "Matrix," "Vector," "Graph," "Node," "Flow," "Arrow," "Manifold," "Plane." Use LaTeX for mathematical symbols in descriptions.

{format_instructions}"""),
            ("user", """Analyze the following research paper and extract a structured breakdown of its PRIMARY invention.

PAPER CONTENT:
{paper_text}

Identify:
1. The main invention/contribution (The One Core Technique)
2. The problem it solves
3. Visual narrative steps (3-5 steps explaining the core transformation)
4. The core visual metaphor
5. The key novel insight""")
        ])
        
        try:
            print("[INVENTION SUMMARIZER] Analyzing paper for main invention...", flush=True)
            
            chain = prompt | self.llm
            response = chain.invoke({
                "paper_text": paper_text[:80000],  # Truncate to fit context window
                "format_instructions": self.parser.get_format_instructions()
            })
            
            import re
            content = response.content.strip()
            # Clean markdown code blocks if present
            json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                # Also handle generic code blocks
                generic_match = re.search(r"```\s*(.*?)\s*```", content, re.DOTALL)
                if generic_match:
                    content = generic_match.group(1)
            # Sanitize invalid escape sequences in JSON (e.g., LaTeX \( \) \[ \])
            # The LLM often puts raw LaTeX in JSON strings, causing parse errors
            import json as json_mod
            
            def safe_parse_json(s):
                """Try to parse JSON, fixing invalid escapes if needed."""
                # First try direct parse
                try:
                    return json_mod.loads(s)
                except json_mod.JSONDecodeError:
                    pass
                
                # Fix: replace problematic backslash sequences
                # Walk through the string and double any backslash that isn't 
                # part of a valid JSON escape (\" \\ \/ \b \f \n \r \t \u)
                fixed = []
                i = 0
                while i < len(s):
                    if s[i] == '\\' and i + 1 < len(s):
                        next_char = s[i + 1]
                        if next_char in '"\\/bfnrtu':
                            # Valid JSON escape — keep as-is
                            fixed.append(s[i])
                            fixed.append(s[i + 1])
                            i += 2
                        else:
                            # Invalid escape — double the backslash
                            fixed.append('\\\\')
                            fixed.append(s[i + 1])
                            i += 2
                    else:
                        fixed.append(s[i])
                        i += 1
                
                fixed_str = ''.join(fixed)
                return json_mod.loads(fixed_str)
            
            parsed = safe_parse_json(content)
            
            # Use the parser's Pydantic model to validate
            from models.invention import InventionBreakdown
            result = InventionBreakdown(**parsed)
            
            print(f"[INVENTION SUMMARIZER] Found invention: {result.invention_title}", flush=True)
            print(f"[INVENTION SUMMARIZER] {len(result.solution_steps)} visual steps identified", flush=True)
            
            return result
            
        except Exception as e:
            print(f"[INVENTION SUMMARIZER] Error: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc()
            return None


def create_tool(api_key: str = None):
    """Create and return the invention summarizer tool instance."""
    return InventionSummarizerTool(api_key=api_key)
