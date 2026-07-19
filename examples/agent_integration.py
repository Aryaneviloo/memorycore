"""
Example: Using MemVault as a memory layer for an AI agent.

Shows the pattern for auto-retrieving context before a response
and auto-storing facts after. Uses a mock LLM to avoid API keys.

Run:
    python examples/agent_integration.py
"""


from memvault import MemVault, MemoryType


def mock_llm_respond(prompt: str) -> str:
    """
    Simulates an LLM response (replace with real API call)
    """

    if "python" in prompt.lower():
        return "I see you are interested in Python; what would you like to know?"
    return "That is interesting! Tell me more"

def mock_extract_facts(user_message: str, response: str) -> list[str]:
    """
    Simulates fact extraction from a conversation turn
    In production this would be LLM call:
        "Given this conversation, what facts are worth remembering?"
    """

    facts = []
    if "prefer" in user_message.lower() or "like" in user_message.lower():
        facts.append(user_message)
    return facts

def chat(mc: MemVault, user_id: str, user_message: str) -> str:
    
    """
    One turn of a memory augmented conversation
    
    Pattern:
    1. Retrieve relevant memories
    2. Build context augmented prompt
    3. Get LLM response
    4. Extract and store memorable facts
    
    """

    #Step 1: retreive relevant information
    memories = mc.recall(user_message, user_id=user_id, top_k=3)

    #Step 2 build augmented prompt
    context_lines = [f" - {r.item.content}" for r in memories]
    context = "\n".join(context_lines) if context_lines else "No prior context"

    prompt = f"""Known context about this user:
{context}


User says: {user_message}
Respond helpfully:"""
    
    #Step 3: get response

    response = mock_llm_respond(prompt)

    #Step 4: extract and store facts

    facts = mock_extract_facts(user_message, response)
    for fact in facts:
        mc.remember(
            fact,
            user_id=user_id,
            agent_id="jarvis",
            memory_type=MemoryType.SEMANTIC,
            importance=0.7,
            source="conversation",
        )

    return response

def main():
    mc = MemVault(db_path="agent_example.db")
    user_id = "bob"

    print ("===Memory augmented agent demo===\n")


    turns = [
        "I really prefer Python for all my projects",
        "What is the best way to learn decorators?",
        "I work in data science",
        "What do you remember about my preferences?"

    ]

    for message in turns:
        print(f"User: {message}")

        response = chat(mc, user_id, message)

        print(f"Agent: {response}")

        memories = mc.recent(user_id=user_id, limit = 2)
        if memories:
            print(f" [memory] stored: '{memories[0].content[:50]}...'")
        print()

    print(f"Total memories stored: {len(mc.recent(user_id=user_id, limit=100))}")

    import os
    if os.path.exists("agent_example.db"):
        os.remove("agent_example.db")


if __name__ == "__main__":
    main()



    