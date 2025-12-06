"""Test script to verify the Python environment is set up correctly."""

import sys
import os

print("=" * 60)
print("Research Agent - Environment Test")
print("=" * 60)

# Test 1: Check Python version
print(f"\n✓ Python version: {sys.version}")

# Test 2: Check imports
print("\nTesting imports...")
try:
    import langchain
    print("✓ LangChain imported successfully")
except ImportError as e:
    print(f"✗ LangChain import failed: {e}")

try:
    import mcp
    print("✓ MCP imported successfully")
except ImportError as e:
    print(f"✗ MCP import failed: {e}")

try:
    import manim
    print("✓ Manim imported successfully")
except ImportError as e:
    print(f"✗ Manim import failed: {e}")

try:
    from manim_slides import Slide
    print("✓ Manim Slides imported successfully")
except ImportError as e:
    print(f"✗ Manim Slides import failed: {e}")

try:
    import PyPDF2
    import pdfplumber
    print("✓ PDF libraries imported successfully")
except ImportError as e:
    print(f"✗ PDF libraries import failed: {e}")

# Test 3: Check environment variables
print("\nChecking environment variables...")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"✓ GEMINI_API_KEY is set (length: {len(api_key)})")
else:
    print("✗ GEMINI_API_KEY is not set")
    print("  Please create a .env file with your API key")

# Test 4: Test tools
print("\nTesting tools...")
try:
    from agent.tools.pdf_parser import PDFParserTool
    parser = PDFParserTool()
    print("✓ PDF Parser tool initialized")
except Exception as e:
    print(f"✗ PDF Parser tool failed: {e}")

try:
    from agent.tools.concept_extractor import ConceptExtractorTool
    if api_key:
        extractor = ConceptExtractorTool()
        print("✓ Concept Extractor tool initialized")
    else:
        print("⚠ Concept Extractor skipped (no API key)")
except Exception as e:
    print(f"✗ Concept Extractor tool failed: {e}")

# Test 5: Test agent
print("\nTesting agent...")
try:
    from agent.roadmap_agent import RoadmapAgent
    if api_key:
        agent = RoadmapAgent()
        print("✓ Roadmap Agent initialized")
    else:
        print("⚠ Roadmap Agent skipped (no API key)")
except Exception as e:
    print(f"✗ Roadmap Agent failed: {e}")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Make sure .env file has your GEMINI_API_KEY")
print("2. Test with a real PDF: python agent/roadmap_agent.py")
print("3. Run MCP server: python agent/mcp_server.py")
print("4. Check MCP_SETUP.md for detailed usage")
