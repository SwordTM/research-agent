"""Roadmap Agent - LangChain agent for analyzing research papers and generating roadmaps with Dart visualizations."""

import os
import sys
import json
from typing import Optional, Any, List, Dict

# Add parent directory to path to allow importing from models and other packages
current_dir = os.path.dirname(os.path.abspath(__file__)) # python/agent
python_dir = os.path.dirname(current_dir) # python
sys.path.append(python_dir)

import logging
import logging.handlers

# Ensure logs directory exists
log_dir = os.path.join(python_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "research_agent.log")

# Configure root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File Handler (Writing to log file)
file_handler = logging.handlers.RotatingFileHandler(
    log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Stream Handler (Writing to stdout)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

from models.roadmap import Roadmap, Concept
from agent.tools.pdf_parser import create_tool as create_pdf_parser
from agent.tools.invention_summarizer import create_tool as create_invention_summarizer
from generate_manim_web_dart import generate_dart_code, fix_dart_code
from build_manim_web import build_manim_web

MAX_BUILD_RETRIES = 3

class RoadmapAgent:
    def __init__(self, api_key: str = None):
        """Initialize the Roadmap Agent."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
            
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        # Initialize components
        print(f"-> Initializing PDF Parser...")
        self.pdf_parser = create_pdf_parser()
        
        print(f"-> Initializing Invention Summarizer...")
        self.invention_summarizer = create_invention_summarizer(api_key=self.api_key)
        
        # Initialize LLM for summary tasks
        print(f"-> Initializing Gemini Pro (via OpenRouter)...")
        from langchain_openai import ChatOpenAI
        self.llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            openai_api_key=self.api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={"HTTP-Referer": "https://research-agent.com", "X-Title": "Research Agent"}
        )
             
    def analyze_paper(self, pdf_path: str) -> Roadmap:
        """
        Analyze a research paper and create a roadmap with a Dart visualization.
        """
        print("\n" + "="*70)
        print("[ROADMAP AGENT] Starting paper analysis (DART PIPELINE)...")
        print("="*70)
        sys.stdout.flush()
        
        # 1. Parse PDF
        print(f"\n[1/4] Parsing PDF: {pdf_path}")
        sys.stdout.flush()
        pdf_data = self.pdf_parser.parse_pdf(pdf_path)
        paper_text = pdf_data["text"]
        print(f"      -> Extracted {len(paper_text)} characters")
        sys.stdout.flush()
        
        # 2. Summarize Invention
        print(f"\n[2/4] Analyzing invention context...")
        sys.stdout.flush()
        invention = self.invention_summarizer.summarize(paper_text)
        summary = self.generate_summary(paper_text)
        
        invention_title = invention.invention_title if invention else "Research Contribution"
        print(f"      -> Focus: {invention_title}")
        sys.stdout.flush()
        
        # 3. Extract key concepts (simulated for roadmap structure)
        # We'll use a simple list based on the invention summary for the MVP
        concepts = [
            Concept(
                id="main_visual",
                title=invention_title,
                description=invention.problem_statement if invention else "Core contribution",
                concept_type="architecture",
                importance_score=1.0
            )
        ]
        
        # 4. Generate Dart Visualization
        print(f"\n[3/4] Generating Dart Manim Visualization...")
        sys.stdout.flush()
        
        # We use the specialized generator and pass the invention context
        invention_data = invention.model_dump() if invention else None
        dart_result = generate_dart_code(paper_text, invention_context=invention_data)
        
        if not dart_result.get("success"):
            print(f"      [ERROR] Dart generation failed: {dart_result.get('error')}")
            sys.stdout.flush()
            # Create roadmap without slide
            return Roadmap(
                paper_title=pdf_data["metadata"].get("title", invention_title),
                paper_summary=summary,
                concepts=concepts,
                main_contribution=invention.key_insight if invention else "",
                prerequisites=[]
            )

        # 5. Build Dart Project (with auto-correction retry loop)
        print(f"\n[4/4] Building Dart project (webdev build)...")
        sys.stdout.flush()
        
        # Save code to a temp file for the builder
        temp_code_path = os.path.join(python_dir, "temp_scenes", f"scene_latest.dart")
        os.makedirs(os.path.dirname(temp_code_path), exist_ok=True)
        
        current_code = dart_result["code"]
        safe_title = "".join([c if c.isalnum() else "_" for c in invention_title]).lower()[:30]
        project_dir = os.path.join(os.path.dirname(python_dir), "manim_project")
        
        build_result = None
        for attempt in range(1, MAX_BUILD_RETRIES + 1):
            # Write current code
            with open(temp_code_path, "w", encoding="utf-8") as f:
                f.write(current_code)
            
            if attempt > 1:
                print(f"\n      [RETRY {attempt}/{MAX_BUILD_RETRIES}] Rebuilding with corrected code...")
            
            sys.stdout.flush()
            
            build_result = build_manim_web(
                temp_code_path, 
                project_dir=project_dir,
                subfolder=f"visuals_{safe_title}"
            )
            
            if build_result.get("success"):
                print(f"      -> SUCCESS! Visualization ready at: {build_result['url']}")
                concepts[0].slide_url = build_result["url"]
                break
            else:
                error_msg = build_result.get('error', 'Unknown build error')
                print(f"      [ERROR] Build failed (attempt {attempt}/{MAX_BUILD_RETRIES}): {error_msg}")
                sys.stdout.flush()
                
                if attempt < MAX_BUILD_RETRIES:
                    # Auto-correction: ask LLM to fix the code
                    print(f"      [AUTO-FIX] Sending code to auto-correction agent...")
                    sys.stdout.flush()
                    
                    fix_result = fix_dart_code(current_code, error_msg, attempt=attempt)
                    
                    if fix_result.get("success"):
                        current_code = fix_result["code"]
                        print(f"      [AUTO-FIX] Received corrected code, retrying build...")
                    else:
                        print(f"      [AUTO-FIX] Fix failed: {fix_result.get('error')}")
                        break
                else:
                    print(f"      [GIVE UP] Max retries ({MAX_BUILD_RETRIES}) reached. Build failed.")
        
        sys.stdout.flush()

        # Create final roadmap
        roadmap = Roadmap(
            paper_title=pdf_data["metadata"].get("title", invention_title),
            paper_summary=summary,
            concepts=concepts,
            main_contribution=invention.key_insight if invention else "",
            prerequisites=[]
        )
        
        return roadmap
    
    def generate_summary(self, paper_text: str) -> str:
        """Generate a high-fidelity summary of the research paper."""
        prompt = f"""Analyze the provided research paper text and provide a 3-sentence summary.
        
        PAPER TEXT:
        {paper_text[:10000]}
        
        Summary:"""
        
        if hasattr(self, 'llm'):
            response = self.llm.invoke(prompt)
            return response.content
        return "Summary not available."

# Compatibility wrapper for create_agent
def create_agent(api_key: str = None) -> RoadmapAgent:
    return RoadmapAgent(api_key=api_key)

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No PDF path provided"}))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        agent = create_agent()
        roadmap = agent.analyze_paper(pdf_path)
        
        result = {
            "paper_title": roadmap.paper_title,
            "paper_summary": roadmap.paper_summary,
            "main_contribution": roadmap.main_contribution,
            "concepts": [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "type": c.concept_type if isinstance(c.concept_type, str) else c.concept_type.value,
                    "importance": c.importance_score,
                    "slide_url": getattr(c, 'slide_url', None)
                }
                for c in roadmap.concepts
            ]
        }
        
        print("\n__JSON_RESULT__")
        print(json.dumps(result))
        print("__JSON_RESULT_END__")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        sys.stderr.write(json.dumps({"error": str(e), "traceback": error_details}))
        sys.exit(1)
