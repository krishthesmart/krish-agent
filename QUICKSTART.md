# Quick Start Guide: llama3.1:8b + devstral:latest

This guide gets you running in 5 minutes with the two-agent system.

## Setup

### 1. Install Ollama

Download from https://ollama.ai and install.

### 2. Pull the Models

Open a terminal and run:

```bash
# Pull worker model (fast, ~4GB)
ollama pull llama3.1:8b

# Pull reviewer model (slower, more powerful, ~30GB+)
ollama pull devstral:latest
```

This may take a few minutes depending on your internet speed.

### 3. Start Ollama Server

Keep this running in a terminal:

```bash
ollama serve
```

You should see:
```
Listening on 127.0.0.1:11434
```

### 4. Verify Models Are Available

In another terminal, check they're loaded:

```bash
curl http://localhost:11434/api/tags
```

You should see both `llama3.1:8b` and `devstral:latest` in the output.

### 5. Run the Agent System

In the project directory, run:

```bash
python cli.py add-tests example_test_output.py
```

You'll see:

```
============================================================
AGENT ORCHESTRATOR: add-tests task
============================================================

[STEP 1] Worker agent: Generating tests...
[WORKER] Calling llama3.1:8b...
[✓] Worker completed in 3.45s
    - Plan: Add comprehensive unit tests...
    - Files to modify: ['tests/test_example_test_output.py']
    - Test result: PASS
```

### 6. Add Review Step (Devstral)

To invoke the reviewer:

```bash
python cli.py add-tests example_test_output.py --review
```

This runs both agents:
- **Worker** (llama3.1:8b) generates tests quickly
- **Reviewer** (devstral:latest) evaluates and suggests improvements

### 7. Auto-Apply Corrections

Have the reviewer fix issues automatically:

```bash
python cli.py add-tests example_test_output.py --apply-corrections
```

This will:
1. Generate tests with worker
2. Review with devstral
3. Apply devstral's corrections
4. Re-run tests to verify

## Check Results

View task history:

```bash
python cli.py history
```

View stats:

```bash
python cli.py stats
```

## Troubleshooting

### "Connection refused"

Make sure Ollama is running:
```bash
ollama serve
```

### "Model not found: llama3.1:8b"

Pull the model:
```bash
ollama pull llama3.1:8b
```

### "Model not found: devstral:latest"

Pull the model:
```bash
ollama pull devstral:latest
```

### Slow performance

- **llama3.1:8b** should complete in 2-5 seconds on a modern GPU
- **devstral:latest** may take 10-30 seconds depending on your hardware
- If running on CPU only, expect 5x-10x slower

Check GPU availability:
```bash
# macOS (Metal)
ollama list
# Shows model memory requirements

# Linux (CUDA)
nvidia-smi  # Check GPU memory usage
```

### Tests not passing

This is expected! The worker generates tests, but they might not all pass initially. That's why the reviewer exists—to improve them.

```bash
# Get devstral's feedback
python cli.py add-tests example_test_output.py --review

# See what needs fixing
python cli.py history
```

## Model Comparison

| Agent | Model | Speed | Quality | Use Case |
|-------|-------|-------|---------|----------|
| Worker | llama3.1:8b | ⚡ Fast (2-5s) | Good | Quick test generation |
| Reviewer | devstral:latest | 🐢 Slow (10-30s) | Excellent | Deep code review |

## Common Commands

```bash
# Generate tests only (no review)
python cli.py add-tests src/main.py

# Generate and review
python cli.py add-tests src/main.py --review

# Generate, review, apply fixes
python cli.py add-tests src/main.py --apply-corrections

# View all runs
python cli.py history

# Show summary stats
python cli.py stats

# Export runs to file
python cli.py export-memory runs.json
```

## Next Steps

1. Try the system on your own code:
   ```bash
   python cli.py add-tests path/to/your/code.py --review
   ```

2. Customize the prompts in `prompts.py` for your coding style

3. Check the generated tests in the `tests/` directory

4. Use `--apply-corrections` to automatically improve test quality

Happy testing! 🚀
