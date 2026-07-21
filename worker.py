"""
Worker agent: Fast coding assistant using a small local model (e.g., llama3.1:8b via Ollama).
Generates tests and makes minimal, focused code changes.
"""

import json
import time
from typing import Dict, List, Optional
from pathlib import Path

from tools import (
    read_file, write_file, list_python_files, run_command,
    parse_json_response, create_test_file_path, normalize_path
)
from prompts import WORKER_SYSTEM_PROMPT, WORKER_TASK_PROMPT_TEMPLATE


class WorkerAgent:
    """Fast coding agent using a small local LLM."""

    def __init__(self, model_endpoint: str = "http://localhost:11434", model_name: str = "llama3.1:8b"):
        """
        Initialize the worker agent.

        Args:
            model_endpoint: URL of the Ollama API endpoint (default: http://localhost:11434).
            model_name: Name of the model to use (default: llama3.1:8b).
        """
        self.model_endpoint = model_endpoint
        self.model_name = model_name
        self.start_time = None
        self.end_time = None

    def call_model(self, prompt: str) -> str:
        """
        Call the small local model via Ollama API.

        Args:
            prompt: The prompt to send to the model.

        Returns:
            The model's response as a string.
        """
        import requests

        print(f"[WORKER] Calling {self.model_name}...")

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
            print(f"[WORKER ERROR] Cannot connect to Ollama at {self.model_endpoint}")
            print("Make sure Ollama is running: ollama serve")
            raise
        except requests.exceptions.RequestException as e:
            print(f"[WORKER ERROR] API request failed: {e}")
            raise
        except Exception as e:
            print(f"[WORKER ERROR] Unexpected error: {e}")
            raise

    def analyze_target_files(self, target_path: str, repo_root: str) -> Dict:
        """
        Analyze target file(s) to understand what to test.

        Args:
            target_path: Path to file or directory to analyze.
            repo_root: Root of the repository.

        Returns:
            Dict with analysis: files found, code summary, etc.
        """
        target_path = normalize_path(target_path)
        repo_root = normalize_path(repo_root)

        if not Path(target_path).exists():
            return {'error': f"Target path not found: {target_path}"}

        files_to_test = []
        code_samples = {}

        if Path(target_path).is_file():
            files_to_test = [target_path]
        else:
            # Get all Python files in directory
            files_to_test = list_python_files(target_path)

        # Read code from each file
        for file_path in files_to_test[:5]:  # Limit to 5 files for performance
            try:
                content = read_file(file_path)
                # Truncate large files
                if len(content) > 2000:
                    content = content[:2000] + "\n... (truncated)"
                code_samples[file_path] = content
            except Exception as e:
                code_samples[file_path] = f"Error reading file: {e}"

        return {
            'files_found': len(files_to_test),
            'files_to_test': files_to_test[:5],
            'code_samples': code_samples
        }

    def generate_tests(self, target_path: str, repo_root: str) -> Dict:
        """
        Generate unit tests for target files using the worker model.

        Args:
            target_path: Path to file or directory to test.
            repo_root: Root of the repository.

        Returns:
            Dict with: plan, test_code, files_to_modify, test_results.
        """
        self.start_time = time.time()

        try:
            # Analyze target files
            analysis = self.analyze_target_files(target_path, repo_root)
            if 'error' in analysis:
                return {'success': False, 'error': analysis['error']}

            # Build the prompt
            files_summary = '\n'.join(
                f"- {f}: {analysis['code_samples'].get(f, 'N/A')[:300]}"
                for f in analysis['files_to_test']
            )

            task_prompt = WORKER_TASK_PROMPT_TEMPLATE.format(
                files=files_summary,
                repo_root=repo_root,
                test_output="No prior test results"
            )

            full_prompt = f"{WORKER_SYSTEM_PROMPT}\n\n{task_prompt}"

            # Call the model
            model_response = self.call_model(full_prompt)

            # Parse response
            parsed = parse_json_response(model_response)
            if not parsed:
                parsed = {
                    'plan': 'Test generation initiated',
                    'test_code': model_response,
                    'files_to_modify': [create_test_file_path(f) for f in analysis['files_to_test']],
                    'reasoning': 'Raw model output parsed'
                }

            # Try to run tests
            test_result = self._run_tests(repo_root)

            self.end_time = time.time()

            return {
                'success': True,
                'plan': parsed.get('plan', ''),
                'test_code': parsed.get('test_code', ''),
                'files_to_modify': parsed.get('files_to_modify', []),
                'reasoning': parsed.get('reasoning', ''),
                'test_result': test_result,
                'analysis': analysis,
                'execution_time': self.end_time - self.start_time
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - self.start_time if self.start_time else 0
            }

    def apply_changes(self, test_code: str, target_files: List[str], repo_root: str) -> Dict:
        """
        Apply generated test code to files.

        Args:
            test_code: The test code to write.
            target_files: List of files to modify.
            repo_root: Root of the repository.

        Returns:
            Dict with: success, files_modified, errors.
        """
        files_modified = []
        errors = []

        for target_file in target_files:
            try:
                # If no explicit path, use default test location
                if not target_file or target_file == 'tests/test_*.py':
                    target_file = create_test_file_path('unknown')

                full_path = Path(repo_root) / target_file

                # Write the test file
                write_file(str(full_path), test_code)
                files_modified.append(str(full_path))
                print(f"[WORKER] Wrote tests to {full_path}")

            except Exception as e:
                errors.append(f"Error writing {target_file}: {e}")

        return {
            'success': len(errors) == 0,
            'files_modified': files_modified,
            'errors': errors
        }

    def _run_tests(self, repo_root: str, test_cmd: str = "pytest tests/ -v") -> Dict:
        """
        Run tests and capture results.

        Args:
            repo_root: Root of the repository.
            test_cmd: Command to run tests.

        Returns:
            Dict with: success, stdout, stderr, returncode.
        """
        print(f"[WORKER] Running tests with: {test_cmd}")
        result = run_command(test_cmd, cwd=repo_root, timeout=60)

        return {
            'passed': result['success'],
            'returncode': result['returncode'],
            'stdout': result['stdout'][:1000],  # Truncate for brevity
            'stderr': result['stderr'][:500],
            'command': test_cmd
        }

    def summarize_run(self, generation_result: Dict) -> Dict:
        """
        Create a summary of the worker's run for the reviewer.

        Args:
            generation_result: Result from generate_tests().

        Returns:
            Structured summary for review.
        """
        return {
            'task': 'add_tests',
            'model': self.model_name,
            'success': generation_result.get('success', False),
            'plan': generation_result.get('plan', ''),
            'files_modified': generation_result.get('files_to_modify', []),
            'test_summary': generation_result.get('test_result', {}),
            'reasoning': generation_result.get('reasoning', ''),
            'execution_time': generation_result.get('execution_time', 0),
            'test_code': generation_result.get('test_code', '')[:500]  # Truncate for summary
        }
