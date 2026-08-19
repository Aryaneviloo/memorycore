"""Basic MemVault usage example

Shows the full lifecycle: store-> retrieve -> reinforce -> consolidate

Run:
    python examples/basic_usage.py
"""
import os
from memvault import MemoryType, MemVault

# Initialise with default (SQlite + BGE locak embedding)

mc = MemVault(db_path="example_memories.db")

USER = "aryan"
AGENT = "jarvis"

print("=== Storing Memories ===")

m1 = mc.remember(
    "Aryan prefers Rust over Javascript",
    user_id=USER,
    agent_id=AGENT,
    memory_type=MemoryType.SEMANTIC,
    importance=0.9,
    tags=["language", "preferences"],
)

print(f"Stored: {m1.id[:8]}... | {m1.content}")

m2 = mc.remember(
    "Aryan has 6 months of python experience",
    user_id=USER,
    agent_id=AGENT,
    memory_type=MemoryType.SEMANTIC,
    importance=0.8,
)
print(f"Stored: {m2.id[:8]}... | {m2.content}")

m3 = mc.remember(
    "Aryan asked about Python decorators in the first session",
    user_id=USER,
    agent_id=AGENT,
    memory_type=MemoryType.EPISODIC,
    importance=0.6,
)
print(f"Stored: {m3.id[:8]}... | {m3.content}")

m4 = mc.remember(
    "Aryan prefers dark mode in all her tools",
    user_id=USER,
    agent_id=AGENT,
    memory_type=MemoryType.SEMANTIC,
    importance=0.7,
)
print(f"Stored: {m4.id[:8]}... | {m4.content}")

print("\n=== Semantic recall ===")

results = mc.recall(
    "what programming language does this user know?",
    user_id=USER,
    top_k=3,
)

for r in results:
    print(f"  [{r.final_score:.3f}] {r.item.content}")


print("\n=== Reinforcing a memory ===")

mc.reinforce(m1.id)
updated = mc.get(m1.id)
print(f"  access_count: {updated.access_count} | importance: {updated.importance:.3f}")

print("\n=== Recent memories ===")
recent = mc.recent(user_id=USER, limit=3)
for item in recent:
    print(f"  [{item.type.value}] {item.content[:60]}")


print("\n=== Done ===")
print("Check example_memories.db to see the stored data.")

# clean uppppp

if os.path.exists("example_memories.db"):
    os.remove("example_memories.db")
