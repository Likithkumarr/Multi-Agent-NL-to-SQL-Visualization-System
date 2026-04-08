def router_entry(state):

    return {
        "question": state["question"],
        "session_id": state["session_id"],
        "username": state["username"],
        "display_name": state.get("display_name", state["username"]),
        "con": state["con"],

        # carry previous conversation context
        "history": state.get("history"),

        # ensure nothing breaks downstream
        "sql": state.get("sql"),
        "code": state.get("code"),
        "table": state.get("table"),
        "visual": state.get("visual"),
        "response": state.get("response"),
        "error": state.get("error")
    }


