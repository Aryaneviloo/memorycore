"""
Rule-based fact extractor.

Uses pattern matching and heuristics to extract memorable facts
from conversations.
"""

from __future__ import annotations

import re

from memvault.ingestion.base import BaseExtractor, ExtractedFact

# Format: (regex pattern, memory_type, importance)
FACT_PATTERNS: list[tuple[str, str, float]] = [
    # --- Identity ---
    (r"\bmy name is\b", "semantic", 0.9),
    (r"\bpeople call me\b", "semantic", 0.9),
    (r"\bi go by\b", "semantic", 0.85),
    (r"\bi('m| am) (a|an) \w+\b", "semantic", 0.8),
    (
    r"\bi('m| am)\b.{0,40}\b"
    r"(developer|engineer|student|designer|researcher|"
    r"founder|architect|lead|manager|scientist|analyst)\b",
    "semantic",
    0.85,
    ),
    (r"\bi work (at|for|with)\b", "semantic", 0.8),
    (r"\bi('m| am) (from|based in|living in|located in)\b", "semantic", 0.75),
    (r"\bi('m| am) \d+ years old\b", "semantic", 0.75),
    (r"\bi study (at|in)\b", "semantic", 0.8),
    (r"\bmy (job|role|position|title) is\b", "semantic", 0.85),
    (r"\bi run (a|an|my)\b", "semantic", 0.75),

    # --- Preferences ---
    (r"\bi prefer\b", "semantic", 0.8),
    (r"\bi love\b", "semantic", 0.7),
    (r"\bi hate\b", "semantic", 0.75),
    (r"\bi dislike\b", "semantic", 0.75),
    (r"\bi enjoy\b", "semantic", 0.7),
    (r"\bi like\b", "semantic", 0.65),
    (r"\bi can't stand\b", "semantic", 0.75),
    (r"\bi('m| am) (a big fan|not a fan)\b", "semantic", 0.75),
    (r"\bmy (favorite|favourite|preferred|go-to)\b", "semantic", 0.8),
    (r"\bi('d| would) (rather|prefer)\b", "semantic", 0.75),
    (r"\bgives me (the creeps|anxiety|joy|energy)\b", "semantic", 0.65),
    (r"\bi (swear by|rely on|depend on|count on)\b", "semantic", 0.75),

    # --- Habits / Behavior ---
    (r"\bi always\b", "procedural", 0.75),
    (r"\bi never\b", "semantic", 0.75),
    (r"\bi usually\b", "procedural", 0.65),
    (r"\bi tend to\b", "procedural", 0.65),
    (r"\bi (make it a point|make sure) to\b", "procedural", 0.7),
    (r"\bmy (routine|habit|workflow|process) is\b", "procedural", 0.75),
    (r"\bevery (day|morning|night|week|month)\b", "procedural", 0.6),
    (r"\bi (start|end|begin) (my day|each day|every day)\b", "procedural", 0.7),

    # --- Technical ---
    (
    r"\bmy (main|primary|go-to|default) "
    r"(language|tool|framework|stack|editor|ide|database|cloud)\b",
    "semantic",
    0.85,
    ),
    (r"\bi use\b", "semantic", 0.6),
    (r"\bi('ve| have) been (using|working with|building|shipping)\b", "semantic", 0.7),
    (r"\bi('ve| have) \d+ years? (of )?experience\b", "semantic", 0.85),
    (r"\bi('ve| have) worked (with|on|in|at)\b", "semantic", 0.7),
    (r"\bi (code|program|develop|build|ship) (in|with|using)\b", "semantic", 0.75),
    (r"\bi('m| am) (learning|studying|picking up)\b", "semantic", 0.65),
    (r"\bi switched (from|to|away from)\b", "semantic", 0.75),
    (r"\bmy (stack|setup|environment|config) (is|consists of|includes)\b", "semantic", 0.8),
    # --- Projects / Goals ---
    (r"\bi('m| am) (building|working on|developing|shipping|launching)\b", "episodic", 0.75),
    (r"\bmy (project|side project|startup|product|app|tool|library)\b", "episodic", 0.7),
    (r"\bi('m| am) (trying|planning|aiming) to\b", "episodic", 0.6),
    (r"\bmy goal (is|was|has been)\b", "episodic", 0.75),
    (r"\bi want to (build|create|make|launch|ship)\b", "episodic", 0.65),
    (r"\bi('ve| have) (built|created|made|launched|shipped|published)\b", "episodic", 0.75),
    (r"\bwe('re| are) (building|working on|developing)\b", "episodic", 0.65),

    # --- Constraints / Context ---
    (r"\bi (can't|cannot|don't|do not) (have|use|like|do|support)\b", "semantic", 0.7),
    (r"\bi('m| am) (limited to|constrained by|stuck with)\b", "semantic", 0.7),
    (r"\bi don't have (access to|time for|budget for)\b", "semantic", 0.7),
    (r"\bwe don't (use|have|support|allow)\b", "semantic", 0.65),
    (r"\bour (company|team|org) (uses|prefers|requires|forbids)\b", "semantic", 0.75),

    # --- Opinions ---
    (
    r"\bi (think|believe|feel) (that )?([\w\s]+ )?"
    r"(is|are|should|shouldn't|must|can't)\b",
    "semantic",
    0.6,
    ),
    (r"\bin my (opinion|experience|view)\b", "semantic", 0.6),
    (r"\bfrom my experience\b", "semantic", 0.6),
    (r"\bif you ask me\b", "semantic", 0.55),
    (r"\bhonestly[,]?\b", "semantic", 0.5),
]

