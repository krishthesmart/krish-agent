"""
Code generation agent - Generate new code files, refactor, add features.
Like Aider's code generation capabilities.
"""

import json
import time
from typing import Dict, List
from pathlib import Path

from krish_agent.tools import (
    read_file, write_file, run_command,
    parse_json_response, normalize_path
)
from krish_agent.prompts import WORKER_SYSTEM_PROMPT


class CodeGenerator:
    """Generate and modify code using LLM."""

    def __init__(self, model_endpoint: str = "http://localhost:11434", model_name: str = "llama3.1:8b"):
        """Initialize code generator."""
        self.model_endpoint = model_endpoint
        self.model_name = model_name
        self.start_time = None
        self.end_time = None

    def call_model(self, prompt: str) -> str:
        """Call the LLM for code generation."""
        import requests

        print(f"[GENERATOR] Calling {self.model_name}...")

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
        except requests.exceptions.ConnectionError:
            print(f"[GENERATOR ERROR] Cannot connect to Ollama at {self.model_endpoint}")
            print("Make sure Ollama is running: ollama serve")
            raise
        except Exception as e:
            print(f"[GENERATOR ERROR] API request failed: {e}")
            raise

    def generate_code(self, description: str, repo_root: str) -> Dict:
        """
        Generate new code based on description.

        Args:
            description: What the user wants to create
            repo_root: Repository root

        Returns:
            Dict with generated code and file info
        """
        self.start_time = time.time()

        try:
            prompt = f"""You are a code generation expert. Generate Python code based on this request:

{description}

Generate complete, working code. Include:
- Proper imports
- Error handling
- Comments
- Type hints if possible

Return ONLY the code, no explanations.
"""

            response = self.call_model(prompt)

            # Determine filename from description
            filename = self._determine_filename(description)

            self.end_time = time.time()

            return {
                'success': True,
                'code': response,
                'filename': filename,
                'description': description,
                'execution_time': self.end_time - self.start_time
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - self.start_time if self.start_time else 0
            }

    def refactor_code(self, file_path: str, instructions: str, repo_root: str) -> Dict:
        """
        Refactor existing code.

        Args:
            file_path: Path to file to refactor
            instructions: Refactoring instructions
            repo_root: Repository root

        Returns:
            Dict with refactored code
        """
        self.start_time = time.time()

        try:
            # Read original code
            original_code = read_file(file_path)

            prompt = f"""You are a code refactoring expert. Refactor this code:

Original code:
```python
{original_code}
```

Instructions: {instructions}

Return ONLY the refactored code, no explanations. Keep the same functionality but improve it according to the instructions.
"""

            response = self.call_model(prompt)

            self.end_time = time.time()

            return {
                'success': True,
                'original_code': original_code,
                'refactored_code': response,
                'file_path': file_path,
                'instructions': instructions,
                'execution_time': self.end_time - self.start_time
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - self.start_time if self.start_time else 0
            }

    def add_feature(self, file_path: str, feature_description: str, repo_root: str) -> Dict:
        """
        Add a feature to existing code.

        Args:
            file_path: Path to file to modify
            feature_description: What feature to add
            repo_root: Repository root

        Returns:
            Dict with modified code
        """
        self.start_time = time.time()

        try:
            # Read original code
            original_code = read_file(file_path)

            prompt = f"""You are a code enhancement expert. Add this feature to the code:

Original code:
```python
{original_code}
```

Feature to add: {feature_description}

Return ONLY the complete modified code with the new feature integrated, no explanations.
"""

            response = self.call_model(prompt)

            self.end_time = time.time()

            return {
                'success': True,
                'original_code': original_code,
                'modified_code': response,
                'file_path': file_path,
                'feature': feature_description,
                'execution_time': self.end_time - self.start_time
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - self.start_time if self.start_time else 0
            }

    def fix_bug(self, file_path: str, bug_description: str, repo_root: str) -> Dict:
        """
        Fix a bug in existing code.

        Args:
            file_path: Path to file with bug
            bug_description: Description of the bug
            repo_root: Repository root

        Returns:
            Dict with fixed code
        """
        self.start_time = time.time()

        try:
            # Read original code
            original_code = read_file(file_path)

            prompt = f"""You are a debugging expert. Fix this bug:

Original code:
```python
{original_code}
```

Bug description: {bug_description}

Return ONLY the corrected code with the bug fixed, no explanations.
"""

            response = self.call_model(prompt)

            self.end_time = time.time()

            return {
                'success': True,
                'original_code': original_code,
                'fixed_code': response,
                'file_path': file_path,
                'bug': bug_description,
                'execution_time': self.end_time - self.start_time
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - self.start_time if self.start_time else 0
            }

    def write_code_to_file(self, code: str, filename: str, repo_root: str) -> Dict:
        """Write generated code to a file."""
        try:
            # Normalize repo root
            repo_root = normalize_path(repo_root)

            # If filename is empty or None, use default
            if not filename or filename == '':
                filename = 'generated.py'

            # Strip markdown code fences if present
            code = self._clean_code(code)

            filepath = Path(repo_root) / filename

            # Create directories if needed
            filepath.parent.mkdir(parents=True, exist_ok=True)

            write_file(str(filepath), code)

            return {
                'success': True,
                'filepath': str(filepath),
                'message': f'Code written to {filepath}'
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _determine_filename(self, description: str) -> str:
        """Determine a good filename from description."""
        import re

        # Extract key words
        words = re.findall(r'\b\w+\b', description.lower())

        # Filter out common words
        stop_words = {'a', 'an', 'the', 'for', 'with', 'from', 'to', 'and', 'or', 'create', 'make', 'generate', 'write', 'build', 'new', 'file'}
        meaningful_words = [w for w in words if w not in stop_words][:2]

        if meaningful_words:
            filename = '_'.join(meaningful_words) + '.py'
        else:
            filename = 'generated.py'

        return filename

    def _clean_code(self, code: str) -> str:
        """Remove markdown code fences from code."""
        import re

        # Remove markdown code fences
        code = re.sub(r'^```python\n', '', code)
        code = re.sub(r'^```\n', '', code)
        code = re.sub(r'\n```$', '', code)
        code = re.sub(r'\n```python$', '', code)

        return code.strip()
