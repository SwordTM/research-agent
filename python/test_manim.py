import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(__file__))

from visualization.manim_generator import ManimCodeGenerator, SlideRenderer
from models.roadmap import Concept, ConceptType

def test_generation():
    print("Testing Manim generation...")
    
    # Create a dummy concept
    concept = Concept(
        id="test_concept_1",
        title="Transformer Architecture",
        description="The Transformer follows an encoder-decoder structure using stacked self-attention and point-wise, fully connected layers.",
        concept_type=ConceptType.ARCHITECTURE,
        importance_score=0.9
    )
    
    try:
        # Initialize generator
        generator = ManimCodeGenerator()
        renderer = SlideRenderer(output_dir="../research-agent-web/public/slides")
        
        # Generate code
        print("Generating code...")
        code = generator.generate_code(concept)
        print("Generated Code:")
        print(code)
        
        # Render
        print("Rendering slides...")
        url = renderer.render(code, concept.id)
        
        if url:
            print(f"Success! Slide URL: {url}")
        else:
            print("Rendering failed.")
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation()
