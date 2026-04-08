from nl_to_sql import convert_nl_to_sql
import re

def clean_sql(sql: str):
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```", "", sql)
    sql = re.sub(r"`", "", sql)
    return sql.strip()

def nl_to_sql_node(state):

    con = state["con"]

    # 1. GET ALL TABLES IN DATABASE
    table_rows = con.execute("SHOW TABLES").fetchall()
    available_tables = [t[0] for t in table_rows]  # ['employee', 'sales', 'finance', ...]

    # 2. GET COLUMNS FOR EACH TABLE
    available_columns = {}
    for table in available_tables:
        df = con.execute(f"PRAGMA table_info('{table}')").df()
        available_columns[table] = df["name"].tolist()

    # 3. CALL MULTI‑TABLE NL2SQL GENERATOR
    raw_sql = convert_nl_to_sql(
        user_question=state["question"],
        available_tables=available_tables,
        available_columns=available_columns
    )

    cleaned_sql = clean_sql(raw_sql)

    # 4. RETURN CLEAN SQL TO GRAPH
    return {
        "question": state["question"],
        "session_id": state["session_id"],
        "username": state["username"],
        "con": con,
        "history": state.get("history"),

        "sql": cleaned_sql,
        "code": None,
        "table": None,
        "visual": None,
        "error": None
    }










# from nl_to_sql import convert_nl_to_sql
# import re

# def clean_sql(sql: str):
#     sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
#     sql = re.sub(r"```", "", sql)
#     sql = re.sub(r"`", "", sql)
#     return sql.strip()

# def nl_to_sql_node(state):
#     sql = convert_nl_to_sql(state["question"])
#     cleaned = clean_sql(sql)

#     return {
#         "question": state["question"],
#         "session_id": state["session_id"],
#         "username": state["username"],
#         "con": state["con"],
#         "history": state.get("history"),

#         "sql": cleaned,
#         "code": None,
#         "table": None,
#         "visual": None,
#         "error": None
#     }

