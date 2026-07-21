"""
Advanced features: Memory, context awareness, conversation history, smart suggestions.
Makes krish-agent better than Aider.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console


class ConversationMemory:
    """
    Persistent conversation memory - remembers context across sessions.
    Learns from past interactions and provides smart suggestions.
    """

    def __init__(self, memory_file: str = ".krish_memory.json"):
        """Initialize conversation memory."""
        self.memory_file = memory_file
        self.console = Console()
        self.conversations = []
        self.context_stack = []
        self.learned_patterns = {}
        self.load_memory()

    def load_memory(self):
        """Load memory from disk."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.conversations = data.get('conversations', [])
                    self.learned_patterns = data.get('patterns', {})
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load memory: {e}[/yellow]")

    def save_memory(self):
        """Save memory to disk."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump({
                    'conversations': self.conversations,
                    'patterns': self.learned_patterns,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2, default=str)
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not save memory: {e}[/yellow]")

    def add_interaction(self, user_request: str, action: str, result: Dict, files_affected: List[str]):
        """Record a user interaction."""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_request': user_request,
            'action': action,
            'result': result,
            'files_affected': files_affected,
            'success': result.get('success', False)
        }
        self.conversations.append(interaction)

        # Learn patterns
        self._learn_pattern(user_request, action)
        self.save_memory()

    def _learn_pattern(self, request: str, action: str):
        """Learn patterns from user requests."""
        # Extract keywords
        keywords = tuple(sorted(set(request.lower().split())))
        if keywords not in self.learned_patterns:
            self.learned_patterns[keywords] = {
                'action': action,
                'count': 0,
                'last_used': datetime.now().isoformat()
            }
        self.learned_patterns[keywords]['count'] += 1

    def get_context(self, max_interactions: int = 5) -> str:
        """Get recent context for LLM."""
        if not self.conversations:
            return ""

        recent = self.conversations[-max_interactions:]
        context = "Previous interactions:\n"
        for interaction in recent:
            context += f"- {interaction['user_request']}: {interaction['action']}\n"
        return context

    def suggest_next_action(self, user_request: str) -> Optional[str]:
        """Suggest the next action based on conversation history."""
        request_words = set(user_request.lower().split())

        best_match = None
        best_score = 0

        for keywords, pattern in self.learned_patterns.items():
            # Calculate similarity
            overlap = len(request_words & set(keywords))
            if overlap > best_score:
                best_score = overlap
                best_match = pattern

        if best_match and best_score > 0:
            return best_match['action']
        return None

    def get_related_files(self, keyword: str) -> List[str]:
        """Get files related to a keyword from memory."""
        related = []
        for interaction in self.conversations:
            if keyword.lower() in interaction['user_request'].lower():
                related.extend(interaction['files_affected'])
        return list(set(related))

    def show_context(self):
        """Show current context."""
        if not self.conversations:
            self.console.print("[yellow]No memory yet[/yellow]")
            return

        self.console.print("\n[bold cyan]📚 Conversation Memory:[/bold cyan]")
        recent = self.conversations[-5:]
        for i, interaction in enumerate(recent, 1):
            timestamp = interaction['timestamp'].split('T')[1][:5]
            status = "[green]✓[/green]" if interaction['success'] else "[red]✗[/red]"
            self.console.print(f"  {status} {timestamp} - {interaction['action']}: {interaction['user_request'][:50]}")


class CodeAnalyzer:
    """
    Analyze code quality, complexity, and issues.
    Provides smart feedback and suggestions.
    """

    def __init__(self):
        """Initialize code analyzer."""
        self.console = Console()

    def analyze(self, code: str, filename: str = "") -> Dict:
        """Analyze code and return issues/suggestions."""
        issues = []
        suggestions = []
        score = 100

        lines = code.split('\n')

        # Check for docstrings
        if not ('"""' in code or "'''" in code):
            issues.append("Missing module/function docstrings")
            score -= 10

        # Check for type hints
        if 'def ' in code and '->' not in code:
            issues.append("Missing type hints")
            score -= 5

        # Check line length
        long_lines = [i for i, line in enumerate(lines) if len(line) > 100]
        if long_lines:
            suggestions.append(f"Lines {long_lines} exceed 100 characters")

        # Check for error handling
        if 'raise' not in code and 'try' not in code and 'except' not in code:
            suggestions.append("Consider adding error handling")

        # Check for imports
        if 'import' not in lines[0:5]:
            suggestions.append("Imports should be at the top")

        # Check complexity (rough estimate)
        complexity = code.count('if ') + code.count('for ') + code.count('while ')
        if complexity > 10:
            suggestions.append("Code complexity is high - consider refactoring")

        return {
            'quality_score': max(0, score),
            'issues': issues,
            'suggestions': suggestions,
            'complexity': complexity,
            'lines_of_code': len(lines)
        }


