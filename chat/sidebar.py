import streamlit as st
from utils.session_store import get_user_sessions, create_session, delete_all_sessions

def render_sidebar():
    username = st.session_state.username

    st.sidebar.header(f"👤 {st.session_state.display_name}'s Sidebar")

    ids, metas = get_user_sessions(username)

    # NEW CHAT (no session until first message)
    if st.sidebar.button("➕ New Chat Session", use_container_width=True):
        st.session_state.active_session = "NEW"
        st.session_state.chat_started = False
        st.rerun()

    # CLEAR CURRENT
    if st.sidebar.button("🧹 Clear Current Screen", use_container_width=True):
        st.session_state.active_session = "NEW"
        st.rerun()

    # DELETE ALL HISTORY
    if st.sidebar.button("🗑 DELETE ALL MY HISTORY", use_container_width=True):
        delete_all_sessions(username)
        st.session_state.active_session = "NEW"
        st.rerun()

    # LOGOUT
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 Your Past Chats")

    if not metas:
        st.sidebar.info("No past chats yet.")
        return

    # show all sessions
    for sid, meta in zip(ids, metas):
        title = meta["session_name"]
        short_title = (title[:20] + "…") if len(title) > 20 else title

        if st.sidebar.button(f"💬 {short_title}", key=f"session_{sid}", use_container_width=True):
            st.session_state.active_session = sid
            st.rerun()