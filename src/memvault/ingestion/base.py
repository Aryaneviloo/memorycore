"""
Base interface for conversation ingestion
Any extractor takes a conversation and returns a list of
facts worth storing as memories.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ExtractedFact:
    """A single fact extracted from a conversation"""
    content: str
    memory_type: str = "semantic"
    importance: float = 0.6
    tags: list[str] | None = None


class BaseExtractor:
    """
    Abstract interface for fact extraction from conversation

    Implement this to add a new provider:
      - RuleBasedExtractor (no LLM, offline)
      - AnthropicExtractor (claude-haiku)
      - OpenAI (gpt-4o-mini)
      - Ollama (local LLM)
    """

    @abstractmethod
    def extract(self, 
                messages: list[dict]
                ) -> list[ExtractedFact]:
        """
        Extract memorable facts from a conversation
        Args: 
            messages: List of{"role": "user"/"assistant", 
                          "content": "..."}
        Returns:
            List of Extracted facts
        """
        raise NotImplementedError