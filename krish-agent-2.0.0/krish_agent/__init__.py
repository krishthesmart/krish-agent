"""
Krish Agent: Dual-agent AI coding system for automated testing and code review.

Components:
- Worker Agent: Fast test generation using llama3.1:8b
- Reviewer Agent: Deep code review using devstral:latest
"""

__version__ = "0.1.0"
__author__ = "Arul Meiyappan Kannappan"

from krish_agent.worker import WorkerAgent
from krish_agent.reviewer import ReviewerAgent
from krish_agent.cli import AgentOrchestrator

__all__ = [
    "WorkerAgent",
    "ReviewerAgent",
    "AgentOrchestrator",
]
