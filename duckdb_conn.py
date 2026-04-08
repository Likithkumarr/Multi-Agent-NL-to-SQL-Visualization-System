import duckdb
import pandas as pd
import os

DB_PATH = "database.duckdb"

def get_duckdb_connection():
    """
    Creates or opens a persistent DuckDB database file.
    Loads the CSV ONLY if table does not exist.
    """
    # Create / open file-based database
    con = duckdb.connect(DB_PATH)

    # Check if employee table exists
    tables = con.execute("SHOW TABLES").fetchall()

    if ("employee",) not in tables:
        df = pd.read_csv("Data/data.csv")
        con.execute("CREATE TABLE employee AS SELECT * FROM df")

    return con
