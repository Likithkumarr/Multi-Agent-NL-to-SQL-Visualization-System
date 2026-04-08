from chat.chat_engine import ask_llm
import re

def clean_python(code: str):
    code = re.sub(r"```python", "", code, flags=re.IGNORECASE)
    code = re.sub(r"```", "", code)
    return code.strip()

def generate_code_node(state):
    q = state["question"]
    con = state["con"]
    # 1 Detect which tables exist in database
    table_rows = con.execute("SHOW TABLES").fetchall()
    all_tables = [t[0] for t in table_rows]   # list of table names

    # 2 Build full schema dictionary
    schema_text = ""
    for tbl in all_tables:
        cols = con.execute(f"PRAGMA table_info('{tbl}')").df()["name"].tolist()
        schema_text += f"\nTABLE: {tbl}\nColumns: {', '.join(cols)}\n"

    # 3) Visualization Prompt
    prompt = f"""
       You are a Python data visualization generator.

       The user asked:
       "{q}"

       DATABASE STRUCTURE (IMPORTANT)
       The system has multiple tables. Here are all tables and their columns:

       {schema_text}

       RULES ABOUT COLUMNS:
       - Column names are CASE‑SENSITIVE.
       - ALWAYS use column names EXACTLY as shown above.
       - NEVER guess or modify column names.
       - If user uses wrong casing → automatically correct it.
       - If user specifies a table → use that table.
       - If user does NOT specify a table → choose the MOST relevant table.


       PYTHON RULES

       - Allowed imports ONLY:
       import pandas as pd
       import matplotlib.pyplot as plt
       import io
       import base64

       - NEVER import duckdb or open a connection.
       - ALWAYS use existing connection:
       result_df = con.execute(sql).df()

       - REQUIRED variables you MUST define:
       sql
       result_df
       img_base64

       - ALWAYS produce a matplotlib figure:
       fig = plt.figure(figsize=(10,5))

       - ALWAYS convert figure to base64:
       buffer = io.BytesIO()
       fig.savefig(buffer, format='png')
       buffer.seek(0)
       img_base64 = base64.b64encode(buffer.read()).decode()

       - DO NOT use plt.show()
       - DO NOT print anything
       - DO NOT return anything extra
       - DO NOT wrap code in markdown or backticks
       - Output ONLY raw Python code.
       """

    code = ask_llm(prompt)
    code = clean_python(code)

    return {
        "question": q,
        "session_id": state["session_id"],
        "username": state["username"],
        "con": con,
        "history": state.get("history"),

        "sql": None,
        "code": code,
        "visual": None,
        "table": None,
        "error": None,
        "response": None
    }
