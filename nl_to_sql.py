from chat.chat_engine import ask_llm

def convert_nl_to_sql(user_question: str, available_tables: list, available_columns: dict):

    # Build table list
    tables_text = ", ".join(available_tables)

    # Build column lists for all tables
    col_text = ""
    for table, cols in available_columns.items():
        col_text += f"\nTABLE {table} COLUMNS:\n" + ", ".join(cols) + "\n"

    prompt = f"""
        You are an expert DuckDB SQL generator that understands multiple tables.
        You MUST follow the exact output format with zero formatting errors.

        DATABASE INFORMATION

        Available tables:
        {tables_text}

        {col_text}

        SMART JOIN RULES (IMPORTANT)

        When user refers to multiple tables, you MUST:

        1. Identify all tables appearing in the user request.

        2. Find COMMON JOIN KEYS automatically:
        - If two tables share a column with the same name, use it as JOIN key.
        - Typical keys include:
                EmployeeNumber, EmpID, ID, DepartmentID, JobRoleID, etc.
        - Use ONLY columns that exist in BOTH tables.
        - NEVER invent join keys.
        - NEVER use columns that do not appear in both tables.

        3. If multiple join keys exist:
        - Choose the most meaningful one (EmployeeNumber > Department > Generic IDs)
        - Prefer narrow/high-cardinality keys.

        4. JOIN TYPE SELECTION:
        - Use INNER JOIN when user wants matching rows only.
        - Use LEFT JOIN when user asks for "all employees + sales data" or similar.
        - Use FULL OUTER JOIN when user says "combine", "merge fully", or "all data".

        5. If user explicitly mentions join column, use that one.
        6. If NO common key exists, respond with an error inside INSIGHT:
            "No common join key exists between tables."


        OUTPUT FORMAT (STRICT)


        For ONE query:
        TITLE: <title>
        SQL:
        <sql>

        For MULTIPLE queries:
        TITLE: <title 1>
        SQL:
        <sql>

        TITLE: <title 2>
        SQL:
        <sql>

        Always end with:
        INSIGHT:
        <short explanation of the result>

        STRICT RULES

        - FIRST line MUST be TITLE:
        - NEVER output SQL_1, TITLE_1
        - NEVER output markdown or backticks
        - ONLY SQL inside SQL block
        - Must ALWAYS include INSIGHT
        - Use ONLY available tables + columns provided above
        - No hallucinated columns or tables


        User request:
        {user_question}

        """

    return ask_llm(prompt).strip()


# from chat.chat_engine import ask_llm

# def convert_nl_to_sql(user_question: str):

#     prompt = f"""
#         You are a highly disciplined SQL generator and data analyst.
#         You MUST strictly follow the required output format and rules below.


#         REQUIRED OUTPUT FORMAT (NO EXCEPTIONS)

#         For ONE SQL query:
#         TITLE: <clear descriptive title>
#         SQL:
#         <single valid DuckDB SQL query>

#         For MULTIPLE SQL queries:
#         TITLE: <title for the first SQL query>
#         SQL:
#         <first SQL query>

#         TITLE: <title for the second SQL query>
#         SQL:
#         <second SQL query>

#         (Repeat TITLE + SQL pairs ONLY when needed)

#         After ALL SQL blocks, ALWAYS output:
#         INSIGHT:
#         <short analyst-style explanation of what the SQL results show>

#         NON‑NEGOTIABLE RULES (STRICT)

#         1. Your FIRST line MUST start with: TITLE:
#         - NOT SQL:, NOT SELECT, NOT explanation, NOT markdown.

#         2. You MUST NOT output SQL_1, SQL_2, SQL-1, SQL-2,
#         or TITLE_1, TITLE_2 under ANY circumstance.
#         If you generate those, your answer is INVALID and
#         must be regenerated internally.

#         3. You MUST ONLY output:
#         TITLE:
#         SQL:
#         INSIGHT:

#         4. NEVER output markdown or backticks.
#         NEVER output Python.
#         NEVER output comments.
#         NEVER output reasoning outside the INSIGHT block.

#         5. EVERY SQL block MUST have a TITLE block above it.

#         6. INSIGHT is MANDATORY.
#         If INSIGHT is missing, your answer is INVALID and must be regenerated.

#         7. SQL must be valid DuckDB SQL.
#         Use ONLY this table:
#         employee

#         8. USE ONLY these EXACT valid column names (case-insensitive):

#         Age, Attrition, BusinessTravel, DailyRate, Department, DistanceFromHome,
#         Education, EducationField, EmployeeCount, EmployeeNumber, EnvironmentSatisfaction,
#         Gender, HourlyRate, JobInvolvement, JobLevel, JobRole, JobSatisfaction,
#         MaritalStatus, MonthlyIncome, MonthlyRate, NumCompaniesWorked, Over18, OverTime,
#         PercentSalaryHike, PerformanceRating, RelationshipSatisfaction, StandardHours,
#         StockOptionLevel, TotalWorkingYears, TrainingTimesLastYear, WorkLifeBalance,
#         YearsAtCompany, YearsInCurrentRole, YearsSinceLastPromotion, YearsWithCurrManager

#         9. NEVER invent new columns or tables.

#         10. If ANY required block (TITLE, SQL, INSIGHT) is missing,
#             your output is INVALID — regenerate internally until correct.

#         User request: {user_question}
#         """
#     return ask_llm(prompt).strip()