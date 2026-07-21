"""
Reviewer agent: Senior code reviewer using Devstral.
Evaluates and improves changes made by the worker agent.
"""

import json
import time
from typing import Dict, List, Optional

from tools import read_file, write_file, run_command, parse_json_response
from prompts import REVIEWER_SYSTEM_PROMPT, REVIEWER_TASK_PROMPT_TEMPLATE


class ReviewerAgent:
    """Senior reviewer using Devstral model."""

    def __init__(self, model_endpoint: str = "http://localhost:11434", model_name: str = "devstral:latest"):
        """
        Initialize the reviewer agent.

        Args:
            model_endpoint: URL of the Ollama API endpoint (default: http://localhost:11434).
            model_name: Name of the Devstral model (default: devstral:latest).
        """
        self.model_endpoint = model_endpoint
        self.model_name = model_name
        self.start_time = None
        self.end_time = None

    def call_model(self, prompt: str) -> str:
        """
        Call the Devstral model via Ollama API for deep review.

        Args:
            prompt: The prompt to send to the model.

        Returns:
            The model's response as a string.
        """
        import requests

        print(f"[REVIEWER] Calling {self.model_name}...")

        try:
            response = requests.post(
                f"{self.model_endpoint}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=180
            )
            response.raise_for_status()
            return response.json()['response']
        except requests.exceptions.ConnectionError:
            print(f"[REVIEWER ERROR] Cannot connect to Ollama at {self.model_endpoint}")
            print("Make sure Ollama is running: ollama serve")
            raise
        except requests.exceptions.RequestException as e:
            print(f"[REVIEWER ERROR] API request failed: {e}")
            raise
        except Exception as e:
            print(f"[REVIEWER ERROR] Unexpected error: {e}")
            raise

    def review_worker_output(self, worker_summary: Dict, original_code: str = "") -> Dict:
        """
        Review the worker agent's output using Devstral.

        Args:
            worker_summary: Summary dict from WorkerAgent.summarize_run().
            original_code: The original code being tested (optional).

        Returns:
            Dict with: issues_found, corrections_applied, corrected_code, quality_score.
        """
        self.start_time = time.time()

        try:
            # Build the review prompt
            task_prompt = REVIEWER_TASK_PROMPT_TEMPLATE.format(
                worker_plan=worker_summary.get('plan', ''),
                test_code=worker_summary.get('test_code', ''),
                test_output=json.dumps(worker_summary.get('test_summary', {}), indent=2),
                original_code=original_code[:1000] if original_code else "Not provided"
            )

            full_prompt = f"{REVIEWER_SYSTEM_PROMPT}\n\n{task_prompt}"

            # Call Devstral model
            model_response = self.call_model(full_prompt)

            # Parse response
            parsed = parse_json_response(model_response)
            if not parsed:
                parsed = {
                    'issues_found': ['Could not parse model output'],
                    'corrections_applied': model_response[:500],
                    'corrected_code': '',
                    'test_quality_score': 0,
                    'reasoning': 'Raw model output'
                }

            self.end_time = time.time()

            return {
                'success': True,
                'issues_found': parsed.get('issues_found', []),
                'corrections_applied': parsed.get('corrections_applied', ''),
                'corrected_code': parsed.get('corrected_code', ''),
                'test_quality_score': parsed.get('test_quality_score', 0),
                'reasoning': parsed.get('reasoning', ''),
                'execution_time': self.end_time - self.start_time
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': time.time() - self.start_time if self.start_time else 0
            }

    def apply_corrections(self, corrected_code: str, target_files: List[str], repo_root: str) -> Dict:
        """
        Apply corrections suggested by the reviewer.

        Args:
            corrected_code: The corrected test code.
            target_files: List of files to update.
            repo_root: Root of the repository.

        Returns:
            Dict with: success, files_updated, errors.
        """
        files_updated = []
        errors = []

        for target_file in target_files:
            try:
                full_path = f"{repo_root}/{target_file}"
                write_file(full_path, corrected_code)
                files_updated.append(full_path)
                print(f"[REVIEWER] Updated {full_path}")
            except Exception as e:
                errors.append(f"Error updating {target_file}: {e}")

        return {
            'success': len(errors) == 0,
            'files_updated': files_updated,
            'errors': errors
        }

    def run_tests_after_review(self, repo_root: str, test_cmd: str = "pytest tests/ -v") -> Dict:
        """
        Run tests after applying corrections.

        Args:
            repo_root: Root of the repository.
            test_cmd: Command to run tests.

        Returns:
            Dict with: passed, returncode, stdout, stderr.
        """
        print(f"[REVIEWER] Running tests to verify corrections: {test_cmd}")
        result = run_command(test_cmd, cwd=repo_root, timeout=60)

        return {
            'passed': result['success'],
            'returncode': result['returncode'],
            'stdout': result['stdout'][:1000],
            'stderr': result['stderr'][:500],
            'command': test_cmd
        }

    def summarize_review(self, review_result: Dict, test_result: Dict) -> Dict:
        """
        Create a summary of the reviewer's work.

        Args:
            review_result: Result from review_worker_output().
            test_result: Result from run_tests_after_review().

        Returns:
            Structured summary of the review.
        """
        return {
            'model': self.model_name,
            'review_success': review_result.get('success', False),
            'issues_found': review_result.get('issues_found', []),
            'corrections_applied': review_result.get('corrections_applied', ''),
            'quality_score': review_result.get('test_quality_score', 0),
            'tests_passed': test_result.get('passed', False),
            'test_returncode': test_result.get('returncode', -1),
            'execution_time': review_result.get('execution_time', 0)
        }
