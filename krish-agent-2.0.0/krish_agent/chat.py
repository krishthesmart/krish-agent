"""
Aider-like interactive chat mode for krish-agent with model selection.
Continuous conversation interface for code testing and review.
No commands - just natural language!
"""

import sys
import requests
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from krish_agent.cli import AgentOrchestrator
from krish_agent.tools import list_python_files, write_file, normalize_path
from krish_agent.code_generator import CodeGenerator


class AiderLikeChat:
    """Aider-style interactive chat interface for krish-agent."""

    def __init__(self, repo_root: str = ".", ollama_endpoint: str = "http://localhost:11434"):
        """Initialize chat mode."""
        self.console = Console()
        self.orchestrator = AgentOrchestrator(repo_root=repo_root)
        self.repo_root = repo_root
        self.ollama_endpoint = ollama_endpoint
        self.review_mode = False
        self.write_mode = False
        self.files = []
        self.models = []
        self.worker_model = "llama3.1:8b"
        self.reviewer_model = None
        self.code_generator = CodeGenerator(ollama_endpoint, self.worker_model)

        self.load_files()
        self.load_models()

    def load_files(self):
        """Load Python files from repo."""
        try:
            self.files = list_python_files(self.repo_root)
        except:
            self.files = []

    def load_models(self):
        """Load available models from Ollama."""
        try:
            response = requests.get(f"{self.ollama_endpoint}/api/tags", timeout=5)
            models_data = response.json().get("models", [])
            self.models = [m["name"] for m in models_data]

            # Auto-select worker and reviewer if available
            if "llama3.1:8b" in self.models:
                self.worker_model = "llama3.1:8b"
            elif self.models:
                self.worker_model = self.models[0]

            # Set reviewer to second model or different from worker
            if len(self.models) > 1:
                self.reviewer_model = self.models[1] if self.models[1] != self.worker_model else self.models[0]
            elif self.models:
                self.reviewer_model = self.models[0]

        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load models from Ollama: {e}[/yellow]")
            self.models = ["llama3.1:8b"]  # Fallback

    def show_banner(self):
        """Show welcome banner like Aider."""
        banner = """
[bold cyan]╔════════════════════════════════════════════════════════════╗
║         krish-agent - AI-Powered Test Generation               ║
║                                                                ║
║  Just chat naturally! Type what you want to do.               ║
║  Examples: "add tests for main.py", "review code"            ║
╚════════════════════════════════════════════════════════════════╝[/bold cyan]
        """
        self.console.print(banner)

    def show_files(self):
        """Show currently tracked files."""
        if not self.files:
            self.console.print("[yellow]No Python files found in this directory[/yellow]")
            return

        self.console.print("\n[bold cyan]📁 Tracked Files (All files in repo):[/bold cyan]")
        for i, file in enumerate(self.files[:15], 1):
            self.console.print(f"  {i}. {file}")
        if len(self.files) > 15:
            self.console.print(f"  ... and {len(self.files) - 15} more")

    def show_status(self):
        """Show current status bar with model info."""
        status = f"[cyan]Files: {len(self.files)}[/cyan]"

        # Add model info
        status += f" | [green]Worker: {self.worker_model}[/green]"
        if self.reviewer_model:
            status += f" | [magenta]Reviewer: {self.reviewer_model}[/magenta]"

        if self.review_mode:
            status += " | [yellow]✓ Review[/yellow]"
        if self.write_mode:
            status += " | [yellow]✓ Write[/yellow]"

        self.console.print(f"\n{status}")

    def show_model_selection_menu(self):
        """Show model selection menu."""
        if not self.models:
            self.console.print("[red]No models available in Ollama[/red]")
            return

        while True:
            self.console.print("\n[bold cyan]📊 Model Configuration:[/bold cyan]")
            self.console.print(f"  [green]1.[/green] Change Worker Model (current: {self.worker_model})")
            self.console.print(f"  [magenta]2.[/magenta] Change Reviewer Model (current: {self.reviewer_model or 'Disabled'})")
            self.console.print(f"  [cyan]3.[/cyan] View all models")
            self.console.print(f"  [yellow]0.[/yellow] Done")

            choice = Prompt.ask("Select", default="0")

            if choice == "0":
                break
            elif choice == "1":
                self.select_worker_model()
            elif choice == "2":
                self.select_reviewer_model()
            elif choice == "3":
                self.show_models_table()
            else:
                self.console.print("[red]Invalid selection[/red]")

    def select_worker_model(self):
        """Interactive worker model selection."""
        if not self.models:
            return

        self.console.print("\n[bold cyan]Select Worker Model:[/bold cyan]")
        for i, model in enumerate(self.models, 1):
            marker = "[green]→[/green]" if model == self.worker_model else " "
            self.console.print(f"  {marker} {i}. {model}")

        try:
            choice = Prompt.ask("Select", default=str(self.models.index(self.worker_model) + 1))
            idx = int(choice) - 1
            if 0 <= idx < len(self.models):
                self.worker_model = self.models[idx]
                self.console.print(f"[green]✓ Worker: {self.worker_model}[/green]")
        except ValueError:
            self.console.print("[red]Invalid input[/red]")

    def select_reviewer_model(self):
        """Interactive reviewer model selection."""
        if not self.models:
            return

        self.console.print("\n[bold cyan]Select Reviewer Model:[/bold cyan]")
        for i, model in enumerate(self.models, 1):
            marker = "[magenta]→[/magenta]" if model == self.reviewer_model else " "
            self.console.print(f"  {marker} {i}. {model}")
        self.console.print("   0. None (disable reviewer)")

        try:
            choice = Prompt.ask("Select", default=str(self.models.index(self.reviewer_model) + 1) if self.reviewer_model else "0")
            idx = int(choice)
            if idx == 0:
                self.reviewer_model = None
                self.console.print("[yellow]Reviewer disabled[/yellow]")
            elif 0 < idx <= len(self.models):
                self.reviewer_model = self.models[idx - 1]
                self.console.print(f"[green]✓ Reviewer: {self.reviewer_model}[/green]")
        except ValueError:
            self.console.print("[red]Invalid input[/red]")

    def show_models_table(self):
        """Show all available models."""
        if not self.models:
            self.console.print("[red]No models available[/red]")
            return

        table = Table(title="Available Models", show_header=True, header_style="bold magenta")
        table.add_column("Model", style="green")
        table.add_column("Role", style="yellow")

        for model in self.models:
            role = ""
            if model == self.worker_model:
                role = "🏃 Worker"
            elif model == self.reviewer_model:
                role = "🔍 Reviewer"
            table.add_row(model, role)

        self.console.print(table)

    def process_user_request(self, request: str):
        """Process natural language request."""
        import re

        # Check for model selection keyword
        if any(word in request.lower() for word in ["model", "worker", "reviewer", "change model", "select model"]):
            self.show_model_selection_menu()
            return

        # Check for review toggle
        if "review" in request.lower() and "off" in request.lower():
            self.review_mode = False
            self.console.print("[red]Review disabled[/red]")
            return
        elif "review" in request.lower() and "on" in request.lower():
            self.review_mode = True
            self.console.print("[green]Review enabled[/green]")
            return

        # Check for write toggle
        if "write" in request.lower() and "off" in request.lower():
            self.write_mode = False
            self.console.print("[red]Write disabled[/red]")
            return
        elif "write" in request.lower() and "on" in request.lower():
            self.write_mode = True
            self.console.print("[green]Write enabled[/green]")
            return

        # Check for help
        if "help" in request.lower() or request.lower() == "?":
            self.show_help()
            return

        # Detect task type
        request_lower = request.lower()

        # Code generation: "create", "make", "generate", "write" + program/function/file
        if any(word in request_lower for word in ["create", "make", "generate", "write"]) and \
           any(word in request_lower for word in ["program", "function", "file", "code", "class", "api", "app", "server"]):
            self.handle_code_generation(request)
            return

        # Bug fixing: "fix", "bug", "error", "issue"
        if any(word in request_lower for word in ["fix", "bug", "error", "issue", "wrong"]):
            self.handle_bug_fix(request)
            return

        # Refactoring: "refactor", "improve", "clean", "optimize", "simplify"
        if any(word in request_lower for word in ["refactor", "improve", "clean", "optimize", "simplify"]):
            self.handle_refactoring(request)
            return

        # Adding feature: "add", "feature", "enhance", "extend"
        if any(word in request_lower for word in ["add", "feature", "enhance", "extend"]) and \
           any(word in request_lower for word in ["to", "function", "file", "class"]):
            self.handle_feature_addition(request)
            return

        # Default: treat as test generation
        self.handle_test_generation(request)

    def handle_code_generation(self, request: str):
        """Generate new code file."""
        self.console.print(f"\n[cyan]Generating code: {request}[/cyan]")
        self.console.print(f"[cyan]Model: {self.worker_model}[/cyan]")

        result = self.code_generator.generate_code(request, self.repo_root)

        if result.get('success'):
            code = result.get('code', '')
            filename = result.get('filename', 'generated.py')

            self.console.print(Panel(
                f"[green]✓ Code generated in {result.get('execution_time', 0):.2f}s[/green]",
                border_style="green"
            ))

            # Show preview
            lines = code.split('\n')[:10]
            self.console.print("\n[cyan]Preview:[/cyan]")
            for line in lines:
                self.console.print(f"  {line}")
            if len(code.split('\n')) > 10:
                self.console.print("  ...")

            # Ask to save
            save = Prompt.ask("\nSave to file?", choices=["y", "n"], default="y")
            if save.lower() == "y":
                # Ensure repo_root is set correctly
                repo_root = normalize_path(self.repo_root) if self.repo_root else normalize_path(".")
                write_result = self.code_generator.write_code_to_file(code, filename, repo_root)
                if write_result['success']:
                    self.console.print(f"[green]✓ Saved to: {write_result['filepath']}[/green]")
                    self.load_files()  # Refresh file list
                else:
                    self.console.print(f"[red]✗ Error: {write_result['error']}[/red]")
        else:
            self.console.print(f"[red]✗ Error: {result.get('error')}[/red]")

    def handle_test_generation(self, request: str):
        """Generate tests."""
        # Extract file paths from request
        import re
        paths = re.findall(r"(?:src/[\w/\.]+|[\w/\.]+\.py)", request)

        if not paths:
            # If no paths specified, use all tracked files or first one
            if not self.files:
                self.console.print("[yellow]No files to test[/yellow]")
                return
            paths = self.files  # Use all files by default

        # Check for flags in the request
        review = self.review_mode or any(word in request.lower() for word in ["review", "check", "improve", "deep"])
        write = self.write_mode or any(word in request.lower() for word in ["write", "create", "save", "file"])

        # Process each file
        for target_path in paths[:3]:  # Limit to first 3 files per request
            self.console.print(f"\n[cyan]Processing: {target_path}[/cyan]")
            self.console.print(f"[cyan]Worker: {self.worker_model}[/cyan]")
            if self.reviewer_model and review:
                self.console.print(f"[cyan]Reviewer: {self.reviewer_model}[/cyan]")

            try:
                # Update orchestrator with selected models
                self.orchestrator.worker.model_name = self.worker_model
                if self.reviewer_model:
                    self.orchestrator.reviewer.model_name = self.reviewer_model

                result = self.orchestrator.add_tests(
                    target_path,
                    review=review and self.reviewer_model is not None,
                    apply_corrections=False,
                    write_tests=write
                )

                if result.get("success"):
                    worker_summary = result.get("worker", {})
                    self.console.print(Panel(
                        f"[green]✓ Tests generated in {worker_summary.get('execution_time', 0):.2f}s[/green]",
                        border_style="green"
                    ))

                    if result.get("reviewer"):
                        reviewer_summary = result.get("reviewer", {})
                        self.console.print(Panel(
                            f"[green]✓ Reviewed with score: {reviewer_summary.get('quality_score', 0)}/10[/green]",
                            border_style="green"
                        ))

                    if result.get("test_file_written"):
                        self.console.print(f"[green]✓ Tests written to: {result.get('test_file_written')}[/green]")

                else:
                    self.console.print(f"[red]✗ Error: {result.get('error')}[/red]")

            except Exception as e:
                self.console.print(f"[red]✗ Error: {e}[/red]")

    def handle_bug_fix(self, request: str):
        """Fix a bug in code."""
        import re
        paths = re.findall(r"[\w/\.]+\.py", request)

        if not paths:
            self.console.print("[yellow]Please specify a file to fix[/yellow]")
            return

        target_file = paths[0]
        self.console.print(f"\n[cyan]Fixing bug in: {target_file}[/cyan]")
        self.console.print(f"[cyan]Model: {self.worker_model}[/cyan]")

        result = self.code_generator.fix_bug(target_file, request, self.repo_root)

        if result.get('success'):
            self.console.print(Panel(
                f"[green]✓ Bug fix generated in {result.get('execution_time', 0):.2f}s[/green]",
                border_style="green"
            ))

            save = Prompt.ask("\nApply fix?", choices=["y", "n"], default="y")
            if save.lower() == "y":
                write_file(target_file, result.get('fixed_code', ''))
                self.console.print(f"[green]✓ Fixed: {target_file}[/green]")
        else:
            self.console.print(f"[red]✗ Error: {result.get('error')}[/red]")

    def handle_refactoring(self, request: str):
        """Refactor code."""
        import re
        paths = re.findall(r"[\w/\.]+\.py", request)

        if not paths:
            self.console.print("[yellow]Please specify a file to refactor[/yellow]")
            return

        target_file = paths[0]
        self.console.print(f"\n[cyan]Refactoring: {target_file}[/cyan]")
        self.console.print(f"[cyan]Model: {self.worker_model}[/cyan]")

        result = self.code_generator.refactor_code(target_file, request, self.repo_root)

        if result.get('success'):
            self.console.print(Panel(
                f"[green]✓ Refactored in {result.get('execution_time', 0):.2f}s[/green]",
                border_style="green"
            ))

            save = Prompt.ask("\nApply refactoring?", choices=["y", "n"], default="y")
            if save.lower() == "y":
                write_file(target_file, result.get('refactored_code', ''))
                self.console.print(f"[green]✓ Refactored: {target_file}[/green]")
        else:
            self.console.print(f"[red]✗ Error: {result.get('error')}[/red]")

    def handle_feature_addition(self, request: str):
        """Add a feature to code."""
        import re
        paths = re.findall(r"[\w/\.]+\.py", request)

        if not paths:
            self.console.print("[yellow]Please specify a file to modify[/yellow]")
            return

        target_file = paths[0]
        self.console.print(f"\n[cyan]Adding feature to: {target_file}[/cyan]")
        self.console.print(f"[cyan]Model: {self.worker_model}[/cyan]")

        result = self.code_generator.add_feature(target_file, request, self.repo_root)

        if result.get('success'):
            self.console.print(Panel(
                f"[green]✓ Feature added in {result.get('execution_time', 0):.2f}s[/green]",
                border_style="green"
            ))

            save = Prompt.ask("\nApply changes?", choices=["y", "n"], default="y")
            if save.lower() == "y":
                write_file(target_file, result.get('modified_code', ''))
                self.console.print(f"[green]✓ Updated: {target_file}[/green]")
        else:
            self.console.print(f"[red]✗ Error: {result.get('error')}[/red]")

    def show_help(self):
        """Show help message."""
        help_text = """
[bold cyan]Just chat naturally![/bold cyan]

Examples:
  "add tests for src/main.py"
  "generate tests with review"
  "create tests and write to file"
  "test all files"
  "enable review"
  "change worker model"
  "change reviewer model"
  "help"
  "exit"

All Python files in this directory are automatically tracked! 📁
        """
        self.console.print(help_text)

    def run(self):
        """Start the interactive chat loop."""
        self.show_banner()
        self.show_files()

        while True:
            try:
                self.show_status()
                user_input = Prompt.ask("[bold green]You[/bold green]", console=self.console).strip()

                if not user_input:
                    continue

                # Check for exit
                if user_input.lower() in ["exit", "quit", "bye", "q"]:
                    self.console.print("[yellow]Goodbye! 👋[/yellow]")
                    sys.exit(0)

                # Process as natural language request
                self.process_user_request(user_input)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Type 'exit' to quit[/yellow]")
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")


def launch_chat(repo_root: str = "."):
    """Launch the Aider-like chat interface."""
    chat = AiderLikeChat(repo_root=repo_root)
    chat.run()
