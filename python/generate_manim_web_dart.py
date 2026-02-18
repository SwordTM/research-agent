import os
import sys
import json
import argparse
from dotenv import load_dotenv

# Add parent directory to path to allow importing from agent and models
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Handle potential import errors if running standalone
try:
    from agent.tools.pdf_parser import create_tool as create_pdf_parser
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    # Assuming user might run this without full env setup, but for now required
    print(json.dumps({"error": "Missing dependencies (langchain, etc.)"}), file=sys.stdout)
    sys.exit(1)

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_dart_code(paper_text: str, pdf_path: str = None, invention_context: dict = None):
    """
    Generates Manim Web (Dart) code for a core concept using provided text and context.
    """
    # Ensure logs directory exists if running standalone or need to setup handlers again
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(current_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "research_agent.log")
    
    # Add file handler if not already present
    if not any(isinstance(h, logging.FileHandler) for h in logging.getLogger().handlers):
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)

    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("[DART-GEN] Error: API Key not found", file=sys.stderr)
        return {"error": "API Key not found"}

    # Use provided text or parse from path if needed
    if not paper_text and pdf_path:
        print(f"[DART-GEN] Parsing PDF: {pdf_path}")
        from agent.tools.pdf_parser import create_tool as create_pdf_parser
        pdf_parser = create_pdf_parser()
        pdf_data = pdf_parser.parse_pdf(pdf_path)
        paper_text = pdf_data["text"][:20000]

    if not paper_text:
        return {"error": "No paper text provided"}

    llm = ChatOpenAI(
        model="google/gemini-2.0-flash-001",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={"HTTP-Referer": "https://research-agent.com", "X-Title": "Research Agent"}
    )

    # Prepare Contextual Prompt
    context_str = ""
    if invention_context:
        context_str = f"""
        **TARGET INVENTION**: {invention_context.get('invention_title')}
        **VISUAL STEPS TO REPLICATE**:
        {chr(10).join(invention_context.get('solution_steps', []))}
        **VISUAL METAPHOR**: {invention_context.get('visual_metaphor')}
        """

    # Generate Code
    print(f"[DART-GEN] Generating Dart Code...")
    prompt = ChatPromptTemplate.from_messages([
        ("system", r"""You are an expert in Manim Web (Dart version by hugos29).
        Your task is to take a research paper's core invention and visualized it using the `manim_web` package.
        
        {context_info}
        
        **CRITICAL API DIFFERENCES (Python vs Dart):**
        
        1. **Method Names**:
           - `next_to(mob)` -> `nextToMobject(mob)`
           - `move_to(mob)` -> `moveToMobject(mob)`
           - `move_to(point)` -> `moveToPoint(point)`
           - `align_to(mob)` -> `alignToMobject(mob)`
           - `scale(n)` -> `scaleUniformly(n)`
        
        2. **Parameters**:
           - Use `buffer` instead of `buff` for `nextToMobject`.
           - `Transform(mobject, target: newMobject)` (target is named).
        
        3. **NO CHAINING (VERY IMPORTANT)**:
           - In this Dart library, methods like `scaleUniformly`, `shift`, `nextToMobject`, `setColor`, `rotate` return `void`.
           - **YOU CANNOT CHAIN METHODS.**
           - **YOU CANNOT CHAIN ON INITIALIZATION.**
           - **YOU CANNOT USE THE RESULT OF THESE METHODS.**
           
           **WRONG (WILL CRASH):**
           ```dart
           var x = Tex('A').scaleUniformly(2); // ERROR: x becomes void
           var y = Circle().shift(RIGHT); // ERROR: y becomes void
           x.nextToMobject(y).shift(UP); // ERROR: chaining void
           add(Tex('A').shift(UP)); // ERROR: add receives void
           ```
           
           **RIGHT:**
           ```dart
           var x = Tex('A'); 
           x.scaleUniformly(2);
           
           var y = Circle();
           y.shift(RIGHT);
           
           x.nextToMobject(y);
           x.shift(UP);
           
           add([x]); // Add the object, not the result of a method
           ```
           
           **ALSO WRONG (copy + chain):**
           ```dart
           // obj.copy() returns a Mobject, but .scaleUniformly() returns void!
           Transform(mob, target: mob.copy().scaleUniformly(0.5)); // ERROR
           Transform(mob, target: mob.copy().moveToMobject(other)); // ERROR: moveToMobject doesn't exist
           ```
           
           **RIGHT (Transform with copy):**
           ```dart
           var targetMob = mob.copy();
           targetMob.scaleUniformly(0.5);
           targetMob.shift(DOWN * 2);
           await playMany([Transform(mob, target: targetMob)]);
           ```
           
           **FORBIDDEN METHODS** (do not exist):
           - `moveToMobject` -> Use `moveToPoint(otherMob.getCenter())` or `nextToMobject(otherMob)`
           - `getBelow` -> Use `nextToMobject(mob, direction: DOWN)`
           - `getAbove` -> Use `nextToMobject(mob, direction: UP)`
           - `textString` -> Tex has no `textString` getter. Do not try to read back the text content.
        
        4. **Animations**:
           - Use `ShowCreation(mobject)` (NOT Create).
           - Use `FadeIn(mobject)` and `FadeOut(mobject)`.
           - **Multiple Animations**: Use `playMany([anim1, anim2])`.
           - **CRITICAL**: `playMany` expects `List<Animation>`. Do NOT pass a `List<List>`. 
           - **WRONG**: `playMany([ [FadeIn(x), FadeIn(y)] ])`
           - **RIGHT**: `playMany([FadeIn(x), FadeIn(y)])`
           
        5. **Math Functions & Constants**:
           - Use `sin()`, `cos()`, `pow()`, `sqrt()`, `exp()` directly (NO `Math.`).
           - Use `PI` (not `Math.PI` or `pi`).
           
        6. **Colors (STRICT LIST)**:
           - **ONLY USE**: `RED`, `GREEN`, `BLUE`, `YELLOW`, `WHITE`, `BLACK`, `ORANGE`, `PURPLE`, `GREY`.
           - **FORBIDDEN**: `LIME`, `TEAL`, `PINK`, `GOLD`, `MAROON`, `NAVY`.
           - If you need a custom color, use a hex string or define it, but try to stick to the basic constants.
        
        7. **Constructors & Parameters (CRITICAL - NAMED PARAMETERS ONLY)**:
           - **Axes**: 
              - **MUST USE NAMED PARAMETERS**: `xMin`, `xMax`, `yMin`, `yMax`.
              - **FORBIDDEN**: `x_range`, `y_range`, `xRange`, `yRange`.
              - **RIGHT**: `var axes = Axes(xMin: -5, xMax: 5, yMin: -3, yMax: 3);`
              
           - **FunctionGraph**: 
              - **MUST USE NAMED PARAMETER**: `function`.
              - **RIGHT**: `var graph = FunctionGraph(function: (x) => x * x, color: YELLOW);`
              
           - **Tex(String text, {{Color color = WHITE}})**: The text is a positional argument.
           - **Animation Constructors (Transform, ShowCreation, FadeIn, FadeOut)**:
              - **CRITICAL**: Each call returns a SINGLE `Animation` object.
              - **CRITICAL**: The FIRST argument (the mobject) MUST be POSITIONAL.
              - **RIGHT**: `ShowCreation(mob)`
              - **RIGHT**: `FadeIn(mob)`
           
           - **playMany(List<Animation> animations)**:
              - **CRITICAL**: Takes a FLAT LIST of Animation objects.
              - **WRONG**: `playMany([ [FadeIn(x), FadeIn(y)] ])` (List of List)
              - **WRONG**: `playMany(FadeIn(x))` (Not a list)
              - **RIGHT**: `playMany([FadeIn(x), FadeIn(y)])`
              - **RIGHT**: `playMany([ShowCreation(mobj)])`
        
        8. **Reference API (VERIFIED FROM SOURCE CODE - Ground Truth)**:
           - `Tex(String text, {{Color color = WHITE}})`
           - `Arrow({{required Vector3 start, required Vector3 end, double buff, Color color = WHITE}})` — ALL NAMED
           - `Line({{Vector3 start = RIGHT, Vector3 end = LEFT, double buff = 0, Color color = WHITE}})` — ALL NAMED
           - `Rectangle({{double width = 4.0, double height = 2.0, Color color = WHITE}})` — ALL NAMED
           - `Square({{double sideLength = 2.0, Color color = WHITE}})` — ALL NAMED
           - `Circle({{double radius = 1, Vector3 arcCenter = ORIGIN, Color color = WHITE}})` — ALL NAMED
           - `Dot(Vector3 pt, {{double radius, Color color = WHITE}})` — pt is POSITIONAL
           - `Axes({{double xMin, double xMax, double yMin, double yMax}})`
           - `FunctionGraph({{required double Function(double) function, Color color, double xMin, double xMax}})`
           - `Transform(Mobject mobject, {{Mobject? target, double runTime ...}})`
           - `ShowCreation(Mobject mobject, {{double runTime ...}})`
           - `FadeIn(Mobject mobject)` / `FadeOut(Mobject mobject)`
           - `Vector3(double x, double y, double z)`
           - **FORBIDDEN**: `Matrix` class (Does not exist). Use `Tex(r"\begin{{bmatrix}} ... \end{{bmatrix}}")`.
           - **FORBIDDEN**: `strokeWidth` as a constructor parameter for Arrow/Line. Arrow sets its own stroke internally.
           
        9. **Common Mistakes to AVOID**:
           - **NO**: `Arrow(start, end)` -> Use `Arrow(start: start, end: end)` (named params required).
           - **NO**: `Arrow(start: a, end: b, strokeWidth: 2)` -> `strokeWidth` is NOT a constructor param.
           - **NO**: `Matrix(...)` -> Use `Tex(r"\begin{{bmatrix}}...\end{{bmatrix}}")`.
           - **NO**: `add(mobj)` -> Use `add([mobj])` (List required).
           - **NO**: `obj.setColor(RED)` -> Use `obj.setColor(color: RED)`.
           - **NO**: `wait(Duration(...))` -> Use `wait(1.0)`.
           - **NO**: `fillOpacity: ...` or `opacity: ...` -> Use `color: RED.withTransparency(0.5)`.
           - **NO**: `buff: ...` in `nextToMobject` -> Use `buffer: ...`.
           - **NO**: `setStroke(1.0)` -> Use `setStroke(width: 1.0)`.
           - **NO**: `interpolateColor(...)` -> Do not use.
           - **NO**: `mob.height` or `mob.width` -> Use `setHeight(...)` or `setWidth(...)`.
           - **NO CHAINING**: `Tex("A").shift(UP)` -> `var t = Tex("A"); t.shift(UP);`
           - **NO SELF-REFERENCE**: `var line = Line(..., color: line.color)` -> Cannot reference variable in its own declaration.
           - **SIMPLICITY**: Keep the visualization SIMPLE. Prefer sequential steps with Tex labels, arrows, and basic shapes. Avoid complex loops generating many dynamic objects. A clear, step-by-step visual narrative is better than a complex programmatic one.
        
        **Structure:**
        
        ```dart
        import 'dart:async';
        import 'package:manim_web/manim.dart';
        
        class TemplateScene extends Scene {{
          @override
          FutureOr<void> preload() {{
              // ...
          }}
          
          @override
          FutureOr<void> construct() async {{
             // Logic based on the visual steps provided
          }}
        }}
        ```
        
        **REQUIREMENTS:**
        - Output ONLY the Dart code block.
        - STRICTLY follow the class name `TemplateScene`.
        - **NEVER CHAIN METHODS.**
        - **ALL CONSTRUCTORS USE NAMED PARAMETERS.**
        - **`add()` TAKES A LIST.**
        """),
        ("user", "Follow the visual breakdown of the invention to create a Manim animation.\n\nPaper Text:\n{paper_text}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "paper_text": paper_text,
        "context_info": context_str
    })
    
    # Text processing to extract code
    import re
    content = response.content.strip()
    match = re.search(r"```dart\n(.*?)```", content, re.DOTALL)
    if match:
        code = match.group(1).strip()
    else:
        # Fallback cleanup
        code = content.replace("```dart", "").replace("```", "").strip()
        
    print(f"[DART-GEN] Code generated ({len(code)} chars)")
    
    return {
        "success": True,
        "code": code,
        "language": "dart",
        "concept_title": invention_context.get('invention_title') if invention_context else "Dart Visualization"
    }


def fix_dart_code(broken_code: str, build_errors: str, attempt: int = 1):
    """
    Auto-correction agent: takes broken Dart code and build errors,
    asks the LLM to fix it, and returns corrected code.
    """
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return {"success": False, "error": "API Key not found"}

    llm = ChatOpenAI(
        model="google/gemini-2.0-flash-001",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={"HTTP-Referer": "https://research-agent.com", "X-Title": "Research Agent"}
    )

    print(f"[DART-FIX] Auto-correction attempt {attempt}...")
    sys.stdout.flush()
    
    fix_prompt = ChatPromptTemplate.from_messages([
        ("system", r"""You are a Dart code repair specialist for the `manim_web` package (by hugos29).
        
You are given Dart code that FAILED to compile, along with the exact compiler errors.
Your job is to FIX the code so it compiles successfully.

**VERIFIED API (from actual source code):**
- `Tex(String text, {{Color color = WHITE}})` — text is positional
- `Arrow({{required Vector3 start, required Vector3 end, double buff, Color color = WHITE}})` — ALL NAMED
- `Line({{Vector3 start = RIGHT, Vector3 end = LEFT, double buff = 0, Color color = WHITE}})` — ALL NAMED
- `Rectangle({{double width = 4.0, double height = 2.0, Color color = WHITE}})` — ALL NAMED
- `Square({{double sideLength = 2.0, Color color = WHITE}})` — ALL NAMED
- `Circle({{double radius = 1, Vector3 arcCenter = ORIGIN, Color color = WHITE}})` — ALL NAMED
- `Dot(Vector3 pt, {{double radius, Color color = WHITE}})` — pt is POSITIONAL
- `ShowCreation(Mobject mob)`, `FadeIn(Mobject mob)`, `FadeOut(Mobject mob)` — mob is POSITIONAL
- `Transform(Mobject mob, {{Mobject? target}})` — mob is POSITIONAL, target is NAMED
- `playMany(List<Animation> anims)` — takes a FLAT list
- `add(List<Mobject> mobs)` — takes a LIST
- `shift(Vector3)`, `scaleUniformly(double)`, `setColor({{required Color color}})` — ALL return VOID
- `nextToMobject(Mobject mob, {{Vector3 direction, double buffer}})` — use `buffer` not `buff`
- `setFill({{Color? color, List<Color>? colors}})` — NO opacity param. Use `color: RED.withTransparency(0.5)`
- `setStroke({{double? width}})` — named `width`
- `wait(double seconds)` — positional double

**COLORS**: ONLY use `RED`, `GREEN`, `BLUE`, `YELLOW`, `WHITE`, `BLACK`, `ORANGE`, `PURPLE`, `GREY`.

**CRITICAL RULES:**
1. Methods like `shift`, `scaleUniformly`, `setColor`, `rotate`, `nextToMobject` return VOID. 
   NEVER chain them: `Tex("A").shift(UP)` is WRONG. Do `var t = Tex("A"); t.shift(UP);`
2. NEVER do `obj.copy().method()` in a single expression. Always assign copy to a variable first.
3. `moveToMobject` does NOT exist. Use `moveToPoint(otherMob.getCenter())`.
4. `textString` does NOT exist on Tex.
5. `strokeWidth` is NOT a constructor parameter for Arrow/Line.
6. `height`/`width` getters do NOT exist. Use `setHeight()`/`setWidth()`.
7. `interpolateColor` does NOT exist.
8. Do NOT self-reference variables in declarations: `var line = Line(color: line.color)` is WRONG.

**Output ONLY the corrected Dart code block (```dart ... ```).**
Keep the same visual intent, just fix the compilation errors.
"""),
        ("user", """Here is the broken Dart code:

```dart
{broken_code}
```

Here are the build errors:
```
{build_errors}
```

Fix ALL the errors and return the complete corrected code.""")
    ])
    
    chain = fix_prompt | llm
    response = chain.invoke({
        "broken_code": broken_code,
        "build_errors": build_errors
    })
    
    # Extract code
    import re
    content = response.content.strip()
    match = re.search(r"```dart\n(.*?)```", content, re.DOTALL)
    if match:
        code = match.group(1).strip()
    else:
        code = content.replace("```dart", "").replace("```", "").strip()
    
    print(f"[DART-FIX] Fixed code generated ({len(code)} chars)")
    sys.stdout.flush()
    
    return {
        "success": True,
        "code": code,
        "language": "dart"
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', type=str, required=True, help='Path to PDF file')
    args = parser.parse_args()
    
    result = generate_dart_code(args.pdf)
    print(json.dumps(result))
