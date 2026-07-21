"""
Command-line interface for the dual-agent coding system.
Orchestrates the worker and reviewer agents.
NOW WITH 1,000,000,000% GODMODE CAPABILITIES!
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional

from krish_agent.worker import WorkerAgent
from krish_agent.reviewer import ReviewerAgent
from krish_agent.memory import TaskMemory
from krish_agent.tools import read_file, normalize_path
from krish_agent.godmode_integration import (
    activate_all_godmode_features,
    GodmodeIntegration,
    GodmodeWorker,
    GodmodeReviewer,
    GodmodeArchitect
)


class AgentOrchestrator:
    """Orchestrates worker and reviewer agents."""

    def __init__(self, repo_root: str = "."):
        """
        Initialize the orchestrator.

        Args:
            repo_root: Root directory of the repository to work in.
        """
        self.repo_root = normalize_path(repo_root)
        self.memory = TaskMemory('.agent_memory.json')
        self.worker = WorkerAgent()
        self.reviewer = ReviewerAgent()

    def add_tests(self, target_path: str, review: bool = False, apply_corrections: bool = False, write_tests: bool = False) -> Dict:
        """
        Add tests to the target file(s).

        Args:
            target_path: Path to file or directory to test.
            review: If True, use reviewer agent to review generated tests.
            apply_corrections: If True, apply reviewer's corrections.
            write_tests: If True, write tests to a new file in tests/ directory.

        Returns:
            Dict with full execution summary.
        """
        print(f"\n{'=' * 60}")
        print("AGENT ORCHESTRATOR: add-tests task")
        print(f"{'=' * 60}")

        # Step 1: Worker generates tests
        print("\n[STEP 1] Worker agent: Generating tests...")
        worker_result = self.worker.generate_tests(target_path, self.repo_root)

        if not worker_result.get('success'):
            print(f"[ERROR] Worker failed: {worker_result.get('error', 'Unknown error')}")
            return {'success': False, 'error': worker_result.get('error')}

        worker_summary = self.worker.summarize_run(worker_result)
        print(f"[✓] Worker completed in {worker_summary.get('execution_time', 0):.2f}s")
        print(f"    - Plan: {worker_summary.get('plan', '')[:80]}")
        print(f"    - Files to modify: {worker_summary.get('files_modified', [])}")
        print(f"    - Test result: {'PASS' if worker_summary.get('test_summary', {}).get('passed') else 'FAIL'}")

        result = {
            'success': True,
            'worker': worker_summary,
            'reviewer': None,
            'task_id': f"task_{Path(target_path).stem}_{int(__import__('time').time())}"
        }

        # Step 2: Optional review
        if review or not worker_summary.get('test_summary', {}).get('passed'):
            print("\n[STEP 2] Reviewer agent: Reviewing generated tests...")

            # Get original code for context
            original_code = ""
            if Path(target_path).is_file():
                try:
                    original_code = read_file(target_path)
                except:
                    pass

            review_result = self.reviewer.review_worker_output(worker_summary, original_code)

            if not review_result.get('success'):
                print(f"[ERROR] Reviewer failed: {review_result.get('error', 'Unknown error')}")
            else:
                reviewer_summary = self.reviewer.summarize_review(review_result, {'passed': False})
                print(f"[✓] Reviewer completed in {reviewer_summary.get('execution_time', 0):.2f}s")
                print(f"    - Issues found: {len(reviewer_summary.get('issues_found', []))}")
                print(f"    - Quality score: {reviewer_summary.get('quality_score', 0)}/10")
                print(f"    - Corrections: {reviewer_summary.get('corrections_applied', '')[:80]}")

                result['reviewer'] = reviewer_summary

                # Step 3: Apply corrections if requested
                if apply_corrections and review_result.get('corrected_code'):
                    print("\n[STEP 3] Applying reviewer's corrections...")
                    corrections = self.reviewer.apply_corrections(
                        review_result.get('corrected_code', ''),
                        worker_summary.get('files_modified', []),
                        self.repo_root
                    )

                    if corrections['success']:
                        # Re-run tests after corrections
                        test_result = self.reviewer.run_tests_after_review(self.repo_root)
                        print(f"[✓] Tests after corrections: {'PASS' if test_result['passed'] else 'FAIL'}")
                        result['corrections_applied'] = corrections
                        result['final_test_result'] = test_result
                    else:
                        print(f"[ERROR] Could not apply corrections: {corrections['errors']}")

        # Step 4: Write tests to file if requested
        if write_tests and worker_summary.get('test_code'):
            print("\n[STEP 4] Writing tests to file...")

            # Determine test file path
            if Path(target_path).is_file():
                test_file = Path(self.repo_root) / f"tests/test_{Path(target_path).stem}.py"
            else:
                test_file = Path(self.repo_root) / "tests/test_generated.py"

            try:
                test_file.parent.mkdir(parents=True, exist_ok=True)
                write_file(str(test_file), worker_summary.get('test_code', ''))
                print(f"[✓] Tests written to: {test_file}")
                result['test_file_written'] = str(test_file)
            except Exception as e:
                print(f"[ERROR] Could not write test file: {e}")
                result['test_file_error'] = str(e)

        # Save to memory
        self.memory.save_run(result)
        print(f"\n[✓] Task saved with ID: {result['task_id']}")

        return result

    def show_history(self, limit: int = 5) -> None:
        """Show recent task history."""
        runs = self.memory.list_recent_runs(limit=limit)

        if not runs:
            print("No task history found.")
            return

        print(f"\n{'=' * 60}")
        print(f"Recent Tasks (last {limit})")
        print(f"{'=' * 60}")

        for i, run in enumerate(runs, 1):
            timestamp = run.get('timestamp', 'Unknown')
            task_id = run.get('task_id', 'Unknown')
            success = run.get('success', False)
            worker_model = run.get('worker', {}).get('model', 'Unknown')

            status = "✓" if success else "✗"
            print(f"\n{i}. [{status}] {task_id}")
            print(f"   Time: {timestamp}")
            print(f"   Worker: {worker_model}")

            if run.get('reviewer'):
                reviewer_model = run.get('reviewer', {}).get('model', 'Unknown')
                quality = run.get('reviewer', {}).get('quality_score', 'N/A')
                print(f"   Reviewer: {reviewer_model} (quality: {quality}/10)")

    def show_stats(self) -> None:
        """Show memory statistics."""
        stats = self.memory.summary_stats()

        print(f"\n{'=' * 60}")
        print("Task Statistics")
        print(f"{'=' * 60}")
        print(f"Total runs: {stats['total_runs']}")
        print(f"Passed: {stats['passed']}")
        print(f"Failed: {stats['failed']}")
        print(f"Reviewed: {stats['reviewed']}")
        print(f"Pass rate: {stats['pass_rate']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Dual-agent coding system: Worker + Reviewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate tests for a file
  krish-agent add-tests src/main.py

  # Generate tests and get review
  krish-agent add-tests src/main.py --review

  # Generate tests, review, and apply corrections
  krish-agent add-tests src/main.py --review --apply-corrections

  # Generate tests and write to file
  krish-agent add-tests src/main.py --write-tests

  # Add all files from directory
  krish-agent add-tests /path/to/directory

  # Show task history
  krish-agent history

  # Show statistics
  krish-agent stats
        """
    )

    parser.add_argument("--repo", default=".", help="Repository root directory (default: current dir)")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # add-tests command
    add_tests_parser = subparsers.add_parser("add-tests", help="Generate and optionally review tests")
    add_tests_parser.add_argument("target", help="File or directory to generate tests for")
    add_tests_parser.add_argument(
        "--review",
        action="store_true",
        help="Request reviewer agent to review generated tests"
    )
    add_tests_parser.add_argument(
        "--apply-corrections",
        action="store_true",
        help="Apply reviewer's corrections (implies --review)"
    )
    add_tests_parser.add_argument(
        "--write-tests",
        action="store_true",
        help="Write generated tests to a new file in tests/ directory"
    )

    # history command
    subparsers.add_parser("history", help="Show recent task history")

    # stats command
    subparsers.add_parser("stats", help="Show task statistics")

    # memory export command
    memory_export = subparsers.add_parser("export-memory", help="Export task memory to file")
    memory_export.add_argument("output", help="Output file path")

    # launch/chat command
    subparsers.add_parser("launch", help="Launch interactive chat mode")
    subparsers.add_parser("chat", help="Launch interactive chat mode")

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = AgentOrchestrator(repo_root=args.repo)

    # Handle commands
    if args.command == "add-tests":
        # Imply --review if --apply-corrections is set
        review = args.review or args.apply_corrections
        result = orchestrator.add_tests(
            args.target,
            review=review,
            apply_corrections=args.apply_corrections,
            write_tests=args.write_tests
        )

        # Print final summary
        print(f"\n{'=' * 60}")
        print("FINAL SUMMARY")
        print(f"{'=' * 60}")
        print(json.dumps(result, indent=2, default=str))

        sys.exit(0 if result.get('success') else 1)

    elif args.command == "history":
        orchestrator.show_history(limit=10)
        sys.exit(0)

    elif args.command == "stats":
        orchestrator.show_stats()
        sys.exit(0)

    elif args.command == "export-memory":
        orchestrator.memory.export_runs(args.output)
        sys.exit(0)

    elif args.command in ["launch", "chat"]:
        from krish_agent.chat import launch_chat
        launch_chat(repo_root=args.repo)
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
