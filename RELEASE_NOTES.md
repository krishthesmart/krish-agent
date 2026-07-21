# Release Notes: krish-agent v0.1.0

Dual-agent AI coding system for automated testing and code review. Now pip-installable!

## Installation

### Quick Start (3 steps)

```bash
# 1. Install the package
pip install -e .

# 2. Verify
krish-agent --help

# 3. Run it
krish-agent add-tests example_test_output.py --review
```

See **INSTALL.md** for detailed instructions.

## What's Included

### Package Structure

```
krish_agent/
├── __init__.py       # Package exports
├── cli.py            # Command-line interface
├── worker.py         # llama3.1:8b worker agent
├── reviewer.py       # devstral:latest reviewer agent
├── tools.py          # Utilities
├── prompts.py        # System prompts
└── memory.py         # Task logging
```

### Installation Files

- `setup.py` — Legacy setup config
- `pyproject.toml` — Modern Python packaging (PEP 517/518)
- `.gitignore` — Standard Python gitignore

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `QUICKSTART.md` | 5-minute setup guide |
| `INSTALL.md` | Installation guide |
| `PACKAGE_STRUCTURE.md` | Package layout |
| `IMPLEMENTATION_GUIDE.md` | LLM integration options |

## Models

- **Worker**: llama3.1:8b (fast, ~2-5s)
- **Reviewer**: devstral:latest (powerful, ~10-30s)
- Both via Ollama at http://localhost:11434

## Key Features

✓ **Pip-installable** — Install once, use anywhere  
✓ **CLI tool** — `krish-agent` command  
✓ **Python API** — Import and use in code  
✓ **Real Ollama integration** — Connects to running Ollama server  
✓ **Task memory** — Persistent JSON logging to `.agent_memory.json`  
✓ **Clean architecture** — Worker and reviewer cleanly separated  
✓ **No heavy frameworks** — Pure Python, minimal dependencies  

## Commands After Installation

```bash
# Generate tests (worker only)
krish-agent add-tests src/main.py

# Generate tests + deep review
krish-agent add-tests src/main.py --review

# Generate, review, auto-fix
krish-agent add-tests src/main.py --apply-corrections

# View task history
krish-agent history

# Show statistics
krish-agent stats

# Export runs
krish-agent export-memory runs.json
```

## Python API After Installation

```python
from krish_agent import WorkerAgent, ReviewerAgent, AgentOrchestrator

# Use orchestrator
orchestrator = AgentOrchestrator(repo_root=".")
result = orchestrator.add_tests("src/main.py", review=True)

# Or use agents directly
worker = WorkerAgent()
result = worker.generate_tests("src/main.py", ".")
```

## Dependencies

**Required:**
- Python 3.8+
- requests>=2.28.0

**Optional (Development):**
- pytest, black, flake8, mypy

Install all:
```bash
pip install -e ".[dev]"
```

## Roadmap for v0.2.0

- [ ] Unit tests
- [ ] Type hints (mypy clean)
- [ ] GitHub Actions CI
- [ ] PyPI publication
- [ ] Web dashboard for memory
- [ ] GitHub integration
- [ ] Support for other test frameworks

## Known Limitations

- Ollama server must be running at http://localhost:11434
- Both models should be pulled: `ollama pull llama3.1:8b devstral:latest`
- Tests are generated but may require review/fixes
- Works best with 16GB+ GPU VRAM for both models

## Troubleshooting

See **INSTALL.md** for detailed troubleshooting, or run:

```bash
# Test installation
python -c "from krish_agent import WorkerAgent; print('OK')"

# Check CLI
krish-agent --help

# Check Ollama connection
curl http://localhost:11434/api/tags
```

## Documentation

- **New to the project?** Start with **QUICKSTART.md** or **README.md**
- **Installing it?** See **INSTALL.md**
- **Want to develop?** See **PACKAGE_STRUCTURE.md**
- **Integration options?** See **IMPLEMENTATION_GUIDE.md**

## Contributing

Fork, branch, edit, test, and submit PRs to improve:
- Agent prompts
- Error handling
- Additional agents
- Test frameworks support
- Documentation

## License

MIT

## Contact

Author: Arul Meiyappan Kannappan  
Email: arulmeiyappankannappan@gmail.com

---

## Change Log

### v0.1.0 (First Release)
- ✨ Dual-agent system with worker + reviewer
- ✨ Real Ollama integration (llama3.1:8b + devstral:latest)
- ✨ Pip-installable package structure
- ✨ CLI tool with 5 commands
- ✨ Task memory and statistics
- ✨ Comprehensive documentation
