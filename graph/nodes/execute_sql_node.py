import os
import re
import pandas as pd
from datetime import datetime

def execute_sql_node(state):
    con = state["con"]
    raw = state["sql"]
    analysis_text = None

    # ------------------------------------------
    # CLEAN RAW LLM OUTPUT (Remove anything before TITLE)
    # ------------------------------------------
    raw_low = raw.lower()
    pos = raw_low.find("title:")
    raw = raw[pos:].strip() if pos != -1 else raw.strip()

    # ------------------------------------------
    # EXTRACT INSIGHT SAFELY (DO NOT send to DuckDB)
    # ------------------------------------------
    if "insight:" in raw.lower():
        sql_part, insight_block = re.split("INSIGHT:", raw, flags=re.IGNORECASE)
        sql_part = sql_part.strip()          # ✅ ensure clean SQL-only block
        analysis_text = insight_block.strip()
    else:
        sql_part = raw.strip()

    # ------------------------------------------
    # PARSE TITLE + SQL BLOCKS
    # ------------------------------------------
    lines = sql_part.splitlines()
    results = {}
    current_title = None
    current_sql = []

    def store():
        if current_title and current_sql:
            clean_sql = "\n".join(current_sql).strip()
            results[current_title] = clean_sql

    for line in lines:
        s = line.strip()

        if s.upper().startswith("TITLE:"):
            store()
            current_title = s.split(":", 1)[1].strip()
            current_sql = []
            continue

        if s.upper().startswith("SQL:"):
            continue

        if current_title and s:
            current_sql.append(s)

    store()

    executed_sql = {}
    tables = {}

    # ------------------------------------------
    # EXECUTE EACH SQL BLOCK
    # ------------------------------------------
    try:
        for title, query in results.items():

            # ✅ Remove any INSIGHT leftovers inside query
            query = query.split("INSIGHT")[0].strip()

            executed_sql[title] = query

            res = con.execute(query)

            # SELECT returns DataFrame — TRY
            try:
                df = res.df()
            except:
                df = None

            tables[title] = df

            # ------------------------------------------
            # DETECT WRITE OPERATIONS → CSV BACKUP & SYNC
            # ------------------------------------------
            write_ops = ("update", "insert", "delete", "alter", "create", "drop")

            if query.lower().startswith(write_ops):

                # Identify table name
                match = re.match(
                    r"^(update|insert\s+into|delete\s+from|alter\s+table|create\s+table|drop\s+table)\s+(\w+)",
                    query.lower()
                )

                if match:
                    table_name = match.group(2)

                    # Validate table exists
                    all_tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]

                    if table_name in all_tables:

                        # Ensure backup folder exists
                        os.makedirs("Data/backups", exist_ok=True)

                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

                        # ✅ WINDOWS-SAFE BACKUP (no "move" operations)
                        backup_path = f"Data/backups/{table_name}_{ts}.csv"
                        con.execute(
                            f"COPY (SELECT * FROM {table_name}) TO '{backup_path}' "
                            "(HEADER, DELIMITER ',');"
                        )
                        print(f"[BACKUP SAVED] {backup_path}")

                        # ✅ ALWAYS UPDATE MAIN CSV SNAPSHOT
                        main_csv = f"Data/{table_name}.csv"
                        con.execute(
                            f"COPY (SELECT * FROM {table_name}) TO '{main_csv}' "
                            "(HEADER, DELIMITER ',');"
                        )
                        print(f"[SYNC COMPLETED] Updated {main_csv}")

                # ✅ Write database changes to disk
                con.execute("CHECKPOINT;")

        # ------------------------------------------
        # NORMAL RETURN
        # ------------------------------------------
        return {
            "question": state["question"],
            "session_id": state["session_id"],
            "username": state["username"],
            "con": con,

            "sql": executed_sql,
            "titles": list(executed_sql.keys()),
            "table": tables,
            "analysis_text": analysis_text,

            "response": "SQL executed successfully.",
            "error": None,
            "visual": None,
            "code": None,
            "history": state.get("history")
        }

    # ------------------------------------------
    # ERROR RETURN
    # ------------------------------------------
    except Exception as e:
        return {
            "question": state["question"],
            "session_id": state["session_id"],
            "username": state["username"],
            "con": con,

            "sql": results,
            "titles": list(results.keys()),
            "table": None,
            "analysis_text": analysis_text,

            "response": None,
            "error": str(e),
            "visual": None,
            "code": None,
            "history": state.get("history")
        }







# def execute_sql_node(state):
#     con = state["con"]
#     raw = state["sql"]
#     analysis_text = None
#     # 1. SMART CLEANER — strip junk before TITLE:
#     lower = raw.lower()
#     pos = lower.find("title:")
#     raw = raw[pos:].strip() if pos != -1 else raw.strip()

#     # 2. SPLIT SQL BLOCKS + INSIGHT
#     if "INSIGHT:" in raw:
#         sql_part, insight_block = raw.split("INSIGHT:", 1)
#         analysis_text = insight_block.strip()
#     else:
#         sql_part = raw

#     lines = sql_part.splitlines()
#     results = {}
#     current_title = None
#     current_sql = []

#     def store():
#         if current_title and current_sql:
#             results[current_title] = "\n".join(current_sql).strip()

#     for line in lines:
#         stripped = line.strip()

#         if stripped.upper().startswith("TITLE:"):
#             store()
#             current_title = stripped.split(":", 1)[1].strip()
#             current_sql = []
#             continue

#         if stripped.upper().startswith("SQL:"):
#             continue

#         if current_title:
#             current_sql.append(line)

#     store()
#     # 3. EXECUTE SQL
#     executed_sql = {}
#     tables = {}

#     try:
#         for title, query in results.items():
#             executed_sql[title] = query
#             res = con.execute(query)
#             try:
#                 df = res.df()
#             except:
#                 df = None
#             tables[title] = df

            
#             write_ops = ("update", "insert", "delete", "alter", "create", "drop")
#             if query.strip().lower().startswith(write_ops):
#                 try:
#                     con.execute("COPY employee TO 'Data/data.csv' (HEADER, DELIMITER ',');")
#                 except Exception as e:
#                     print("csv update failed:", str(e))
#         return {
#             "question": state["question"],
#             "session_id": state["session_id"],
#             "username": state["username"],
#             "con": con,

#             "sql": executed_sql,
#             "titles": list(executed_sql.keys()),
#             "table": tables,
#             "analysis_text": analysis_text,

#             "response": "SQL executed successfully.",
#             "error": None,
#             "visual": None,
#             "code": None,
#             "history": state.get("history")
#         }

#     except Exception as e:
#         return {
#             "question": state["question"],
#             "session_id": state["session_id"],
#             "username": state["username"],
#             "con": con,

#             "sql": results,
#             "titles": list(results.keys()),
#             "table": None,
#             "analysis_text": analysis_text,

#             "response": None,
#             "error": str(e),
#             "visual": None,
#             "code": None,
#             "history": state.get("history")
#         }
