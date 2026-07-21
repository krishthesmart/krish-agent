"""
Utility tools for file operations, command execution, and diff generation.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple


def read_file(path: str) -> str:
    """Read a file and return its contents as a string."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except Exception as e:
        raise Exception(f"Error reading file {path}: {e}")


def write_file(path: str, content: str) -> None:
    """Write content to a file, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise Exception(f"Error writing file {path}: {e}")


def append_file(path: str, content: str) -> None:
    """Append content to a file, creating if it doesn't exist."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise Exception(f"Error appending to file {path}: {e}")


def list_python_files(root_dir: str, exclude_dirs: Optional[List[str]] = None) -> List[str]:
    """
    Recursively list all Python files in a directory.

    Args:
        root_dir: Root directory to search.
        exclude_dirs: List of directory names to exclude (e.g., ['__pycache__', '.git']).

    Returns:
        List of relative paths to Python files.
    """
    if exclude_dirs is None:
        exclude_dirs = ['__pycache__', '.git', '.venv', 'venv', 'node_modules', '.pytest_cache']

    python_files = []
    for root, dirs, files in os.walk(root_dir):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                python_files.append(full_path)

    return sorted(python_files)


def run_command(cmd: str, cwd: Optional[str] = None, timeout: int = 30) -> Dict[str, any]:
    """
    Execute a shell command and return output and return code.

    Args:
        cmd: Command to execute.
        cwd: Working directory for the command.
        timeout: Timeout in seconds.

    Returns:
        Dict with keys: 'returncode', 'stdout', 'stderr', 'success'
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds',
            'success': False
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }


def get_git_diff(repo_path: str, staged_only: bool = False) -> str:
    """
    Get git diff of recent changes.

    Args:
        repo_path: Path to the git repository.
        staged_only: If True, only show staged changes.

    Returns:
        Diff output as a string.
    """
    cmd = 'git diff --staged' if staged_only else 'git diff'
    result = run_command(cmd, cwd=repo_path)
    return result['stdout'] if result['success'] else result['stderr']


def create_test_file_path(source_file: str) -> str:
    """
    Generate a test file path from a source file path.

    Examples:
        src/main.py -> tests/test_main.py
        lib/utils.py -> tests/test_utils.py
    """
    base_name = os.path.basename(source_file)
    test_name = f"test_{base_name}" if not base_name.startswith('test_') else base_name
    return os.path.join('tests', test_name)


def extract_code_block(text: str, language: str = 'python') -> Optional[str]:
    """
    Extract a code block from markdown text.

    Args:
        text: Text potentially containing markdown code blocks.
        language: Programming language marker (default 'python').

    Returns:
        Extracted code or None if no block found.
    """
    import re
    pattern = rf'```{language}\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1) if match else None


def parse_json_response(text: str) -> Dict:
    """
    Safely parse JSON from LLM response, handling potential markdown wrapping.

    Args:
        text: Response text from LLM.

    Returns:
        Parsed JSON dict or empty dict if parsing fails.
    """
    # Try direct parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    code_block = extract_code_block(text, 'json')
    if code_block:
        try:
            return json.loads(code_block)
        except json.JSONDecodeError:
            pass

    # Try to find JSON-like structure
    import re
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    return {}


def file_exists(path: str) -> bool:
    """Check if a file exists."""
    return os.path.isfile(path)


def dir_exists(path: str) -> bool:
    """Check if a directory exists."""
    return os.path.isdir(path)


def normalize_path(path: str) -> str:
    """Normalize a file path to absolute path."""
    return os.path.abspath(path)
