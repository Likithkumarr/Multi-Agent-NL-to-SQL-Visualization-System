import streamlit as st

def init_session():
    """
    Initializes Streamlit session_state variables.
    """
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "display_name" not in st.session_state:
        st.session_state.display_name = None
    if "active_session" not in st.session_state:
        st.session_state.active_session = None