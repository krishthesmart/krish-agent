# Dual-Agent Coding System: Worker + Reviewer

A lightweight, extensible Python system for automated code testing and review using two specialized agents:

1. **Worker Agent**: Fast, small local model (**llama3.1:8b** via Ollama) for quick test generation and minimal code changes.
2. **Reviewer Agent**: Slower, powerful model (**devstral:latest** via Ollama) for deep code quality review and corrections.

## Architecture

```
krish-agent/
├── cli.py              # Command-line interface and orchestrator
├── worker.py           # Fast worker agent (test generation, minimal fixes)
├── reviewer.py         # Deep reviewer agent (code quality, corrections)
├── tools.py            # Shared utilities (file I/O, git, run commands)
├── prompts.py          # System prompts for both agents
├── memory.py           # Task logging and history
└── README.md           # This file
```

## Features

- **Fast Worker Agent**: Uses small local LLM to quickly generate unit tests and make focused changes
- **Deep Review with Devstral**: Optional powerful reviewer for code quality and comprehensive feedback
- **Test Execution**: Built-in pytest integration with automatic test running and reporting
- **Memory & History**: Persistent task logging with statistics tracking
- **Clean Separation**: No heavy frameworks—explicit orchestration with clear responsibilities
- **Extensible Prompts**: Easy to customize system prompts in `prompts.py`

## Installation

