import os
import subprocess
import uuid
from pathlib import Path
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from models.roadmap import Concept

class ManimCodeGenerator:
    """Generates Manim code for visualizing concepts."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=self.api_key,
            temperature=0.2
        )
        
    def generate_code(self, concept: Concept) -> str:
        """Generate Manim code for a concept."""
        
        print(f"                 [AI] Requesting code from Gemini 2.5 Pro...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Manim animator. Your task is to write Python code using the Manim library to visualize a research concept.
            
            CRITICAL RULES:
            1. Your code MUST inherit from `Slide` (from manim_slides).
            2. You MUST define a class named `ConceptScene`.
            3. You MUST implement the `construct` method.
            4. Use `self.next_slide()` to separate steps in the animation.
            5. ONLY import: `from manim import *` and `from manim_slides import Slide`.
            6. Do NOT use interactive input() calls.
            7. Keep animations simple and clear. Use standard Manim shapes (Rectangle, Circle, Arrow, Text, MathTex).
            8. Explain the concept visually with clear titles and labels.
            9. For background color, use: self.camera.background_color = ManimColor.from_hex("#1e1e1e")
            10. AVOID complex Text parameters like t2a, t2c, t2s - use simple Text() only.
            11. AVOID special characters that might cause encoding issues.
            12. Use line_spacing parameter for multi-line text instead of complex formatting.
            13. Keep Text font_size between 20-48.
            14. Test all syntax - ensure valid Python code.
            15. Use standard Manim colors: WHITE, BLUE, GREEN, RED, YELLOW, PURPLE, ORANGE, etc.
            
            Example Structure:
            ```python
            from manim import *
            from manim_slides import Slide
            
            class ConceptScene(Slide):
                def construct(self):
                    # Set background - MUST use ManimColor
                    self.camera.background_color = ManimColor.from_hex("#1e1e1e")
                    
                    # Title
                    title = Text("Concept Name", font_size=48, color=WHITE)
                    title.to_edge(UP)
                    underline = Line(LEFT, RIGHT, color=BLUE)
                    underline.match_width(title).next_to(title, DOWN, buff=0.1)
                    self.play(Write(title), Create(underline))
                    self.next_slide()
                    
                    # Content - use simple shapes and text
                    box = Rectangle(width=4, height=2, color=BLUE, fill_opacity=0.3)
                    label = Text("Core Idea", font_size=32, color=WHITE)
                    label.move_to(box)
                    self.play(Create(box), Write(label))
                    self.next_slide()
            ```
            
            IMPORTANT: Generate ONLY valid, simple Python code. Avoid advanced Text features.
            CRITICAL: Always use ManimColor.from_hex() for hex colors, never plain strings!
            """),
            ("user", """Create a Manim visualization for the following concept:
            
            Title: {title}
            Description: {description}
            Type: {type}
            
            Generate ONLY the Python code. Keep it simple and avoid complex Text parameters.
            Remember: Use ManimColor.from_hex("#hexcode") for colors, not strings!""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "title": concept.title,
            "description": concept.description,
            "type": concept.concept_type
        })
        
        print(f"                 [AI] Response received, extracting code...")
        
        # Extract code from markdown block if present
        code = response.content
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
            
        return code

class SlideRenderer:
    """Renders Manim slides to HTML."""
    
    def __init__(self, output_dir: str = "public/slides"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = Path("temp_scenes")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Get paths to executables in venv
        venv_scripts = Path(__file__).parent.parent / "venv" / "Scripts"
        self.manim_exe = str(venv_scripts / "manim.exe")
        self.manim_slides_exe = str(venv_scripts / "manim-slides.exe")
        
    def render(self, code: str, concept_id: str) -> Optional[str]:
        """Render the Manim code to HTML."""
        
        # Write code to temp file
        filename = f"scene_{concept_id}.py"
        filepath = self.temp_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        
        print(f"                 [RENDER] Code written to: {filename}")
        
        # Validate Python syntax before rendering
        print(f"                 [RENDER] Validating Python syntax...")
        try:
            import ast
            import sys
            ast.parse(code)
            print(f"                 [RENDER] Syntax validation passed")
            sys.stdout.flush()
        except SyntaxError as e:
            print(f"                 [RENDER] SYNTAX ERROR in generated code:")
            print(f"                 [RENDER] Line {e.lineno}: {e.msg}")
            print(f"                 [RENDER] {e.text}")
            sys.stdout.flush()
            return None
            
        try:
            # Step 1: Render Manim Scene using manim-slides render
            # This combines both manim rendering and slide preparation
            print(f"                 [RENDER] Step 1/2: Rendering Manim scene...")
            cmd_render = [
                self.manim_slides_exe, "render", 
                filename,  # Just the filename since we're running in temp_dir
                "ConceptScene",
                "-ql"  # Low quality for speed
            ]
            
            print(f"                 [RENDER] Executing: {' '.join(cmd_render)}")
            result = subprocess.run(
                cmd_render, 
                check=True, 
                capture_output=True,
                text=True,
                cwd=str(self.temp_dir)
            )
            
            print(f"                 [RENDER] Scene rendered successfully")
            
            # Step 2: Convert to HTML
            print(f"                 [RENDER] Step 2/2: Converting to HTML...")
            output_html = self.output_dir / f"{concept_id}.html"
            
            cmd_convert = [
                self.manim_slides_exe, "convert", 
                "ConceptScene", 
                str(output_html),
                "--force"  # Overwrite if exists
            ]
            
            print(f"                 [RENDER] Executing: {' '.join(cmd_convert)}")
            result = subprocess.run(
                cmd_convert,
                check=True,
                capture_output=True,
                text=True,
                cwd=str(self.temp_dir)
            )
            
            print(f"                 [RENDER] HTML conversion complete")
            print(f"                 [RENDER] Output file: {output_html}")
            
            return f"/slides/{concept_id}.html"
            
        except subprocess.CalledProcessError as e:
            print(f"Error rendering slides: {e}")
            if e.stdout:
                print(f"Stdout: {e.stdout}")
            if e.stderr:
                print(f"Stderr: {e.stderr}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return None
