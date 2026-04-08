from chat.chat_engine import ask_llm
import pandas as pd

def unified_agent_node(state):

    con = state["con"]
    question = state["question"]

    # 1. Fetch all tables
    tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]

    # 2. Fetch full schema
    schema_info = {}
    for t in tables:
        cols = con.execute(f"PRAGMA table_info('{t}')").df()["name"].tolist()
        schema_info[t] = cols

    # 3. Build context for LLM
    db_context = "Available tables:\n"
    for t, cols in schema_info.items():
        db_context += f"- {t}: {', '.join(cols)}\n"

    prompt = f"""
        You are a unified intelligent database agent with strong analytical skills.
        You can read tables, understand schema, generate SQL, execute logic, and produce 
        professional business analysis in natural language.

        You MUST decide the best response type:
        - If user needs data → generate SQL
        - If user needs explanation → generate natural language
        - If SQL is needed → produce SQL + INSIGHT
        - If user asks for reasons, trends, patterns, or business insights → 
        provide a detailed 8–12 line analytical explanation

        DATABASE CONTEXT:
        {db_context}

        USER QUESTION:
        {question}

        RESPONSE RULES:
        1. If SQL is required → output:
            SQL:
            <query>

            INSIGHT:
            <short explanation>
        2. If SQL is NOT required → output:
            ANSWER:
            <8–12 lines of deep, natural-language, data-analyst level reasoning>
        3. NEVER output markdown or backticks.
        4. NEVER hallucinate tables or columns.
        5. Use ONLY real tables and schema.
        6. INSIGHTS must be meaningful, pattern-based, and related to available data.

        Think like a data analyst, business analyst, and SQL expert combined.
        """

    llm_output = ask_llm(prompt).strip()

    return {
        "question": question,
        "session_id": state["session_id"],
        "username": state["username"],
        "con": con,
        "history": state.get("history"),

        "sql": llm_output if llm_output.startswith("SQL:") else None,
        "response": llm_output if llm_output.startswith("ANSWER:") else None,
        "table": None,
        "visual": None,
        "code": None,
        "error": None
    }