# Where to See the Debugging Logs

## Important Clarification

The **MCP server window will NOT show the debugging logs** during PDF analysis. Here's why:

## Current Architecture

```
User uploads PDF
    ↓
Next.js API Route (/api/analyze)
    ↓
Spawns Python subprocess directly
    ↓
roadmap_agent.py executes
    ↓
Logs appear in Next.js terminal
```

**The MCP server is NOT being used** for the PDF analysis workflow. It's available for external integrations but the Next.js app calls the Python script directly.

## Where to Look for Logs

### ✅ **Next.js Server Window** (PID: 18508)

This is where you'll see ALL the debugging output:

```
======================================================================
[NEXT.JS] Spawning Python script...
[NEXT.JS] Python: C:\...\python\venv\Scripts\python.exe
[NEXT.JS] Script: C:\...\python\agent\roadmap_agent.py
[NEXT.JS] Args: C:\...\uploads\paper.pdf
======================================================================

======================================================================
[ROADMAP AGENT] Starting paper analysis...
======================================================================

[1/4] Parsing PDF: C:\...\uploads\paper.pdf
      -> Opening PDF file...
      -> Found 15 pages
      -> Processing page 1/15...
      ...

[2/4] Extracting concepts using AI...
      -> Calling Gemini AI to analyze paper...
      ...

[3/4] Generating paper summary...
      ...

[4/4] Generating Manim slides for 6 concepts...

[SLIDE 1/6] Processing: Transformer Architecture
              -> Generating Manim code with AI...
              ...

======================================================================
[NEXT.JS] Python script finished with code: 0
======================================================================
```

### ❌ **MCP Server Window** (PID: 7008)

This window will only show:
```
C:\...\python\venv\lib\site-packages\google\api_core\_python_version_support.py:266: 
FutureWarning: You are using a Python version (3.10.11) which Google will stop 
supporting...
```

And nothing else during PDF analysis, because it's not being called.

## Why Two Windows?

| Window | Purpose | What You'll See |
|--------|---------|-----------------|
| **Next.js Server** | Handles web requests, spawns Python | PDF analysis logs, slide generation progress |
| **MCP Server** | Exposes tools via MCP protocol | Nothing during normal operation (optional service) |

## What the MCP Server Is For

The MCP server is useful for:
- External AI assistants that support MCP protocol
- Direct tool calls from other applications
- Testing tools independently

But for the web app, it's **not needed** - the Next.js API routes call Python directly.

## How to See the Logs

1. **Upload a PDF** via the web interface at http://localhost:3000
2. **Watch the Next.js window** (the one with PID 18508)
3. **You'll see real-time progress** as the Python script runs

## Example Output in Next.js Window

When you upload a PDF, you should see:

```
POST /api/upload 200 in 45ms
POST /api/analyze 200 in 125000ms

======================================================================
[NEXT.JS] Spawning Python script...
[NEXT.JS] Python: C:\Users\BUTA0001\Desktop\Machine Learning Practice\ResearchAgent\python\venv\Scripts\python.exe
[NEXT.JS] Script: C:\Users\BUTA0001\Desktop\Machine Learning Practice\ResearchAgent\python\agent\roadmap_agent.py
[NEXT.JS] Args: C:\Users\BUTA0001\Desktop\Machine Learning Practice\ResearchAgent\research-agent-web\uploads\1733321234567-paper.pdf
======================================================================

======================================================================
[ROADMAP AGENT] Starting paper analysis...
======================================================================

[1/4] Parsing PDF: C:\Users\BUTA0001\Desktop\Machine Learning Practice\ResearchAgent\research-agent-web\uploads\1733321234567-paper.pdf
      -> Opening PDF file...
      -> Found 12 pages
      -> Processing page 1/12...
      -> Processing page 5/12...
      -> Processing page 10/12...
      -> Processing page 12/12...
      -> Extracting metadata...
      -> PDF parsing complete
      -> Extracted 38450 characters

[2/4] Extracting concepts using AI...
      -> Calling Gemini AI to analyze paper...
      -> Analyzing 15000 characters...
      -> AI response received, parsing concepts...
      -> Found 5 concepts
      1. Neural Network Architecture (architecture)
      2. Backpropagation Algorithm (algorithm)
      3. Gradient Descent (technique)
      4. Activation Functions (technique)
      5. Training Methodology (methodology)

[3/4] Generating paper summary...
      -> Summary generated (425 chars)

[4/4] Generating Manim slides for 5 concepts...
      This may take several minutes...

[SLIDE 1/5] Processing: Neural Network Architecture
              Type: architecture
              ID: neural_network_architecture
              -> Generating Manim code with AI...
                 [AI] Requesting code from Gemini 2.5 Pro...
                 [AI] Response received, extracting code...
              -> Code generated (2650 chars)
              -> Rendering animation (this may take 30-60s)...
                 [RENDER] Code written to: scene_neural_network_architecture.py
                 [RENDER] Step 1/2: Rendering Manim scene...
                 [RENDER] Executing: manim-slides render scene_neural_network_architecture.py ConceptScene -ql
                 [RENDER] Scene rendered successfully
                 [RENDER] Step 2/2: Converting to HTML...
                 [RENDER] Executing: manim-slides convert ConceptScene neural_network_architecture.html --force
                 [RENDER] HTML conversion complete
                 [RENDER] Output file: C:\...\public\slides\neural_network_architecture.html
              -> SUCCESS! Slide URL: /slides/neural_network_architecture.html

[SLIDE 2/5] Processing: Backpropagation Algorithm
...

======================================================================
[NEXT.JS] Python script finished with code: 0
======================================================================
```

## Summary

- ✅ **Look at the Next.js window** for all debugging output
- ❌ **Don't expect logs in the MCP server window** (it's not being used)
- 🔄 **The changes are already in place** - just upload a PDF to see them
- 📊 **Real-time streaming** - logs appear as they happen, not at the end

## Optional: Using MCP Server Directly

If you want to test the MCP server directly (without the web interface):

```powershell
cd python
.\venv\Scripts\Activate.ps1
python agent\roadmap_agent.py path\to\paper.pdf
```

This will show the logs directly in your terminal.