# Roles whose messages we extract from 
USER_ROLES = {"user", "human"}

# Minimum sentence length to consider 
MIN_SENTENCE_LEN = 15

# Maximum facts to extract 
MAX_FACTS = 20


class RuleBasedExtractor(BaseExtractor):
    """
    Pattern-matching fact extractor. No LLM required.

    Works by scanning user messages for sentences that match
    known patterns indicating memorable facts. Fast, free, and
    effective for common cases like preferences and self-descriptions.
    """

    def __init__(
        self,
        min_importance: float = 0.5,
        max_facts: int = MAX_FACTS,
        extract_from_roles: set[str] | None = None,
    ) -> None:
        self.min_importance = min_importance
        self.max_facts = max_facts
        self.extract_from_roles = extract_from_roles or USER_ROLES

    def extract(self, messages: list[dict]) -> list[ExtractedFact]:
        """Extract facts from conversation messages using pattern matching."""
        facts: list[ExtractedFact] = []
        seen_content: set[str] = set()

        for message in messages:
            role = message.get("role", "").lower()
            content = message.get("content", "")

            if role not in self.extract_from_roles:
                continue
            if not content or not isinstance(content, str):
                continue

            sentences = self._split_sentences(content)

            for sentence in sentences:
                if len(sentence) < MIN_SENTENCE_LEN:
                    continue

                fact = self._match_sentence(sentence)
                if fact is None:
                    continue
                if fact.importance < self.min_importance:
                    continue

                # Deduplicate similar sentences
                normalized = sentence.lower().strip()
                if normalized in seen_content:
                    continue
                seen_content.add(normalized)

                facts.append(fact)

                if len(facts) >= self.max_facts:
                    return facts

        return facts

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences for per-sentence matching."""
        # Split on sentence-ending punctuation, keeping reasonable chunks
        raw = re.split(r"[.!?\n]+", text)
        return [s.strip() for s in raw if s.strip()]

    def _match_sentence(self, sentence: str) -> ExtractedFact | None:
        """Return the best-matching ExtractedFact for a sentence, or None."""
        lower = sentence.lower()
        best_importance = 0.0
        best_type = "semantic"

        for pattern, mem_type, importance in FACT_PATTERNS:
            if re.search(pattern, lower):
                if importance > best_importance:
                    best_importance = importance
                    best_type = mem_type

        if best_importance == 0.0:
            return None

        return ExtractedFact(
            content=sentence.strip(),
            memory_type=best_type,
            importance=best_importance,
            tags=["auto-ingested", "rule-based"],
        )