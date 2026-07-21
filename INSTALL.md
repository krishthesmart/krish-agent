# Installation Guide: krish-agent via pip

## Local Development Installation

### Option 1: Editable Install (Recommended for Development)

```bash
# Clone or download the repository
cd krish-agent

# Install in editable mode with dependencies
pip install -e .

# Verify installation
krish-agent --help
```

This creates a symlink to the package, so changes you make are immediately reflected.

### Option 2: Regular Install

```bash
cd krish-agent
pip install .
```

## PyPI Installation (Once Published)

```bash
# Install from PyPI
pip install krish-agent

# Verify
krish-agent --help
```

## Usage After Installation

### Command-line Tool

```bash
# Generate tests for a file
krish-agent add-tests src/main.py

# Generate tests and review
krish-agent add-tests src/main.py --review

# Generate, review, and apply corrections
krish-agent add-tests src/main.py --apply-corrections

# View task history
krish-agent history

# Show statistics
krish-agent stats

# Export memory
krish-agent export-memory runs.json
```

### Python API

```python
from krish_agent import WorkerAgent, ReviewerAgent, AgentOrchestrator

# Direct agent usage
worker = WorkerAgent()
result = worker.generate_tests("src/main.py", ".")

# Via orchestrator
orchestrator = AgentOrchestrator(repo_root=".")
result = orchestrator.add_tests("src/main.py", review=True)

# Import individual modules
from krish_agent.worker import WorkerAgent
from krish_agent.reviewer import ReviewerAgent
from krish_agent.memory import TaskMemory
from krish_agent.tools import read_file, write_file
```

## Dependencies

The package requires:
- `requests>=2.28.0` (for Ollama API calls)
- Python 3.8+

### Optional Development Dependencies

```bash
# Install dev dependencies
pip install -e ".[dev]"

# This includes:
# - pytest>=7.0
# - black>=22.0 (code formatter)
# - flake8>=4.0 (linter)
# - mypy>=0.950 (type checker)
```

## Verifying Installation

### Check Package is Installed

```bash
pip show krish-agent
```

You should see:
```
Name: krish-agent
Version: 0.1.0
Summary: Dual-agent AI coding system: Worker (llama3.1:8b) + Reviewer (devstral:latest)
```

### Check CLI is Available

```bash
which krish-agent
krish-agent --help
```

### Test with Python

```python
python -c "from krish_agent import WorkerAgent; print('✓ Import successful')"
```

## Troubleshooting

### "command not found: krish-agent"

Make sure the package installed correctly:

```bash
# Reinstall
pip install -e .

# Check installation path
pip show -f krish-agent | grep Location
```

### "ModuleNotFoundError: No module named 'krish_agent'"

The package may not be in your Python path. Try:

```bash
# Reinstall in editable mode
pip uninstall krish-agent
pip install -e .

# Or check Python path
python -c "import sys; print(sys.path)"
```

### "requests module not found"

Install dependencies:

```bash
pip install -e .
# or
pip install requests>=2.28.0
```

## Uninstalling

```bash
pip uninstall krish-agent
```

## Upgrading

```bash
# If using editable install, just update the files and reinstall
pip install --upgrade -e .

# If using PyPI
pip install --upgrade krish-agent
```

## Development Workflow

1. **Install in editable mode:**
   ```bash
   pip install -e .
   ```

2. **Make changes** to files in `krish_agent/`

3. **Test immediately:**
   ```bash
   krish-agent add-tests example_test_output.py
   ```

4. **Run linting (optional):**
   ```bash
   pip install -e ".[dev]"
   black krish_agent/
   flake8 krish_agent/
   mypy krish_agent/
   ```

5. **Run tests (optional):**
   ```bash
   pytest tests/
   ```

## Publishing to PyPI (Maintainers Only)

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI (requires credentials)
python -m twine upload dist/*
```

## Project Structure After Installation

```
krish_agent/
├── __init__.py          # Package entry point
├── cli.py               # CLI interface (installed as 'krish-agent' command)
├── worker.py            # Worker agent
├── reviewer.py          # Reviewer agent
├── tools.py             # Shared utilities
├── prompts.py           # System prompts
└── memory.py            # Task memory

setup.py                # Setup configuration
pyproject.toml          # Modern Python project config
README.md               # Documentation
QUICKSTART.md          # Quick setup guide
```

## Next Steps

After installation, see **QUICKSTART.md** to get started with Ollama and the models.

```bash
krish-agent add-tests example_test_output.py --review
```
