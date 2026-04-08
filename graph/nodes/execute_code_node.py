import pandas as pd
import matplotlib.pyplot as plt
import io, base64, re

def clean_python(code: str):
    code = re.sub(r"```python", "", code)
    code = re.sub(r"```", "", code)
    return code.strip()

def execute_code_node(state):
    # CLEAN PYTHON CODE ONLY 
    code = clean_python(state["code"])
    con = state["con"]

    # Load LIVE DATA from DuckDB (not CSV)
    # df = con.execute("SELECT * FROM employee").df()

    local_env = {
        "con": con,
        # "df": df,
        "plt": plt,
        "pd": pd,
        "io": io,
        "base64": base64
    }

    try:
        exec(code, local_env)

        img = local_env.get("img_base64")

        return {
            "question": state["question"],
            "session_id": state["session_id"],
            "username": state["username"],
            "con": con,
            "history": state.get("history"),

            "code": code,
            "visual": img,
            "sql": None,
            "table": None,
            "response": "Successfully executed Python code.",
            "error": None
        }

    except Exception as e:
        return {
            "question": state["question"],
            "session_id": state["session_id"],
            "username": state["username"],
            "con": con,
            "history": state.get("history"),

            "code": code,
            "visual": None,
            "sql": None,
            "table": None,
            "response": None,
            "error": str(e)
        }