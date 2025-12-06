# Research Agent - Quick Reference Card

## 🚀 Starting Development

### First Time Only
```powershell
.\setup-env.ps1
notepad python\.env  # Add your GEMINI_API_KEY
```

### Every Time
```powershell
.\dev-start.ps1
# or
npm run dev
```

Then open: **http://localhost:3000**

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `python/agent/mcp_server.py` | MCP server entry point |
| `python/agent/roadmap_agent.py` | Main orchestration logic |
| `python/visualization/manim_generator.py` | Manim code generation |
| `research-agent-web/src/app/page.tsx` | Main web page |
| `python/.env` | API keys and config |

---

## 🛠️ Common Commands

### Start Servers
```powershell
.\dev-start.ps1              # Multi-window (recommended)
.\dev-start-single.ps1       # Single terminal
npm run dev                  # Using npm
```

### Python Only
```powershell
cd python
.\venv\Scripts\Activate.ps1
python agent\mcp_server.py
```

### Web Only
```powershell
cd research-agent-web
npm run dev
```

### Test Manim
```powershell
cd python
.\venv\Scripts\Activate.ps1
python test_manim.py
```

### Analyze PDF Directly
```powershell
cd python
.\venv\Scripts\Activate.ps1
python agent\roadmap_agent.py path\to\paper.pdf
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Virtual env not found | `cd python; python -m venv venv` |
| API key error | Edit `python/.env` |
| Port 3000 in use | `netstat -ano \| findstr :3000; taskkill /PID <PID> /F` |
| Module not found | `cd python; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt` |
| FFmpeg not found | Download from https://ffmpeg.org |

---

## 📊 Architecture Flow

```
PDF Upload → PDF Parser → Concept Extractor (AI) → 
Manim Code Generator (AI) → Slide Renderer → HTML Slides
```

---

## 🔑 Environment Variables

### python/.env
```env
GEMINI_API_KEY=your_key_here
LOG_LEVEL=INFO
OUTPUT_DIR=../research-agent-web/public/slides
TEMP_DIR=temp_scenes
```

---

## 📚 Documentation

- `README.md` - Project overview
- `DEV_SETUP.md` - Full development guide
- `MANIM_SLIDES_IMPLEMENTATION_GUIDE.md` - Implementation details
- `python/MCP_SETUP.md` - MCP server docs

---

## 🎯 Development Workflow

1. Start: `.\dev-start.ps1`
2. Open: http://localhost:3000
3. Upload: Research paper PDF
4. View: Generated concepts and slides
5. Edit: Make changes to code
6. Restart: MCP server if Python changes
7. Refresh: Browser if needed

---

## 🔍 Directory Structure

```
ResearchAgent/
├── python/              # Backend
│   ├── agent/          # MCP server & agents
│   ├── visualization/  # Manim generation
│   ├── models/         # Data models
│   └── venv/           # Virtual environment
├── research-agent-web/ # Frontend
│   ├── src/            # Next.js source
│   └── public/slides/  # Generated slides
└── *.ps1               # Development scripts
```

---

## 💡 Tips

- ✅ Always activate venv before running Python
- ✅ Check both server windows for errors
- ✅ Use `-ql` for fast Manim rendering during dev
- ✅ Keep `.env` files out of git
- ✅ Restart MCP server after Python changes
- ✅ Frontend hot-reloads automatically

---

## 🆘 Getting Help

1. Check error messages in both terminals
2. Review `DEV_SETUP.md` for detailed troubleshooting
3. Verify `.env` file has valid API key
4. Ensure all dependencies are installed
5. Check that ports aren't already in use
