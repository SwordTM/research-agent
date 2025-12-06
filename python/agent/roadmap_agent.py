"""Roadmap Agent - LangChain agent for analyzing research papers and generating roadmaps."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
        self.agent_executor = self._create_agent()
    
    def _create_agent(self) -> Optional[Any]:
        """Create the LangChain agent with tools."""
        
        tools = [
            Tool(
                name="parse_pdf",
                func=self.pdf_parser.parse_pdf,
                description="Parse a PDF file and extract text, metadata, and structure. Input: path to PDF file."
            ),
            Tool(
                name="extract_concepts",
                func=lambda text: self.concept_extractor.extract_concepts(text),
                description="Extract key concepts from research paper text. Input: paper text."
            ),
        ]
        
        # For now, we'll use the tools directly instead of creating a complex agent
        # This is simpler and more reliable for the initial implementation
        return None  # We'll call tools directly in analyze_paper
    
    def analyze_paper(self, pdf_path: str) -> Roadmap:
        """
        Analyze a research paper and create a roadmap.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Roadmap object with extracted concepts
        """
        import sys
        
        print("\n" + "="*70)
        print("[ROADMAP AGENT] Starting paper analysis...")
        print("="*70)
        sys.stdout.flush()
        
        # Parse PDF
        print(f"\n[1/4] Parsing PDF: {pdf_path}")
        sys.stdout.flush()
        pdf_data = self.pdf_parser.parse_pdf(pdf_path)
        paper_text = pdf_data["text"]
        print(f"      -> Extracted {len(paper_text)} characters")
        sys.stdout.flush()
        
        # Extract concepts
        print(f"\n[2/4] Extracting concepts using AI...")
        sys.stdout.flush()
        concepts = self.concept_extractor.extract_concepts(paper_text)
        print(f"      -> Found {len(concepts)} concepts")
        for i, c in enumerate(concepts, 1):
            print(f"      {i}. {c.title} ({c.concept_type.value})")
        sys.stdout.flush()
        
        # Generate summary
        print(f"\n[3/4] Generating paper summary...")
        sys.stdout.flush()
        summary = self.generate_summary(paper_text)
        print(f"      -> Summary generated ({len(summary)} chars)")
        sys.stdout.flush()
        
        # Extract main contribution (simplified for now)
        main_contribution = "See summary for main contributions."
        
        # Generate Slides for each concept
        print(f"\n[4/4] Generating Manim slides for {len(concepts)} concepts...")
        print("      This may take several minutes...\n")
        sys.stdout.flush()
        
        from visualization.manim_generator import ManimCodeGenerator, SlideRenderer
        
        code_generator = ManimCodeGenerator(api_key=self.api_key)
        renderer = SlideRenderer(output_dir="../research-agent-web/public/slides")
        
        for idx, concept in enumerate(concepts, 1):
            try:
                print(f"\n[SLIDE {idx}/{len(concepts)}] Processing: {concept.title}")
                print(f"              Type: {concept.concept_type.value}")
                print(f"              ID: {concept.id}")
                
                # Generate Manim code
                print(f"              -> Generating Manim code with AI...")
                code = code_generator.generate_code(concept)
                print(f"              -> Code generated ({len(code)} chars)")
                
                # Render slides
                print(f"              -> Rendering animation (this may take 30-60s)...")
                slide_url = renderer.render(code, concept.id)
                
                if slide_url:
                    print(f"              -> SUCCESS! Slide URL: {slide_url}")
                else:
                    print(f"              -> WARNING: Rendering failed")
            except Exception as e:
                print(f"              -> ERROR: {e}")
                import traceback
                traceback.print_exc()

        # Create roadmap
        roadmap = Roadmap(
            paper_id=os.path.basename(pdf_path),
            title=pdf_data["metadata"].get("title", "Unknown"),
            paper_summary=summary,
            concepts=concepts,
            main_contribution=main_contribution,
            prerequisites=[]
        )
        
        return roadmap
    
    def generate_summary(self, paper_text: str) -> str:
        """Generate a summary of the research paper."""
        prompt = f"""Provide a concise summary (3-4 sentences) of this research paper:

{paper_text[:10000]}

Summary:"""
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def explain_concept(self, concept: Concept, context: str = "") -> str:
        """Generate a detailed explanation of a concept."""
        prompt = f"""Explain the following concept from a research paper in detail:

Concept: {concept.title}
Description: {concept.description}
Type: {concept.concept_type}

{f'Additional context: {context}' if context else ''}

Provide a clear, detailed explanation suitable for creating visual slides."""
        
        response = self.llm.invoke(prompt)
        return response.content


def create_agent(api_key: str = None) -> RoadmapAgent:
    """Create and return a RoadmapAgent instance."""
    return RoadmapAgent(api_key=api_key)


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No PDF path provided"}))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    try:
        agent = create_agent()
        roadmap = agent.analyze_paper(pdf_path)
        
        # Convert to dict for JSON serialization
        result = {
            "paper_title": roadmap.paper_title,
            "paper_summary": roadmap.paper_summary,
            "main_contribution": roadmap.main_contribution,
            "concepts": [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "type": c.concept_type.value,
                    "importance": c.importance_score
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
