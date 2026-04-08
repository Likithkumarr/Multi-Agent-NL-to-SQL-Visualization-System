from chat.chat_engine import ask_llm
from db import user_coll

def general_chat_node(state):
    q = state["question"]
    username = state["username"]

    # pull saved user name
    user_data = user_coll.get(ids=[username])
    saved_name = user_data["metadatas"][0].get("name", username)

    prompt = f"""
    The user asked: "{q}"

    You are a helpful AI assistant with personalized memory.

    IMPORTANT:
    - The user's saved name is: {saved_name}.
    - If the question refers to "my name", use the saved name.
    - DO NOT generate SQL, Python, plots, or code unless the user asks.
    - Provide a friendly, clear, natural-language response.
    - If the user greets you, greet them using their saved name.
    - Respond in a conversational tone like ChatGPT.
    """

    reply = ask_llm(prompt)

    return {
        "question": state["question"],
        "session_id": state["session_id"],
        "username": username,
        "display_name": saved_name,
        "con": state["con"],
        "history": state.get("history"),

        "sql": None,
        "code": None,
        "table": None,
        "visual": None,
        "response": reply,
        "error": None
    }