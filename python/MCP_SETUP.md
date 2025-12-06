# MCP Server Setup Guide

## What is MCP?

Model Context Protocol (MCP) is a standard for exposing tools to AI models. It allows your LangChain agent to call Python functions as tools through a standardized interface.

## Running the MCP Server

### 1. Activate Virtual Environment

```powershell
cd python
.\venv\Scripts\Activate.ps1
```

### 2. Set Environment Variables

Make sure your `.env` file has:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Run the MCP Server

```powershell
python agent/mcp_server.py
```

The server will start and listen for tool calls via stdio (standard input/output).

## Using MCP Tools

### Option 1: Direct Python Usage

You can use the tools directly in Python without MCP:

```python
from agent.tools.pdf_parser import PDFParserTool
from agent.tools.concept_extractor import ConceptExtractorTool

# Parse PDF
parser = PDFParserTool()
result = parser.parse_pdf("path/to/paper.pdf")
print(result["text"])

# Extract concepts
extractor = ConceptExtractorTool()
concepts = extractor.extract_concepts(result["text"])
for concept in concepts:
    print(f"{concept.title}: {concept.description}")
```

### Option 2: Via LangChain Agent

The `roadmap_agent.py` already integrates the tools:

```python
from agent.roadmap_agent import create_agent

agent = create_agent()
roadmap = agent.analyze_paper("path/to/paper.pdf")
print(roadmap.concepts)
```

### Option 3: Via MCP Protocol

For external applications that support MCP:

1. Start the MCP server: `python agent/mcp_server.py`
2. Connect your MCP client to stdio
3. Call tools using the MCP protocol

## Available Tools

### `parse_pdf`
- **Input**: `pdf_path` (string)
- **Output**: Dictionary with text, metadata, pages, tables
- **Example**:
  ```json
  {
    "pdf_path": "uploads/paper.pdf"
  }
  ```

### `extract_concepts`
- **Input**: 
  - `paper_text` (string)
  - `max_concepts` (integer, optional, default: 10)
- **Output**: List of Concept objects
- **Example**:
  ```json
  {
    "paper_text": "Full paper text here...",
    "max_concepts": 5
  }
  ```

## Testing the Tools

### Test PDF Parser

```powershell
python -c "from agent.tools.pdf_parser import PDFParserTool; tool = PDFParserTool(); print(tool.parse_pdf('test.pdf'))"
```

### Test Concept Extractor

```python
from agent.tools.concept_extractor import ConceptExtractorTool

extractor = ConceptExtractorTool()
test_text = """
This paper introduces a novel CNN architecture...
"""
concepts = extractor.extract_concepts(test_text, max_concepts=3)
for c in concepts:
    print(f"{c.title}: {c.description}")
```

## Integration with Next.js

The Next.js API routes call Python scripts directly using `child_process.spawn()`. The MCP server is optional for this setup but provides a standardized interface if you want to expose tools to other applications.

## Troubleshooting

### Import Errors
Make sure you're in the virtual environment:
```powershell
.\venv\Scripts\Activate.ps1
```

### API Key Errors
Check that `.env` file exists and has valid `GEMINI_API_KEY`.

### Model Name Errors
Use valid model names:
- `gemini-1.5-pro` (recommended)
- `gemini-1.5-flash`
- `gemini-2.0-flash-exp` (experimental)

**NOT** `gemini-2.5-pro` (doesn't exist)
