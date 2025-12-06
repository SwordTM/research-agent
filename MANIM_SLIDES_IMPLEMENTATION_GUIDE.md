# Manim Slides Generation - Implementation Guide

## Overview

The Research Agent uses an AI-powered pipeline to automatically generate animated educational slides from research paper concepts using Manim (Mathematical Animation Engine) and Manim Slides. This guide explains the complete implementation architecture and workflow.

## Architecture Components

### 1. **Core Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    Research Agent Pipeline                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PDF Parser → Concept Extractor → Code Generator → Renderer │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2. **Key Modules**

- **`roadmap_agent.py`** - Main orchestrator
- **`manim_generator.py`** - Code generation and rendering
- **`concept_extractor.py`** - AI-powered concept extraction
- **`pdf_parser.py`** - PDF text extraction
- **`roadmap.py`** - Data models

---

## Implementation Workflow

### Phase 1: Concept Extraction

#### Step 1.1: PDF Parsing
**File:** `agent/tools/pdf_parser.py`

```python
# Parse PDF and extract text
pdf_data = pdf_parser.parse_pdf(pdf_path)
paper_text = pdf_data["text"]
```

**What happens:**
- Extracts raw text from PDF
- Captures metadata (title, author, etc.)
- Preserves document structure

#### Step 1.2: Concept Identification
**File:** `agent/tools/concept_extractor.py`

```python
# Extract concepts using Gemini AI
concepts = concept_extractor.extract_concepts(paper_text, max_concepts=10)
```

**AI Prompt Strategy:**
- Uses **Gemini 2.5 Pro** with temperature 0.3 (for consistency)
- Identifies key concepts, techniques, architectures, algorithms
- Assigns importance scores (0.0 to 1.0)
- Categorizes by type: `ARCHITECTURE`, `TECHNIQUE`, `ALGORITHM`, `METHODOLOGY`, `RESULT`, `INNOVATION`

**Output:** List of `Concept` objects with:
```python
class Concept:
    id: str                    # e.g., "transformer_architecture"
    title: str                 # e.g., "Transformer Architecture"
    description: str           # Detailed explanation
    concept_type: ConceptType  # Category
    importance_score: float    # 0.0 to 1.0
```

---

### Phase 2: Manim Code Generation

#### Step 2.1: AI-Powered Code Generation
**File:** `visualization/manim_generator.py`
**Class:** `ManimCodeGenerator`

```python
code_generator = ManimCodeGenerator(api_key=gemini_api_key)
code = code_generator.generate_code(concept)
```

**How it works:**

1. **LLM Configuration:**
   - Model: `gemini-2.5-pro`
   - Temperature: `0.2` (low for code consistency)

2. **Prompt Engineering:**
   The system prompt enforces strict rules:
   ```python
   """You are an expert Manim animator. Your task is to write Python code 
   using the Manim library to visualize a research concept.
   
   RULES:
   1. Your code MUST inherit from `Slide` (from manim_slides).
   2. You MUST define a class named `ConceptScene`.
   3. You MUST implement the `construct` method.
   4. Use `self.next_slide()` to separate steps in the animation.
   5. ONLY import: `from manim import *` and `from manim_slides import Slide`.
   6. Do NOT use interactive input() calls.
   7. Keep animations simple and clear.
   8. Use dark background (#1e1e1e) and light text (WHITE).
   """
   ```

3. **Input Data:**
   ```python
   {
       "title": concept.title,
       "description": concept.description,
       "type": concept.concept_type
   }
   ```

4. **Output:** Complete Python code with `ConceptScene` class

**Example Generated Code Structure:**
```python
from manim import *
from manim_slides import Slide

class ConceptScene(Slide):
    def construct(self):
        # Set background
        self.camera.background_color = "#1e1e1e"
        
        # Title slide
        title = Text("Transformer Architecture", font_size=48, color=WHITE)
        title.to_edge(UP)
        underline = Line(LEFT, RIGHT, color=BLUE).match_width(title)
        underline.next_to(title, DOWN, buff=0.1)
        
        self.play(Write(title), Create(underline))
        self.next_slide()
        
        # Visual content (boxes, arrows, diagrams)
        # ...
        
        self.next_slide()
```

---

### Phase 3: Rendering Pipeline

#### Step 3.1: Scene Rendering
**File:** `visualization/manim_generator.py`
**Class:** `SlideRenderer`

```python
renderer = SlideRenderer(output_dir="../research-agent-web/public/slides")
slide_url = renderer.render(code, concept.id)
```

**Rendering Process:**

1. **File Creation:**
   ```python
   # Write generated code to temporary file
   filepath = temp_dir / f"scene_{concept_id}.py"
   with open(filepath, "w", encoding="utf-8") as f:
       f.write(code)
   ```

