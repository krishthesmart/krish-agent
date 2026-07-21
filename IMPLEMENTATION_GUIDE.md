# Implementation Guide: Connecting Real LLMs

This guide shows how to integrate real LLM endpoints with the worker and reviewer agents.

## Quick Start Options

### Option 1: Ollama (Recommended for Local Testing)

Best for: Local development, no API costs, fast iteration.

**Setup:**
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.1:8b
ollama serve
```

**Implementation in `worker.py`:**
```python
import requests
import json

def call_model(self, prompt: str) -> str:
    """Call Ollama endpoint."""
    try:
        response = requests.post(
            f"{self.model_endpoint}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()['response']
    except requests.RequestException as e:
        print(f"Error calling Ollama: {e}")
        return ""
```

**Test it:**
```bash
python -c "
from worker import WorkerAgent
agent = WorkerAgent()
response = agent.call_model('Write a hello world function.')
print(response[:200])
"
```

---

### Option 2: Anthropic Claude API

Best for: High-quality, robust models. Claude 3 series recommended.

**Setup:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
pip install anthropic
```

**Implementation in `reviewer.py`:**
```python
import anthropic
import os

def call_model(self, prompt: str) -> str:
    """Call Anthropic Claude API."""
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-3-opus-20240229",  # Most capable
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return message.content[0].text
    except anthropic.APIError as e:
        print(f"Error calling Anthropic API: {e}")
        return ""
```

**Test it:**
```bash
python -c "
import os
os.environ['ANTHROPIC_API_KEY'] = 'your-key-here'
from reviewer import ReviewerAgent
agent = ReviewerAgent()
response = agent.call_model('Write a hello world function.')
print(response[:200])
"
```

---

### Option 3: OpenAI API (GPT-4, GPT-3.5)

Best for: High-quality general models, well-tested.

**Setup:**
```bash
export OPENAI_API_KEY="sk-..."
pip install openai
```

**Implementation in both agents:**
```python
from openai import OpenAI

def call_model(self, prompt: str) -> str:
    """Call OpenAI API."""
    try:
        client = OpenAI()  # Uses OPENAI_API_KEY env var
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return ""
```

---

### Option 4: vLLM Local Server (Advanced)

Best for: Running large models locally with efficient inference.

**Setup:**
```bash
pip install vllm

# Start vLLM server with a model
python -m vllm.entrypoints.openai.api_server \
    --model mistralai/Mistral-7B-Instruct-v0.1
# Runs at http://localhost:8000
```

**Implementation in `worker.py`:**
```python
import requests

def call_model(self, prompt: str) -> str:
    """Call vLLM OpenAI-compatible endpoint."""
    try:
        response = requests.post(
            f"{self.model_endpoint}/v1/chat/completions",
            json={
                "model": self.model_name,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.RequestException as e:
        print(f"Error calling vLLM: {e}")
        return ""
```

---

### Option 5: Together.ai (Cloud-Hosted Models)

Best for: Easy cloud deployment without managing infrastructure.

**Setup:**
```bash
export TOGETHER_API_KEY="..."
pip install together
```

**Implementation:**
```python
import together

def call_model(self, prompt: str) -> str:
    """Call Together.ai API."""
    try:
        response = together.Complete.create(
            model=self.model_name,  # e.g., "mistralai/Mistral-7B-Instruct-v0.1"
            prompt=prompt,
            max_tokens=2000,
            temperature=0.7
        )
        return response['output']['choices'][0]['text']
    except Exception as e:
        print(f"Error calling Together.ai: {e}")
        return ""
```

---

## Comparison Table

| Option | Speed | Cost | Quality | Setup | Best For |
|--------|-------|------|---------|-------|----------|
| Ollama (llama3.1:8b) | Fast | Free | Medium | Easy | Local dev, fast iteration |
| Ollama (larger) | Slow | Free | Good | Medium | Production-like testing |
| Claude 3 Opus | Slow | $$$ | Excellent | Easy | Best quality, research |
| GPT-4 | Medium | $$$ | Excellent | Easy | General purpose |
| GPT-3.5 | Fast | $ | Good | Easy | Budget-conscious |
| vLLM Local | Fast | Free | Good | Hard | Local prod, performance tuning |
| Together.ai | Medium | $$ | Good-Excellent | Easy | Cloud without ops burden |

---

## Recommended Setup: Hybrid Approach

**Worker Agent**: Use fast local model
```python
# worker.py
worker = WorkerAgent(
    model_endpoint="http://localhost:11434",
    model_name="llama3.1:8b"
)
```

**Reviewer Agent**: Use high-quality cloud model
```python
# reviewer.py
reviewer = ReviewerAgent(
    model_endpoint="https://api.anthropic.com",
    model_name="claude-3-opus-20240229"
)
```

This gives you:
- ✓ Fast worker (seconds)
- ✓ High-quality review (comprehensive feedback)
- ✓ Reasonable cost (only reviewer uses paid API)
- ✓ Independent failure modes (worker fails → review compensates)

---

## Configuration Management

Create a `config.py` for easier management:

```python
# config.py
import os
from enum import Enum

class ModelProvider(Enum):
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    VLLM = "vllm"

# Worker configuration
WORKER_CONFIG = {
    'provider': ModelProvider.OLLAMA,
    'endpoint': os.getenv('WORKER_ENDPOINT', 'http://localhost:11434'),
    'model': os.getenv('WORKER_MODEL', 'llama3.1:8b'),
    'timeout': 120
}

# Reviewer configuration
REVIEWER_CONFIG = {
    'provider': ModelProvider.ANTHROPIC,
    'endpoint': os.getenv('REVIEWER_ENDPOINT', 'https://api.anthropic.com'),
    'model': os.getenv('REVIEWER_MODEL', 'claude-3-opus-20240229'),
    'timeout': 180,
    'api_key': os.getenv('ANTHROPIC_API_KEY')
}
```

Then import in agents:
```python
from config import WORKER_CONFIG, ModelProvider

class WorkerAgent:
    def __init__(self, config=None):
        self.config = config or WORKER_CONFIG
        if self.config['provider'] == ModelProvider.OLLAMA:
            self.endpoint = self.config['endpoint']
            self.model = self.config['model']
        elif self.config['provider'] == ModelProvider.OPENAI:
            # Different setup
            pass
```

---

## Error Handling & Fallbacks

Add graceful degradation:

```python
def call_model_with_fallback(self, prompt: str) -> str:
    """Try primary model, fall back to alternative."""
    try:
        return self.call_primary_model(prompt)
    except Exception as e:
        print(f"Primary model failed: {e}")
        print("Attempting fallback...")
        try:
            return self.call_fallback_model(prompt)
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            return ""

def call_primary_model(self, prompt: str) -> str:
    # Try Claude first
    return self.call_anthropic(prompt)

def call_fallback_model(self, prompt: str) -> str:
    # Fall back to Ollama
    return self.call_ollama(prompt)
```

---

## Testing Your Integration

Create `test_integration.py`:

```python
import json
from worker import WorkerAgent
from reviewer import ReviewerAgent

def test_worker():
    """Test worker model connectivity."""
    worker = WorkerAgent()
    prompt = "Return valid JSON: {\"test\": \"hello\"}"
    response = worker.call_model(prompt)
    print(f"Worker response: {response[:100]}")
    assert response, "Worker should return non-empty response"

def test_reviewer():
    """Test reviewer model connectivity."""
    reviewer = ReviewerAgent()
    prompt = "Return valid JSON: {\"test\": \"hello\"}"
    response = reviewer.call_model(prompt)
    print(f"Reviewer response: {response[:100]}")
    assert response, "Reviewer should return non-empty response"

def test_full_pipeline():
    """Test end-to-end with actual models."""
    from cli import AgentOrchestrator
    
    # Create test file
    test_code = '''
def greet(name):
    return f"Hello {name}"
    '''
    with open('test_sample.py', 'w') as f:
        f.write(test_code)
    
    # Run orchestrator
    orchestrator = AgentOrchestrator()
    result = orchestrator.add_tests('test_sample.py', review=True)
    
    print(json.dumps(result, indent=2, default=str))
    assert result['success'], "Pipeline should succeed"

if __name__ == '__main__':
    test_worker()
    print("✓ Worker integration OK\n")
    
    test_reviewer()
    print("✓ Reviewer integration OK\n")
    
    test_full_pipeline()
    print("✓ Full pipeline OK\n")
```

Run it:
```bash
python test_integration.py
```

---

## Production Deployment

For production use:

1. **Use a load balancer** if running multiple agent instances
2. **Add retry logic** for transient failures
3. **Implement rate limiting** to avoid API quota issues
4. **Log all API calls** for debugging and cost tracking
5. **Monitor response times** and quality metrics
6. **Use circuit breaker pattern** to handle cascading failures
7. **Cache model responses** when appropriate

Example with retries:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class RobustWorkerAgent(WorkerAgent):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def call_model(self, prompt: str) -> str:
        # Automatic retry on failure with exponential backoff
        return super().call_model(prompt)
```

---

## Next Steps

1. Pick your preferred setup from the options above
2. Implement the `call_model()` method in `worker.py` and `reviewer.py`
3. Test with `test_integration.py`
4. Run: `python cli.py add-tests example_test_output.py --review`
5. Check `.agent_memory.json` for results

Happy coding! 🚀
