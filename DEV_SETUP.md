# Development Environment Setup

This guide will help you run the complete Research Agent development environment with both the MCP server and the Next.js web application running simultaneously.

## Prerequisites

### 1. Python Environment
- Python 3.10 or higher
- Virtual environment activated

### 2. Node.js Environment
- Node.js 18 or higher
- npm or yarn

### 3. System Dependencies
- **FFmpeg** (for Manim video rendering)
- **LaTeX** (optional, for mathematical formulas in Manim)

---

## Quick Start

### Option 1: Using the Development Script (Recommended)

Run everything with a single command:

```powershell
# From the root directory
.\dev-start.ps1
```

This will:
1. Activate the Python virtual environment
2. Start the MCP server in the background
3. Start the Next.js development server
4. Open your browser to http://localhost:3000

### Option 2: Manual Setup

#### Terminal 1: MCP Server
```powershell
cd python
.\venv\Scripts\Activate.ps1
python agent\mcp_server.py
```

#### Terminal 2: Next.js Dev Server
```powershell
cd research-agent-web
npm run dev
```

---

## Detailed Setup Instructions

### Step 1: Python Environment Setup

```powershell
# Navigate to python directory
cd python

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy .env.example to .env and add your API key
```

**Create `.env` file in `python/` directory:**
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### Step 2: Next.js Environment Setup

```powershell
# Navigate to web directory
cd research-agent-web

# Install dependencies
npm install

# Create .env.local file (if needed)
```

**Create `.env.local` file in `research-agent-web/` directory (optional):**
```env
NEXT_PUBLIC_API_URL=http://localhost:3000
```

### Step 3: Verify Installation

#### Test Python Environment
```powershell
cd python
.\venv\Scripts\Activate.ps1
python -c "import manim; import langchain; print('Python environment OK')"
```

#### Test Node Environment
```powershell
cd research-agent-web
npm run build
```

---

## Running the Development Environment

### Method 1: PowerShell Script (Automated)

I've created a PowerShell script that manages both processes:

```powershell
# From the root directory
.\dev-start.ps1
```

**What it does:**
- Checks if virtual environment exists
- Activates Python venv
- Starts MCP server in background
- Starts Next.js dev server
- Provides graceful shutdown (Ctrl+C stops both)

### Method 2: Separate Terminals (Manual Control)

**Terminal 1 - MCP Server:**
```powershell
cd "C:\Users\BUTA0001\Desktop\Machine Learning Practice\ResearchAgent\python"
.\venv\Scripts\Activate.ps1
python agent\mcp_server.py
```

**Terminal 2 - Next.js:**
```powershell
cd "C:\Users\BUTA0001\Desktop\Machine Learning Practice\ResearchAgent\research-agent-web"
npm run dev
```

### Method 3: Using Windows Terminal (Split Panes)

If you use Windows Terminal, you can create a profile:

```json
{
  "name": "Research Agent Dev",
  "commandline": "powershell.exe -NoExit -Command \"cd 'C:\\Users\\BUTA0001\\Desktop\\Machine Learning Practice\\ResearchAgent'; .\\dev-start.ps1\""
}
```

---

## Development Workflow

### Starting Development
```powershell
# Start both servers
.\dev-start.ps1

# Wait for both to be ready:
# - MCP Server: "MCP server running on stdio"
# - Next.js: "Ready on http://localhost:3000"
```

### Testing the Integration

1. **Upload a PDF** via the web interface
2. **Check MCP server logs** to see tool calls
3. **View generated slides** in `/slides` directory

### Making Changes

#### Python Changes (MCP Server, Tools, Manim)
- Edit files in `python/` directory
- Restart MCP server: `Ctrl+C` in Terminal 1, then `python agent\mcp_server.py`
- Changes to tools/agents require server restart

#### Next.js Changes (Frontend)
- Edit files in `research-agent-web/src/`
- Hot reload is automatic (no restart needed)
- API routes require page refresh

### Stopping Development
```powershell
# In the terminal running dev-start.ps1
Ctrl+C

# Or manually stop each terminal
# Terminal 1 (MCP): Ctrl+C
# Terminal 2 (Next.js): Ctrl+C
```

---

## Port Configuration

| Service | Port | URL |
|---------|------|-----|
| Next.js Dev Server | 3000 | http://localhost:3000 |
| MCP Server | stdio | N/A (uses stdin/stdout) |

**Note:** The MCP server doesn't use HTTP ports; it communicates via standard input/output.

