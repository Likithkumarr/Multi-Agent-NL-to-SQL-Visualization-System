from utils.session_store import get_all_messages_for_user

def get_history_node(state):
    username = state["username"]
    msgs = get_all_messages_for_user(username)

    questions = [
        m["response"] for m in msgs
        if m.get("user") == "user"
    ]

    return {
        "question": state["question"],
        "session_id": state["session_id"],
        "username": state["username"],
        "con": state["con"],

        "history": questions,
        "sql": None,
        "code": None,
        "table": None,
        "visual": None,
        "error": None
    }

