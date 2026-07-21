"""
Simple in-memory and persistent task logging using JSON.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class TaskMemory:
    """Manage task logs and history."""

    def __init__(self, log_file: str = '.agent_memory.json'):
        """
        Initialize memory with optional persistent JSON log file.

        Args:
            log_file: Path to JSON file for persistent storage.
        """
        self.log_file = log_file
        self.runs: List[Dict] = []
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Load existing runs from JSON file if it exists."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.runs = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load memory from {self.log_file}: {e}")
                self.runs = []

    def _save_to_disk(self) -> None:
        """Persist runs to JSON file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.runs, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save memory to {self.log_file}: {e}")

    def save_run(self, run_summary: Dict) -> None:
        """
        Record a run with timestamp and metadata.

        Args:
            run_summary: Dict with task info, files touched, results, etc.
        """
        run_record = {
            'timestamp': datetime.now().isoformat(),
            **run_summary
        }
        self.runs.append(run_record)
        self._save_to_disk()

    def list_recent_runs(self, limit: int = 10) -> List[Dict]:
        """
        Get the most recent runs.

        Args:
            limit: Max number of runs to return.

        Returns:
            List of run records, most recent first.
        """
        return sorted(self.runs, key=lambda r: r.get('timestamp', ''), reverse=True)[:limit]

    def get_run_by_id(self, task_id: str) -> Optional[Dict]:
        """Get a specific run by ID or task ID."""
        for run in self.runs:
            if run.get('task_id') == task_id or run.get('id') == task_id:
                return run
        return None

    def summary_stats(self) -> Dict:
        """Get summary statistics about all runs."""
        if not self.runs:
            return {
                'total_runs': 0,
                'passed': 0,
                'failed': 0,
                'reviewed': 0
            }

        total = len(self.runs)
        passed = sum(1 for r in self.runs if r.get('test_result') == 'pass')
        failed = sum(1 for r in self.runs if r.get('test_result') == 'fail')
        reviewed = sum(1 for r in self.runs if r.get('reviewed', False))

        return {
            'total_runs': total,
            'passed': passed,
            'failed': failed,
            'reviewed': reviewed,
            'pass_rate': f"{100 * passed / total:.1f}%" if total > 0 else "N/A"
        }

    def clear_history(self) -> None:
        """Clear all recorded runs."""
        self.runs = []
        self._save_to_disk()

    def export_runs(self, output_file: str) -> None:
        """Export all runs to a JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.runs, f, indent=2, default=str)
            print(f"Exported {len(self.runs)} runs to {output_file}")
        except Exception as e:
            print(f"Error exporting runs: {e}")
