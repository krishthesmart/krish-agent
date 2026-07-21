# krish-agent Complete Package Index

All files for the pip-installable dual-agent coding system.

## Quick Start (Copy & Paste)

```bash
# 1. Install
pip install -e .

# 2. Verify
krish-agent --help

# 3. Setup Ollama (separate terminal)
ollama pull llama3.1:8b devstral:latest
ollama serve

# 4. Run (back in project terminal)
krish-agent add-tests example_test_output.py --review
```

## File Directory

### Package Core (`krish_agent/`)

**Main Python modules - everything is here**

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 20 | Package init, exports main classes |
| `cli.py` | 210 | CLI interface, orchestrator |
| `worker.py` | 260 | Fast worker agent (llama3.1:8b) |
| `reviewer.py` | 190 | Deep reviewer agent (devstral:latest) |
| `tools.py` | 210 | Utilities (files, git, commands) |
| `prompts.py` | 80 | System prompts for agents |
| `memory.py` | 110 | Task logging to JSON |

**Total core: ~1,080 lines**

### Installation & Config

| File | Purpose |
|------|---------|
| `setup.py` | Legacy setuptools config |
| `pyproject.toml` | Modern Python packaging (PEP 517) |
| `.gitignore` | Standard Python .gitignore |

### Documentation

| File | Audience | Read Time |
|------|----------|-----------|
| `README.md` | Everyone | 15 min |
| `QUICKSTART.md` | New users | 5 min |
| `INSTALL.md` | Installers | 10 min |
| `PACKAGE_STRUCTURE.md` | Developers | 8 min |
| `IMPLEMENTATION_GUIDE.md` | Integrators | 12 min |
| `RELEASE_NOTES.md` | Operators | 5 min |
| `INDEX.md` | This file | 5 min |

### Examples & Test Files

| File | Purpose |
|------|---------|
| `example_test_output.py` | Sample Python file to test |

## Installation Options

### Option 1: Editable Install (Development)
```bash
cd krish-agent
pip install -e .
krish-agent add-tests example_test_output.py
```

### Option 2: Regular Install (Production)
```bash
cd krish-agent
pip install .
krish-agent add-tests example_test_output.py
```

### Option 3: PyPI (After Publishing)
```bash
pip install krish-agent
krish-agent add-tests example_test_output.py
```

## Usage Guide

### Command Line

After `pip install -e .`, these commands work anywhere:

```bash
# Generate tests (worker only)
krish-agent add-tests src/main.py

# Generate + review
krish-agent add-tests src/main.py --review

# Generate + review + auto-fix
krish-agent add-tests src/main.py --apply-corrections

# View history
krish-agent history

# Show stats
krish-agent stats

# Export runs
krish-agent export-memory runs.json
```

### Python API

```python
# Import installed package
from krish_agent import WorkerAgent, ReviewerAgent, AgentOrchestrator

# Use it
orchestrator = AgentOrchestrator()
result = orchestrator.add_tests("src/main.py", review=True)
print(result)
```

## Models Used

- **Worker**: `llama3.1:8b` (Ollama)
  - Speed: 2-5 seconds
  - VRAM: ~8GB
  - Purpose: Fast test generation

- **Reviewer**: `devstral:latest` (Ollama)
  - Speed: 10-30 seconds
  - VRAM: ~30GB (or 16GB with quantization)
  - Purpose: Deep code quality review

Both via Ollama at `http://localhost:11434`

## Documentation Map

**Start here:**
1. README.md - Project overview
2. QUICKSTART.md - Setup in 5 minutes
3. Run: `pip install -e .` then `krish-agent add-tests example_test_output.py`

**Then explore:**
- INSTALL.md - Detailed installation
- PACKAGE_STRUCTURE.md - How everything fits together
- IMPLEMENTATION_GUIDE.md - Other LLM integration options (if needed)

**Reference:**
- RELEASE_NOTES.md - What's in this release
- INDEX.md - This file

## Architecture

```
User Input
    ↓
CLI (cli.py) - AgentOrchestrator
    ↓
    ├─→ Worker Agent (worker.py)
    │   ├─→ llama3.1:8b (Ollama API)
    │   ├─→ Analyze files (tools.py)
    │   ├─→ Generate tests
    │   └─→ Run pytest
    │
    ├─→ [Optional] Reviewer Agent (reviewer.py)
    │   ├─→ devstral:latest (Ollama API)
    │   ├─→ Review quality
    │   ├─→ Propose improvements
    │   └─→ Apply corrections
    │
    └─→ Memory (memory.py)
        └─→ Save to .agent_memory.json

Output: JSON summary + modified files
```

## Dependencies

**Required:**
- Python 3.8+
- requests>=2.28.0 (for Ollama API)

**Optional Development:**
- pytest>=7.0
- black>=22.0 (code formatter)
- flake8>=4.0 (linter)
- mypy>=0.950 (type checker)

**External:**
- Ollama (https://ollama.ai)
- llama3.1:8b model
- devstral:latest model

## File Sizes (Approximate)

| Component | Size |
|-----------|------|
| Core package | ~20 KB |
| Installation files | ~2 KB |
| Documentation | ~80 KB |
| Example files | ~5 KB |
| **Total** | **~107 KB** |

## Development Workflow

```
1. pip install -e .
   ↓
2. Make changes to krish_agent/
   ↓
3. Test immediately: krish-agent add-tests example_test_output.py
   ↓
4. Format: black krish_agent/
   ↓
5. Lint: flake8 krish_agent/
   ↓
6. Type check: mypy krish_agent/
```

## Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| Command not found | See INSTALL.md > Troubleshooting |
| Can't connect to Ollama | ollama serve in another terminal |
| Model not found | ollama pull llama3.1:8b |
| Import error | pip install -e . |
| Test failures | Normal - use --review flag for fixes |

## Next Steps

1. **Read** QUICKSTART.md (5 minutes)
2. **Install** Ollama and pull models (5-10 minutes)
3. **Run** `pip install -e .` in this directory (1 minute)
4. **Test** with `krish-agent add-tests example_test_output.py` (30 seconds)
5. **Explore** with `krish-agent history` and `krish-agent stats`

## Support

For detailed help:
- Installation issues → INSTALL.md
- Getting started → QUICKSTART.md or README.md
- API/code issues → PACKAGE_STRUCTURE.md
- Integration options → IMPLEMENTATION_GUIDE.md

---

**Version:** 0.1.0  
**Author:** Arul Meiyappan Kannappan  
**Email:** arulmeiyappankannappan@gmail.com  
**License:** MIT
