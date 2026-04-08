import time
from db import session_coll, message_coll

# ---------- CREATE SESSION ----------
def create_session(username, session_name):
    session_id = f"{username}_{int(time.time() * 1000)}"

    session_coll.add(
        ids=[session_id],
        metadatas=[{
            "username": str(username),
            "session_name": str(session_name),
            "created": float(time.time())
        }],
        documents=["session"]
    )

    return session_id


# ---------- GET USER SESSIONS ----------
def get_user_sessions(username):
    res = session_coll.get(where={"username": username})
    return res["ids"], res["metadatas"]


# ---------- SAVE MESSAGE ----------
def save_message(session_id, username, user, sql, response, image_b64=None):

    msg_id = f"{session_id}_{int(time.time() * 1000)}"

    metadata = {
        "session_id": str(session_id),
        "username": str(username),
        "user": str(user),
        "sql": str(sql) if sql else "",
        "response": str(response) if response else "",
        "image": str(image_b64) if image_b64 else "",
        "created": float(time.time())
    }

    message_coll.add(
        ids=[msg_id],
        metadatas=[metadata],
        documents=["message"]
    )


# ---------- GET ALL MESSAGES FOR A SESSION ----------
def get_session_messages(session_id):
    res = message_coll.get(where={"session_id": session_id})
    return sorted(res["metadatas"], key=lambda x: x["created"])


# ---------- GET ALL MESSAGES FOR USER (HISTORY) ----------
def get_all_messages_for_user(username):
    res = message_coll.get(where={"username": username})
    return sorted(res["metadatas"], key=lambda x: x["created"])


# ---------- DELETE ONE SESSION ----------
def delete_session(session_id):
    msgs = message_coll.get(where={"session_id": session_id})
    if msgs["ids"]:
        message_coll.delete(ids=msgs["ids"])
    session_coll.delete(ids=[session_id])


# ---------- DELETE ALL MESSAGES FOR USER ----------
def delete_all_messages_for_user(username):
    msgs = message_coll.get(where={"username": username})
    if msgs["ids"]:
        message_coll.delete(ids=msgs["ids"])


# ---------- DELETE ALL HISTORY FOR USER ----------
def delete_all_sessions(username):
    sessions = session_coll.get(where={"username": username})

    # delete all sessions
    if sessions["ids"]:
        for sid in sessions["ids"]:
            delete_session(sid)

    # delete all messages for user
    delete_all_messages_for_user(username)


# ---------- GENERATE SESSION TITLE ----------
def generate_session_title(question):
    title = question.strip()[:30]
    return title + "..." if len(title) > 30 else title