class SmartSuggestions:
    """
    Provide intelligent suggestions based on context.
    Anticipate user needs.
    """

    def __init__(self, memory: ConversationMemory):
        """Initialize smart suggestions."""
        self.memory = memory
        self.console = Console()

    def get_suggestions(self, user_request: str, files: List[str]) -> List[str]:
        """Get intelligent suggestions based on context."""
        suggestions = []

        request_lower = user_request.lower()

        # If user generated code, suggest testing
        if any(word in request_lower for word in ["create", "generate", "make", "write"]):
            if not any("test" in f.lower() for f in files):
                suggestions.append("💡 Would you like to add unit tests?")

        # If user is testing, suggest review
        if "test" in request_lower:
            suggestions.append("💡 Run code review to ensure quality?")

        # If user is refactoring, suggest optimization
        if "refactor" in request_lower:
            suggestions.append("💡 Would you like to optimize performance?")

        # If user is fixing bugs, suggest adding tests
        if "fix" in request_lower or "bug" in request_lower:
            suggestions.append("💡 Add a test case to prevent regression?")

        # Based on memory
        next_action = self.memory.suggest_next_action(user_request)
        if next_action:
            suggestions.append(f"💡 Based on your history, next: {next_action}?")

        return suggestions

    def show_suggestions(self, suggestions: List[str]):
        """Display suggestions to user."""
        if suggestions:
            self.console.print("\n[bold cyan]Smart Suggestions:[/bold cyan]")
            for suggestion in suggestions[:3]:  # Show top 3
                self.console.print(f"  {suggestion}")


class FileTracker:
    """
    Track all files in the project with detailed metadata.
    Better than Aider's file tracking.
    """

    def __init__(self, repo_root: str = "."):
        """Initialize file tracker."""
        self.repo_root = repo_root
        self.files = {}
        self.file_history = {}
        self.scan_files()

    def scan_files(self):
        """Scan and catalog all files."""
        from krish_agent.tools import list_python_files

        try:
            py_files = list_python_files(self.repo_root)
            for filepath in py_files:
                self.files[filepath] = {
                    'path': filepath,
                    'created_at': datetime.now().isoformat(),
                    'last_modified': datetime.now().isoformat(),
                    'size_bytes': os.path.getsize(filepath) if os.path.exists(filepath) else 0,
                    'lines_of_code': self._count_lines(filepath)
                }
        except Exception as e:
            pass

    def _count_lines(self, filepath: str) -> int:
        """Count lines in a file."""
        try:
            with open(filepath, 'r') as f:
                return len(f.readlines())
        except:
            return 0

    def add_file(self, filepath: str, source: str = "generated"):
        """Track a new file."""
        self.files[filepath] = {
            'path': filepath,
            'source': source,
            'created_at': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'size_bytes': os.path.getsize(filepath) if os.path.exists(filepath) else 0,
            'lines_of_code': self._count_lines(filepath)
        }

        if filepath not in self.file_history:
            self.file_history[filepath] = []
        self.file_history[filepath].append({
            'action': 'created',
            'timestamp': datetime.now().isoformat(),
            'source': source
        })

    def update_file(self, filepath: str, action: str = "modified"):
        """Update file metadata."""
        if filepath in self.files:
            self.files[filepath]['last_modified'] = datetime.now().isoformat()
            self.files[filepath]['lines_of_code'] = self._count_lines(filepath)
            self.files[filepath]['size_bytes'] = os.path.getsize(filepath) if os.path.exists(filepath) else 0

            if filepath not in self.file_history:
                self.file_history[filepath] = []
            self.file_history[filepath].append({
                'action': action,
                'timestamp': datetime.now().isoformat()
            })

    def get_stats(self) -> Dict:
        """Get project statistics."""
        total_lines = sum(f['lines_of_code'] for f in self.files.values())
        total_size = sum(f['size_bytes'] for f in self.files.values())

        return {
            'total_files': len(self.files),
            'total_lines': total_lines,
            'total_size_kb': total_size / 1024,
            'avg_file_size': total_size / len(self.files) if self.files else 0,
            'generated_files': len([f for f in self.files.values() if f.get('source') == 'generated'])
        }

    def show_stats(self):
        """Display file statistics."""
        stats = self.get_stats()
        from rich.table import Table

        console = Console()
        console.print("\n[bold cyan]📊 Project Statistics:[/bold cyan]")
        console.print(f"  Files: {stats['total_files']}")
        console.print(f"  Lines of code: {stats['total_lines']}")
        console.print(f"  Total size: {stats['total_size_kb']:.1f} KB")
        console.print(f"  Generated files: {stats['generated_files']}")
