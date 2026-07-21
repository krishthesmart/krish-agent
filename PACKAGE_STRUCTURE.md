# Package Structure: krish-agent

Complete directory layout for the pip-installable package.

## Installation Options

### Option 1: Editable Install (Development)
```bash
pip install -e .
krish-agent add-tests src/main.py
```

### Option 2: Regular Install
```bash
pip install .
krish-agent add-tests src/main.py
```

## Directory Structure

```
krish-agent/
│
├── krish_agent/                    # Main package directory
│   ├── __init__.py                 # Package initialization, exports
│   ├── cli.py                      # Command-line interface
│   ├── worker.py                   # Worker agent (llama3.1:8b)
│   ├── reviewer.py                 # Reviewer agent (devstral:latest)
│   ├── tools.py                    # Shared utilities
│   ├── prompts.py                  # System prompts for agents
│   └── memory.py                   # Task memory and logging
│
├── setup.py                        # Setup configuration (legacy)
├── pyproject.toml                  # Modern Python project config
├── .gitignore                      # Git ignore rules
│
├── README.md                       # Main documentation
├── QUICKSTART.md                   # 5-minute setup guide
├── INSTALL.md                      # Installation guide
├── IMPLEMENTATION_GUIDE.md         # LLM integration options
├── PACKAGE_STRUCTURE.md            # This file
│
├── example_test_output.py          # Example Python file to test
└── .agent_memory.json              # Generated task history (git ignored)
```

## Key Files

### Package Core (`krish_agent/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `WorkerAgent`, `ReviewerAgent`, `AgentOrchestrator` |
| `cli.py` | CLI interface, installed as `krish-agent` command |
| `worker.py` | Fast agent using llama3.1:8b, generates tests |
| `reviewer.py` | Deep reviewer using devstral:latest, improves tests |
| `tools.py` | File I/O, command execution, JSON parsing |
| `prompts.py` | System prompts for both agents |
| `memory.py` | Persistent task logging to `.agent_memory.json` |

### Installation & Config

| File | Purpose |
|------|---------|
| `setup.py` | Legacy setup configuration |
| `pyproject.toml` | Modern Python project config (PEP 517/518) |
| `.gitignore` | Excludes `__pycache__`, `.venv`, `.agent_memory.json` |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Complete documentation |
| `QUICKSTART.md` | Get running in 5 minutes |
| `INSTALL.md` | Installation guide |
| `IMPLEMENTATION_GUIDE.md` | LLM integration options |
| `PACKAGE_STRUCTURE.md` | This file |

## Installation Commands

### From Local Directory

```bash
# Clone/download and install
cd krish-agent
pip install -e .              # Editable (development)
# or
pip install .                 # Regular (production)

# Verify
krish-agent --help
```

### From PyPI (After Publishing)

```bash
pip install krish-agent
krish-agent --help
```

## Entry Point

The package installs a console script command:

```bash
krish-agent  # Runs krish_agent.cli:main()
```

This is defined in `pyproject.toml`:
```toml
[project.scripts]
krish-agent = "krish_agent.cli:main"
```

## Usage After Installation

### Command Line

```bash
krish-agent add-tests src/main.py
krish-agent add-tests src/main.py --review
krish-agent add-tests src/main.py --apply-corrections
krish-agent history
krish-agent stats
```

### Python API

```python
# Direct imports from installed package
from krish_agent import WorkerAgent, ReviewerAgent, AgentOrchestrator

# Or import individual modules
from krish_agent.worker import WorkerAgent
from krish_agent.reviewer import ReviewerAgent
from krish_agent.cli import AgentOrchestrator
from krish_agent.memory import TaskMemory
from krish_agent.tools import read_file, write_file
```

## Dependencies

**Required:**
- Python 3.8+
- requests>=2.28.0 (for Ollama API)

**Optional (Development):**
- pytest>=7.0 (testing)
- black>=22.0 (formatting)
- flake8>=4.0 (linting)
- mypy>=0.950 (type checking)

Install with:
```bash
pip install -e ".[dev]"
```

## Development Workflow

1. **Install editable:**
   ```bash
   pip install -e .
   ```

2. **Make changes** to `krish_agent/` files

3. **Test immediately:**
   ```bash
   krish-agent add-tests example_test_output.py
   ```

4. **Format code:**
   ```bash
   black krish_agent/
   ```

5. **Check types:**
   ```bash
   mypy krish_agent/
   ```

## Generated Files

These are created at runtime and should be git-ignored:

- `.agent_memory.json` - Task history log
- `tests/` - Generated test files
- `__pycache__/` - Compiled Python
- `*.pyc` - Compiled modules

## Next Steps After Installation

1. **Read QUICKSTART.md:**
   ```bash
   # Setup Ollama and models
   ollama pull llama3.1:8b
   ollama pull devstral:latest
   ollama serve
   ```

2. **Run your first task:**
   ```bash
   krish-agent add-tests example_test_output.py --review
   ```

3. **Explore CLI:**
   ```bash
   krish-agent history
   krish-agent stats
   ```

4. **Use as library:**
   ```python
   from krish_agent import AgentOrchestrator
   orchestrator = AgentOrchestrator()
   result = orchestrator.add_tests("src/main.py", review=True)
   ```

## Troubleshooting

### Command not found
```bash
pip install -e .
which krish-agent
```

### Import error
```bash
python -c "from krish_agent import WorkerAgent; print('OK')"
```

### Dependencies missing
```bash
pip install -e .
```

See **INSTALL.md** for full troubleshooting guide.
