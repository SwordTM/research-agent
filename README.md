# Research Agent 🔬

AI-powered research paper analysis tool with automated Manim slide generation.

## Quick Start

### First Time Setup

```powershell
# Run the setup script
.\setup-env.ps1

# Edit the .env file with your API key
notepad python\.env
```

### Start Development Environment

**Option 1: Separate Windows (Recommended)**
```powershell
.\dev-start.ps1
```
This opens two PowerShell windows - one for MCP server, one for Next.js.

**Option 2: Single Terminal**
```powershell
.\dev-start-single.ps1
```
Runs both servers in the same terminal with combined output.

**Option 3: Using npm**
```powershell
npm run dev
```

**Option 4: Manual (Separate Terminals)**

Terminal 1 - MCP Server:
```powershell
cd python
.\venv\Scripts\Activate.ps1
python agent\mcp_server.py
```

Terminal 2 - Next.js:
```powershell
cd research-agent-web
npm run dev
```

### Access the Application

Open your browser to: **http://localhost:3000**

---

## Project Structure

```
ResearchAgent/
├── python/                          # Python backend
│   ├── agent/                       # LangChain agents and MCP server
│   │   ├── mcp_server.py           # MCP server entry point
│   │   ├── roadmap_agent.py        # Main orchestration agent
│   │   └── tools/                  # MCP tools
│   │       ├── pdf_parser.py       # PDF text extraction
│   │       └── concept_extractor.py # AI concept extraction
│   ├── visualization/               # Manim code generation
│   │   ├── manim_generator.py      # AI-powered code generator
│   │   └── manim_slides_generator.py # Slide templates
│   ├── models/                      # Pydantic data models
│   │   └── roadmap.py              # Concept, Roadmap models
│   ├── venv/                        # Python virtual environment
│   ├── requirements.txt             # Python dependencies
│   └── .env                         # Environment variables (API keys)
│
├── research-agent-web/              # Next.js frontend
│   ├── src/
│   │   ├── app/                    # Next.js app router
│   │   ├── components/             # React components
│   │   └── lib/                    # Utilities
│   ├── public/
│   │   └── slides/                 # Generated Manim slides (HTML)
│   └── package.json
│
├── dev-start.ps1                    # Development launcher (multi-window)
├── dev-start-single.ps1             # Development launcher (single terminal)
├── setup-env.ps1                    # Initial setup script
├── package.json                     # Root npm scripts
├── DEV_SETUP.md                     # Development guide
└── MANIM_SLIDES_IMPLEMENTATION_GUIDE.md  # Implementation details
```

---

## Features

- 📄 **PDF Parsing** - Extract text and structure from research papers
- 🧠 **AI Concept Extraction** - Identify key concepts using Gemini AI
- 🎬 **Automated Slide Generation** - Create Manim animations for each concept
- 🌐 **Web Interface** - Upload papers and view interactive roadmaps
- 🔄 **MCP Integration** - Standardized tool protocol for AI agents

---

## Available Scripts

### Root Directory

| Command | Description |
|---------|-------------|
| `npm run dev` | Start both MCP and Next.js (multi-window) |
| `npm run dev:single` | Start both servers (single terminal) |
| `npm run setup` | Run initial environment setup |
| `npm run web` | Start only Next.js dev server |
| `npm run mcp` | Start only MCP server |
| `npm run test:manim` | Test Manim slide generation |

### Python Directory

```powershell
cd python
.\venv\Scripts\Activate.ps1

# Start MCP server
python agent\mcp_server.py

# Analyze a PDF directly
python agent\roadmap_agent.py path\to\paper.pdf

# Test Manim generation
python test_manim.py
```

### Web Directory

```powershell
cd research-agent-web

# Development server
npm run dev

# Production build
npm run build
npm run start

# Linting
npm run lint
```

---

## Configuration

### Python Environment Variables

Create `python/.env`:

```env
# Required
GEMINI_API_KEY=your_api_key_here

# Optional
LOG_LEVEL=INFO
OUTPUT_DIR=../research-agent-web/public/slides
TEMP_DIR=temp_scenes
```

### Next.js Environment Variables

Create `research-agent-web/.env.local` (optional):

```env
NEXT_PUBLIC_API_URL=http://localhost:3000
```

---

## How It Works

```
┌─────────────┐
│  Upload PDF │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  PDF Parser     │  Extract text, metadata, structure
└──────┬──────────┘
       │
       ▼
┌─────────────────────┐
│ Concept Extractor   │  AI identifies key concepts
│ (Gemini 2.5 Pro)    │  - Architectures
└──────┬──────────────┘  - Techniques
       │                 - Algorithms
       ▼                 - Results
┌─────────────────────┐
│ Manim Code Generator│  AI generates Python code
│ (Gemini 2.5 Pro)    │  for each concept
└──────┬──────────────┘
       │
       ▼
┌─────────────────┐
│ Slide Renderer  │  manim-slides render & convert
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ HTML Slides     │  Interactive presentations
└─────────────────┘  with navigation
```

---

## Tech Stack

### Backend
- **Python 3.10+**
- **LangChain** - AI agent orchestration
- **Gemini 2.5 Pro** - Concept extraction & code generation
- **Manim** - Mathematical animation engine
- **Manim Slides** - Presentation framework
- **MCP** - Model Context Protocol
- **PyPDF2, pdfplumber** - PDF parsing

### Frontend
- **Next.js 16** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Radix UI** - Component primitives
- **Lucide React** - Icons

---

## Documentation

- **[DEV_SETUP.md](./DEV_SETUP.md)** - Complete development environment guide
- **[MANIM_SLIDES_IMPLEMENTATION_GUIDE.md](./MANIM_SLIDES_IMPLEMENTATION_GUIDE.md)** - Implementation details
- **[python/MCP_SETUP.md](./python/MCP_SETUP.md)** - MCP server documentation

---

## Troubleshooting

### "Virtual environment not found"
```powershell
cd python
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "GEMINI_API_KEY not found"
Edit `python/.env` and add your API key:
```env
GEMINI_API_KEY=your_actual_key_here
```

### "Port 3000 already in use"
```powershell
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### "FFmpeg not found"
Download and install FFmpeg from https://ffmpeg.org/download.html

---

## Development Workflow

1. **Start servers**: `.\dev-start.ps1`
2. **Open browser**: http://localhost:3000
3. **Upload PDF**: Use the web interface
4. **View concepts**: See extracted concepts in the roadmap
5. **View slides**: Click on concepts to see generated Manim slides

### Making Changes

- **Python code**: Restart MCP server (Ctrl+C, then restart)
- **Frontend code**: Hot reload is automatic
- **Manim templates**: Edit `python/visualization/manim_generator.py`

---

## License

MIT

---

## Support

For issues or questions, check:
- [DEV_SETUP.md](./DEV_SETUP.md) - Setup troubleshooting
- [MANIM_SLIDES_IMPLEMENTATION_GUIDE.md](./MANIM_SLIDES_IMPLEMENTATION_GUIDE.md) - Implementation details
- [python/MCP_SETUP.md](./python/MCP_SETUP.md) - MCP documentation
