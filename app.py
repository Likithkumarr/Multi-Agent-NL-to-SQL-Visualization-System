import streamlit as st
from utils.sessions import init_session
from auth.login import login
from auth.register import register
from chat.sidebar import render_sidebar
from utils.session_store import save_message,get_session_messages,create_session,generate_session_title
from graph.sql_visual_graph import build_graph
from duckdb_conn import get_duckdb_connection
import pandas as pd
import base64
# INIT SESSION + DUCKDB (Persistent Table)
init_session()

if "con" not in st.session_state:
    con = get_duckdb_connection()
    st.session_state.con = con

st.set_page_config(page_title="SQL Agent", layout="wide")

# LOGIN PAGE
if not st.session_state.logged_in:
    st.title("🔐 Multi-User Secure Chat")
    st.info("Don’t have an account? Register. Already have an account? Login.")

    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        login()
    with tab2:
        register()
# MAIN APP
else:
    st.title(f"Welcome {st.session_state.display_name}")
    render_sidebar()

    graph = build_graph()
    session_id = st.session_state.active_session

    # DISPLAY CHAT HISTORY
    if session_id not in [None, "NEW"]:
        history = get_session_messages(session_id)

        for msg in history:
            role = msg.get("user", "assistant")

            with st.chat_message(role):

                # Visualization history
                if msg.get("image"):
                    st.image(base64.b64decode(msg["image"]))

                # Python code history
                elif msg.get("response", "").startswith("import ") or "plt." in msg.get("response", ""):
                    st.markdown("### Python Code Used")
                    st.code(msg["response"], language="python")

                # SQL query in history
                elif msg.get("response", "").lstrip().upper().startswith(
                    ("SELECT", "UPDATE", "INSERT", "DELETE", "CREATE", "DROP", "ALTER")
                ):
                    st.markdown("### SQL Query")
                    st.code(msg["response"], language="sql")

                # General chat/history text
                elif msg.get("response"):
                    st.markdown(msg["response"])
    else:
        st.info("Start typing to begin a new chat…")

    # USER INPUT
    user_q = st.chat_input("Ask anything…")

    if user_q:

        # # Create session if needed
        if session_id in [None, "NEW"]:
            title = generate_session_title(user_q)
            sid = create_session(st.session_state.username, title)
            st.session_state.active_session = sid
            session_id = sid

        # Prevent duplicate submissions
        if st.session_state.get("last_question") == user_q:
            st.stop()
        st.session_state["last_question"] = user_q

        # Render user's query
        with st.chat_message("user"):
            st.markdown(user_q)

        save_message(session_id, st.session_state.username, "user", "", user_q)

        # PROCESS THROUGH LANGGRAPH
        answer = graph.invoke({
            "question": user_q,
            "session_id": session_id,
            "username": st.session_state.username,
            "con": st.session_state.con,
        })

        # DISPLAY ASSISTANT OUTPUT
        with st.chat_message("assistant"):

            # GENERAL CHAT RESPONSE
            if answer.get("response"):
                st.markdown(answer["response"])

            #  SQL DISPLAY — handle dict OR string
            if answer.get("sql") and answer.get("visual") is None:
                st.markdown("### SQL Query")

                sql_block = answer["sql"]

                if isinstance(sql_block, dict):
                    for title, query in sql_block.items():
                        st.markdown(f"#### {title}")
                        st.code(query, language="sql")
                else:
                    st.code(sql_block, language="sql")

            #  TABLE DISPLAY — multi-table dict
            if isinstance(answer.get("table"), dict):
                for title, df in answer["table"].items():
                    st.markdown(f"### Result – {title}")
                    if df is not None:
                        st.dataframe(df)
                    else:
                        st.info("No results for this query.")

            #  Single table fallback
            elif answer.get("table") is not None:
                st.markdown("### Result")
                st.dataframe(answer["table"])

            #  INSIGHT
            if answer.get("analysis_text"):
                st.markdown("### Insight")
                st.markdown(answer["analysis_text"])

            #  PYTHON CODE
            if answer.get("code"):
                st.markdown("### Python Code Used")
                st.code(answer["code"], language="python")

            #  VISUALIZATION
            if answer.get("visual"):
                st.markdown("### Visualization")
                st.image(base64.b64decode(answer["visual"]))

            #  HISTORY DISPLAY
            if answer.get("history"):
                st.markdown("### Your Previous Questions")
                for h in answer["history"]:
                    st.markdown(f"- {h}")

            #  ERROR
            if answer.get("error"):
                st.error(answer["error"])

        # SAVE ASSISTANT RESPONSE (FIXED FOR dict OR string SQL)
        assistant_text = ""

        #  Save GENERAL chat response
        if answer.get("response"):
            save_message(
                session_id,
                st.session_state.username,
                "assistant",
                "",
                answer["response"]
            )

        #  Save SQL text correctly
        if answer.get("sql"):
            assistant_text += "### SQL Query\n"

            sql_block = answer["sql"]

            # dict style (multi-SQL)
            if isinstance(sql_block, dict):
                for title, query in sql_block.items():
                    assistant_text += f"#### {title}\n```sql\n{query}\n```\n"

            # string style (unified agent)
            else:
                assistant_text += f"```sql\n{sql_block}\n```\n"

        #  Save TABLE outputs
        if isinstance(answer.get("table"), dict):
            for title, df in answer["table"].items():
                assistant_text += f"### Result – {title}\n"
                if df is not None:
                    assistant_text += df.to_markdown(index=False) + "\n\n"

        #  Save INSIGHT
        if answer.get("analysis_text"):
            assistant_text += "### Insight\n" + answer["analysis_text"] + "\n\n"

        #  Save ERROR
        if answer.get("error"):
            assistant_text += f"\n❌ {answer['error']}"

        #  Save compiled assistant block
        if assistant_text.strip():
            save_message(
                session_id,
                st.session_state.username,
                "assistant",
                answer.get("sql", ""),
                assistant_text
            )

        #  Save Python code
        if answer.get("code"):
            save_message(
                session_id,
                st.session_state.username,
                "assistant",
                "",
                answer["code"]
            )

        #  Save Visualization
        if answer.get("visual"):
            save_message(
                session_id,
                st.session_state.username,
                "assistant",
                "",
                "",
                image_b64=answer["visual"]
            )

       # st.rerun() # removed intentionally