### Requirements
- Python 3.8+
- Ollama (https://ollama.ai)
- llama3.1:8b model (~4GB)
- devstral:latest model (~30GB+)

### Quick Setup (5 minutes)

See **QUICKSTART.md** for step-by-step instructions. Short version:

```bash
# 1. Install Ollama from https://ollama.ai

# 2. Pull models
ollama pull llama3.1:8b
ollama pull devstral:latest

# 3. Start Ollama server (keep running)
ollama serve

# 4. In another terminal, run the agent
python cli.py add-tests example_test_output.py --review
```

## Usage

### Basic Test Generation

```bash
# Generate tests for a single file
python cli.py add-tests src/main.py

# Generate tests for a directory
python cli.py add-tests src/

# Generate and request review
python cli.py add-tests src/main.py --review

# Generate, review, and apply corrections automatically
python cli.py add-tests src/main.py --apply-corrections
```

### View Task History

```bash
# Show recent tasks
python cli.py history

# Show statistics
python cli.py stats

# Export task memory to file
python cli.py export-memory tasks.json
```

## Configuration

### Worker Agent (llama3.1:8b)

The worker is configured to use **llama3.1:8b** on Ollama:

```python
worker = WorkerAgent(
    model_endpoint="http://localhost:11434",  # Ollama default
    model_name="llama3.1:8b"                   # Fast 8B model
)
```

To use a different model, edit `cli.py`:
```python
self.worker = WorkerAgent(model_name="llama2:13b")  # or any available model
```

### Reviewer Agent (devstral:latest)

The reviewer is configured to use **devstral:latest** on Ollama:

```python
reviewer = ReviewerAgent(
    model_endpoint="http://localhost:11434",  # Ollama default
    model_name="devstral:latest"               # Powerful reviewer model
)
```

To use a different model, edit `cli.py`:
```python
self.reviewer = ReviewerAgent(model_name="neural-chat:latest")  # or any available model
```

## How It Works

### Worker Agent (llama3.1:8b)

Calls Ollama's `/api/generate` endpoint:

```python
# Real implementation in worker.py
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False
    },
    timeout=120
)
return response.json()['response']
```

**Typical flow:**
1. Reads target file(s)
2. Generates pytest tests (~2-5 seconds)
3. Writes to `tests/` directory
4. Runs `pytest` and returns results

### Reviewer Agent (devstral:latest)

Calls the same Ollama endpoint with Devstral:

```python
# Real implementation in reviewer.py
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "devstral:latest",
        "prompt": prompt,
        "stream": False
    },
    timeout=180
)
return response.json()['response']
```

**Typical flow:**
1. Reads worker's test code and results
2. Evaluates quality and coverage (~10-30 seconds)
3. Proposes improvements or corrections
4. Optionally applies and re-runs tests

## System Prompts

Both agents use specialized prompts defined in `prompts.py`:

- **WORKER_SYSTEM_PROMPT**: Fast, focused test generation
- **REVIEWER_SYSTEM_PROMPT**: Deep quality review

Customize these to match your coding standards, test frameworks, or specific requirements.

## Typical Workflow

1. **Worker Phase** (seconds)
   - Reads target file(s)
   - Generates unit tests using small local model
   - Writes tests to `tests/` directory
   - Runs `pytest` and captures results
   - Returns structured JSON summary

2. **Review Phase** (optional, slower)
   - Reviewer reads worker's plan and generated tests
   - Uses Devstral to evaluate quality and coverage
   - Identifies gaps and issues
   - Proposes improvements or corrections

3. **Correction Phase** (optional)
   - Apply reviewer's corrections
   - Re-run tests to verify improvements
   - Log final results to memory

## Memory & Logging

All tasks are logged to `.agent_memory.json`:

```json
{
  "timestamp": "2025-01-15T10:30:45.123456",
  "task_id": "task_main_1736936445",
  "success": true,
  "worker": {
    "model": "llama3.1:8b",
    "plan": "Add comprehensive unit tests...",
    "files_modified": ["tests/test_main.py"],
    "execution_time": 2.45
  },
  "reviewer": {
    "model": "devstral",
    "quality_score": 8,
    "issues_found": ["Limited edge case coverage"],
    "execution_time": 5.12
  }
}
```

## Extending the System

### Add a New Command

Edit `cli.py` in the `main()` function:

```python
# Add a new subcommand
fix_bugs = subparsers.add_parser("fix-bugs", help="Fix identified bugs")
fix_bugs.add_argument("target", help="File or directory to fix")

# Handle in the command dispatcher
elif args.command == "fix-bugs":
    result = orchestrator.fix_bugs(args.target)
```

### Create a New Agent Type

1. Create a new file: `agent_type.py`
2. Follow the pattern of `worker.py` or `reviewer.py`
3. Import and use in `cli.py`

### Customize Prompts

Edit `prompts.py` to define new roles or adjust existing behavior:

```python
CUSTOM_AGENT_PROMPT = """Your specialized role and instructions here..."""
```

## Performance

### Speed

- **Worker (llama3.1:8b)**: 2-5 seconds per task on GPU
- **Reviewer (devstral:latest)**: 10-30 seconds per review on GPU

### Hardware Requirements

- **Minimum**: 8GB GPU VRAM (llama3.1:8b only)
- **Recommended**: 16GB+ GPU VRAM for both models
- **CPU-only**: 10-50x slower, not recommended

### Optimization Tips

- Load models sequentially (not simultaneously) to save VRAM
- Use `--review` only when needed (slower)
- Use `--apply-corrections` for automatic improvements
- Run on GPU for best performance

## Example Scenario

```bash
# Generate tests for a new utility module
python cli.py add-tests src/utils.py

# Output:
# [STEP 1] Worker agent: Generating tests...
# [✓] Worker completed in 2.34s
#     - Plan: Add comprehensive unit tests for utility functions
#     - Files to modify: ['tests/test_utils.py']
#     - Test result: PASS

# Now review and improve
python cli.py add-tests src/utils.py --apply-corrections

# Output:
# [STEP 1] Worker agent: Generating tests...
# [✓] Worker completed in 2.34s
# [STEP 2] Reviewer agent: Reviewing generated tests...
# [✓] Reviewer completed in 5.67s
#     - Issues found: 2
#     - Quality score: 8/10
#     - Corrections: Added edge case tests for empty inputs
# [STEP 3] Applying reviewer's corrections...
# [✓] Tests after corrections: PASS
```

## Troubleshooting

### "Cannot connect to Ollama at http://localhost:11434"
```bash
# Make sure Ollama is running
ollama serve

# Verify connectivity
curl http://localhost:11434/api/tags
```

### "Model not found: llama3.1:8b"
```bash
ollama pull llama3.1:8b
```

### "Model not found: devstral:latest"
```bash
ollama pull devstral:latest
```

### Tests failed after generation
This is normal! Review feedback improves tests:
```bash
python cli.py add-tests src/main.py --review
```

### Slow performance
Check GPU memory:
```bash
# CUDA (Linux)
nvidia-smi

# Metal (macOS)
ollama list  # Shows memory per model
```

If only 8GB VRAM: don't use `--review`, just generate tests.

## License

MIT (or your preferred license)

## Contributing

Pull requests welcome! Areas for improvement:
- [ ] Real LLM API integrations
- [ ] Parallel test execution
- [ ] Enhanced diff generation
- [ ] Web UI for memory browsing
- [ ] Integration with GitHub/GitLab
- [ ] Support for other test frameworks (unittest, pytest plugins)
