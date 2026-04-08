from chat.chat_engine import ask_llm
def chat_node(state):
    q = state["question"]
    prompt = f"""
    You are a friendly conversational assistant.
    Respond naturally to the user's message.

    User: {q}
    Assistant:
    """
    reply = ask_llm(prompt).strip()

    return {
        "question": state["question"],
        "session_id": state["session_id"],
        "username": state["username"],
        "con": state["con"],
        "history": state.get("history"),

        "sql": None,
        "code": None,
        "table": None,
        "visual": None,
        "response": reply,
        "error": None
    }