2. **Manim Slides Render:**
   ```bash
   manim-slides render scene_{concept_id}.py ConceptScene -ql
   ```
   
   **Flags:**
   - `-ql` = Low quality (faster rendering)
   - Could use `-qh` for high quality production

   **What happens:**
   - Manim renders each animation frame
   - Creates video segments for each slide
   - Stores slide metadata for navigation

3. **HTML Conversion:**
   ```bash
   manim-slides convert ConceptScene {concept_id}.html --force
   ```
   
   **Output:**
   - Interactive HTML file with embedded videos
   - Navigation controls (next/previous slide)
   - Keyboard shortcuts support
   - Responsive design

4. **File Organization:**
   ```
   research-agent-web/
   └── public/
       └── slides/
           ├── transformer_architecture.html
           ├── attention_mechanism.html
           └── ...
   ```

#### Step 3.2: Error Handling

```python
try:
    # Render and convert
    result = subprocess.run(cmd_render, check=True, capture_output=True)
except subprocess.CalledProcessError as e:
    print(f"Error rendering slides: {e}")
    print(f"Stdout: {e.stdout}")
    print(f"Stderr: {e.stderr}")
    return None
```

---

## Complete Integration Flow

### Main Orchestration
**File:** `agent/roadmap_agent.py`

```python
def analyze_paper(self, pdf_path: str) -> Roadmap:
    # 1. Parse PDF
    pdf_data = self.pdf_parser.parse_pdf(pdf_path)
    paper_text = pdf_data["text"]
    
    # 2. Extract concepts
    concepts = self.concept_extractor.extract_concepts(paper_text)
    
    # 3. Generate summary
    summary = self.generate_summary(paper_text)
    
    # 4. Generate slides for each concept
    code_generator = ManimCodeGenerator(api_key=self.api_key)
    renderer = SlideRenderer(output_dir="../research-agent-web/public/slides")
    
    for concept in concepts:
        try:
            print(f"Generating slides for concept: {concept.title}...")
            
            # Generate Manim code
            code = code_generator.generate_code(concept)
            
            # Render slides
            slide_url = renderer.render(code, concept.id)
            
            if slide_url:
                print(f"Slides generated: {slide_url}")
        except Exception as e:
            print(f"Failed to generate slides for {concept.title}: {e}")
    
    # 5. Create roadmap
    roadmap = Roadmap(
        paper_id=os.path.basename(pdf_path),
        title=pdf_data["metadata"].get("title", "Unknown"),
        paper_summary=summary,
        concepts=concepts,
        main_contribution=main_contribution,
        prerequisites=[]
    )
    
    return roadmap
```

---

## Data Models

### Concept Model
**File:** `models/roadmap.py`

```python
class ConceptType(str, Enum):
    ARCHITECTURE = "architecture"
    TECHNIQUE = "technique"
    ALGORITHM = "algorithm"
    METHODOLOGY = "methodology"
    RESULT = "result"
    INNOVATION = "innovation"

class Concept(BaseModel):
    id: str
    title: str
    description: str
    concept_type: ConceptType
    page_numbers: List[int] = []
    related_concepts: List[str] = []
    importance_score: float = 0.5  # 0.0 to 1.0
```

### Roadmap Model

```python
class Roadmap(BaseModel):
    paper_title: str
    paper_summary: str
    concepts: List[Concept]
    diagrams: List[DiagramInfo] = []
    main_contribution: str
    prerequisites: List[str] = []
```

---

## Environment Setup

### Required Dependencies

```bash
# Python environment
pip install manim
pip install manim-slides
pip install langchain-google-genai
pip install pydantic
pip install python-dotenv

# System dependencies (Windows)
# - FFmpeg (for video rendering)
# - LaTeX (for mathematical formulas)
```

### Environment Variables

```env
GEMINI_API_KEY=your_api_key_here
```

### Virtual Environment Structure

```
python/
├── venv/
│   └── Scripts/
│       ├── manim.exe
│       └── manim-slides.exe
├── temp_scenes/          # Temporary rendering directory
│   ├── scene_*.py        # Generated Python files
│   └── media/            # Rendered videos
└── ...
```

---

## Execution Paths

### Path 1: Command Line Execution

```bash
cd python
python agent/roadmap_agent.py path/to/paper.pdf
```

**Output:** JSON with roadmap data

### Path 2: Programmatic Usage

```python
from agent.roadmap_agent import create_agent

agent = create_agent()
roadmap = agent.analyze_paper("path/to/paper.pdf")

# Access concepts
for concept in roadmap.concepts:
    print(f"{concept.title}: /slides/{concept.id}.html")
```

### Path 3: Testing Individual Components

