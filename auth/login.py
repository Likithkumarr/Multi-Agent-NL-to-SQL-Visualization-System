import streamlit as st
import time
from db import user_coll

def login():
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        res = user_coll.get(ids=[u])

        if res["ids"] and res["metadatas"][0]["pw"] == p:
            meta = res["metadatas"][0]

            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.display_name = meta.get("name", u)

            # ✔ Do NOT create a session here!
            # ✔ We create session ONLY after user sends the first message
            st.session_state.active_session = "NEW"
            st.session_state.last_question = None

            st.success(f"Welcome {st.session_state.display_name}")
            st.balloons()
            time.sleep(1)
            st.rerun()

        else:
            st.error("Invalid Credentials")