---

## Troubleshooting

### Issue: "Virtual environment not found"

```powershell
cd python
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "GEMINI_API_KEY not found"

Create `python/.env`:
```env
GEMINI_API_KEY=your_key_here
```

### Issue: "Module not found" errors

```powershell
# Ensure venv is activated
cd python
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Port 3000 already in use"

```powershell
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use a different port
cd research-agent-web
npm run dev -- -p 3001
```

### Issue: "FFmpeg not found" (Manim rendering fails)

Install FFmpeg:
1. Download from https://ffmpeg.org/download.html
2. Add to PATH
3. Verify: `ffmpeg -version`

### Issue: MCP server not responding

```powershell
# Check if server is running
Get-Process python

# Check logs for errors
cd python
python agent\mcp_server.py
# Look for error messages
```

---

## Advanced Configuration

### Running in Production Mode

#### Build Next.js
```powershell
cd research-agent-web
npm run build
npm run start
```

#### Run MCP Server with PM2 (Process Manager)
```powershell
# Install PM2 globally
npm install -g pm2

# Start MCP server
cd python
pm2 start agent\mcp_server.py --name mcp-server --interpreter python
```

### Environment Variables

#### Python (.env)
```env
GEMINI_API_KEY=your_key_here
LOG_LEVEL=INFO
OUTPUT_DIR=../research-agent-web/public/slides
TEMP_DIR=temp_scenes
```

#### Next.js (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:3000
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

---

## Development Scripts Reference

### PowerShell Scripts

| Script | Description |
|--------|-------------|
| `dev-start.ps1` | Start both MCP and Next.js servers |
| `dev-stop.ps1` | Stop all development servers |
| `setup-env.ps1` | Initial environment setup |

### NPM Scripts (in research-agent-web/)

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Next.js dev server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |

### Python Scripts (in python/)

| Command | Description |
|---------|-------------|
| `python agent\mcp_server.py` | Start MCP server |
| `python agent\roadmap_agent.py <pdf>` | Analyze a PDF directly |
| `python test_manim.py` | Test Manim generation |

---

## Monitoring and Logs

### View MCP Server Logs
```powershell
# If running in foreground, logs appear in terminal
# If running in background, redirect to file:
python agent\mcp_server.py > logs\mcp.log 2>&1
```

### View Next.js Logs
```powershell
# Logs appear in terminal automatically
# Or check browser console for client-side logs
```

### Check Manim Rendering Output
```powershell
# Rendered files are in:
cd temp_scenes\media

# Final HTML slides are in:
cd ..\research-agent-web\public\slides
```

---

## Testing

### Test MCP Server
```powershell
cd python
.\venv\Scripts\Activate.ps1

# Test PDF parser
python -c "from agent.tools.pdf_parser import PDFParserTool; print('PDF Parser OK')"

# Test concept extractor
python -c "from agent.tools.concept_extractor import ConceptExtractorTool; print('Concept Extractor OK')"
```

### Test Next.js
```powershell
cd research-agent-web
npm run build
```

### End-to-End Test
1. Start both servers
2. Navigate to http://localhost:3000
3. Upload a test PDF
4. Verify concepts are extracted
5. Check that slides are generated in `public/slides/`

---

## Best Practices

### Development
- ✅ Always activate virtual environment before running Python scripts
- ✅ Use separate terminals for better log visibility
- ✅ Keep `.env` files out of version control
- ✅ Test changes incrementally

### Performance
- ✅ Use `-ql` (low quality) for Manim during development
- ✅ Cache generated slides to avoid re-rendering
- ✅ Limit concept extraction to 5-10 concepts during testing

### Debugging
- ✅ Check both server logs when issues occur
- ✅ Use browser DevTools for frontend debugging
- ✅ Add print statements in Python for debugging
- ✅ Use React DevTools for component inspection

---

## Next Steps

After setting up the development environment:

1. **Read the Implementation Guide**: `MANIM_SLIDES_IMPLEMENTATION_GUIDE.md`
2. **Explore the codebase**: Start with `python/agent/roadmap_agent.py`
3. **Test with a sample PDF**: Upload a research paper
4. **Customize slide templates**: Edit `python/visualization/manim_generator.py`
5. **Enhance the UI**: Modify components in `research-agent-web/src/components/`

---

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the MCP setup guide: `python/MCP_SETUP.md`
- Review the implementation guide: `MANIM_SLIDES_IMPLEMENTATION_GUIDE.md`
