# Research Agent - Python Backend

This directory contains the Python backend for the Research Agent application.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```
Then add your Gemini API key.

## Structure

- `agent/` - LangChain agent and MCP server
- `agent/tools/` - MCP tools for PDF parsing, concept extraction, etc.
- `visualization/` - Manim Slides generation
- `visualization/slides/` - Individual slide scene definitions
- `models/` - Data models for roadmap and concepts

## Usage

The Python scripts are called from Next.js API routes, not run directly.
