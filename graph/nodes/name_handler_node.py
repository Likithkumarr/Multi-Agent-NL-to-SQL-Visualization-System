from db import user_coll

def name_handler_node(state):
    q = state["question"].lower()
    username = state["username"]

    # Fetch existing name (if any)
    user_data = user_coll.get(ids=[username])
    saved_name = user_data["metadatas"][0].get("name", username)

    reply = ""

    # USER SETS NAME 
    if "my name is" in q:
        new_name = q.split("my name is")[-1].strip().title()

        user_coll.update(
            ids=[username],
            metadatas=[{"name": new_name}],
            documents=["user"]
        )

        reply = f"Got it! I’ll remember that your name is **{new_name}**."

    # USER CHANGES NAME 
    elif "call me" in q:
        new_name = q.split("call me")[-1].strip().title()

        user_coll.update(
            ids=[username],
            metadatas=[{"name": new_name}],
            documents=["user"]
        )

        reply = f"Alright! I will call you **{new_name}** from now on."

    #  USER NEGATES WRONG NAME 
    elif "my name is not" in q:
        wrong = q.split("my name is not")[-1].strip().title()
        reply = f"Okay, I won't use **{wrong}**. What name should I remember?"

    #  USER ASKS “WHAT IS MY NAME?”
    elif "what is my name" in q or "do you know my name" in q:
        reply = f"You told me your name is **{saved_name}**."

    else:
        reply = "Okay, noted!"

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