```python
# Test file: test_manim.py
from visualization.manim_generator import ManimCodeGenerator, SlideRenderer
from models.roadmap import Concept, ConceptType

concept = Concept(
    id="test_concept",
    title="Transformer Architecture",
    description="...",
    concept_type=ConceptType.ARCHITECTURE,
    importance_score=0.9
)

generator = ManimCodeGenerator()
code = generator.generate_code(concept)

renderer = SlideRenderer(output_dir="../research-agent-web/public/slides")
url = renderer.render(code, concept.id)
```

---

## Advanced Features

### 1. Custom Slide Templates
**File:** `visualization/manim_slides_generator.py`

Pre-built slide components:
```python
class ConceptSlide(Slide):
    def construct_title_slide(self, title: str, subtitle: str = ""):
        """Create a title slide."""
        # ...
    
    def construct_bullet_points(self, points: list, title: str = ""):
        """Create a slide with bullet points."""
        # ...
```

### 2. Example Slide: CNN Architecture
```python
class CNNArchitectureSlide(ConceptSlide):
    def construct(self):
        # Title slide
        self.construct_title_slide(
            "Convolutional Neural Network",
            "Architecture Overview"
        )
        
        # Layer visualization
        input_layer = Rectangle(width=1.5, height=2, color=BLUE)
        conv1 = Rectangle(width=1.2, height=1.8, color=GREEN)
        # ... more layers
        
        layers = VGroup(input_layer, conv1, ...)
        layers.arrange(RIGHT, buff=0.5)
        
        for layer in layers:
            self.play(FadeIn(layer, shift=UP))
        
        self.next_slide()
```

---

## Output Format

### HTML Slide Structure

The generated HTML files include:
- **Embedded videos** (WebM format)
- **Navigation controls**
- **Keyboard shortcuts** (Arrow keys, Space)
- **Progress indicator**
- **Fullscreen support**

### Accessing Slides

Frontend integration:
```typescript
// In Next.js/React
const slideUrl = `/slides/${concept.id}.html`;

<iframe 
  src={slideUrl} 
  className="w-full h-full"
  title={concept.title}
/>
```

---

## Performance Considerations

### Rendering Speed
- **Low quality (`-ql`)**: ~10-30 seconds per concept
- **High quality (`-qh`)**: ~1-3 minutes per concept

### Optimization Strategies
1. **Parallel rendering**: Process multiple concepts concurrently
2. **Caching**: Store generated code to avoid re-generation
3. **Lazy rendering**: Generate slides on-demand
4. **Quality tiers**: Use low quality for preview, high for final

---

## Error Handling & Debugging

### Common Issues

1. **Code Generation Fails**
   - Check API key validity
   - Verify concept description quality
   - Review LLM temperature settings

2. **Rendering Fails**
   - Ensure FFmpeg is installed
   - Check temp directory permissions
   - Verify manim-slides installation

3. **Invalid Python Code**
   - AI might generate syntax errors
   - Add code validation before rendering
   - Implement retry logic with different prompts

### Debug Mode

```python
# Enable verbose output
result = subprocess.run(
    cmd_render,
    check=True,
    capture_output=True,
    text=True,
    cwd=str(self.temp_dir)
)
print(f"Render output: {result.stdout}")
print(f"Render errors: {result.stderr}")
```

---

## Future Enhancements

### Planned Features
1. **Template Library**: Pre-built templates for common concept types
2. **Interactive Elements**: Clickable diagrams, zoom controls
3. **Multi-language Support**: Generate slides in different languages
4. **Voice Narration**: Add AI-generated audio explanations
5. **3D Visualizations**: Use Manim's 3D capabilities for complex concepts
6. **Collaborative Editing**: Allow manual refinement of generated code

### Integration Opportunities
- **MCP Server**: Expose slide generation as MCP tool
- **Real-time Preview**: WebSocket-based live rendering
- **Batch Processing**: Queue system for multiple papers
- **Analytics**: Track which slides are most viewed/helpful

---

## Summary

The Manim slides generation system is a sophisticated AI-powered pipeline that:

1. **Extracts** key concepts from research papers using Gemini AI
2. **Generates** custom Manim Python code for each concept
3. **Renders** interactive HTML slides with animations
4. **Integrates** seamlessly with the web frontend

**Key Technologies:**
- **Manim**: Mathematical animation engine
- **Manim Slides**: Presentation framework
- **Gemini 2.5 Pro**: Code generation and concept extraction
- **LangChain**: LLM orchestration
- **Pydantic**: Data validation

**Workflow:**
```
PDF → Text Extraction → Concept Extraction → Code Generation → Rendering → HTML Slides
```

This creates an automated, scalable system for transforming research papers into engaging visual presentations.
