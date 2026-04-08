# import re

# def router_node(state):

#     raw_q = state["question"].strip().lower()

#     q_original = raw_q
#     q = re.sub(r"[^\w\s-]", " ", raw_q)  
#     q = " ".join(q.split())

#     # NAME HANDLING
#     if any(p in q_original for p in [
#         "my name is", "call me", "my name is not",
#         "what is my name", "who am i", "tell me my name"
#     ]):
#         print("ROUTER DECISION: name_handler")
#         return "name_handler"

#     # SMALL TALK    
#     if re.match(r"^(hi|hello|hey|hii|hola|hlo)[\s\W]*", q_original):
#         print("ROUTER DECISION: chat")
#         return "chat"


#     # HISTORY
#     if any(h in q_original for h in [
#         "history", "past questions", "previous",
#         "earlier", "what did i ask",
#         "previous questions", "what are my past questions"
#     ]):
#         print("ROUTER DECISION: get_history")
#         return "get_history"
    
#     if any(x in q for x in ["why", "explain using data", "based on database", "reason", "cause", "analysis"]):
#         print("ROUTER DECISION: Unified-agent(analysis)")
#         return "unified_agent"
#     # VISUALIZATION (TOP PRIORITY)
#     VISUAL = [
#         "visualize", "visualise", "visual", "plot",
#         "graph", "chart", "draw",
#         "bar chart", "line chart", "scatter",
#         "pie chart", "heatmap", "histogram",
#         "count plot", "distribution",
#         "rating distribution",
#         "work life balance",        
#         "worklife balance",         
#         "visualization"
#     ]
#     if any(v in q_original for v in VISUAL):
#         print("ROUTER DECISION: generate_code")
#         return "generate_code"

#     # NL → SQL  (All SQL cases)
#     NL_SQL = [
#         # DDL / DML / DQL keywords
#         "modify","add","delete","update","insert","drop",
#         "create","alter","truncate",
#         # NL → SQL action keywords
#         "write a query", "give me sql","show me sql",
#         "generate sql", "make sql", "generate a query",
#         "sql for", "sql to", "query to", "query for",
#         "find", "calculate", "get me", "show me",
#         # TOP / BOTTOM / RANKING
#         "top 10", "bottom 10",
#         "top", "bottom",
#         "highest paid", "lowest paid",
#         "highest", "lowest",
#         "most", "least",
#         "order", "order by", "sorted",
#         "rank"
#     ]

#     if any(k in q_original for k in NL_SQL):
#         print("ROUTER DECISION: nl_to_sql")
#         return "nl_to_sql"

#     # GENERAL CHAT
#     if any(g in q_original for g in [
#         "explain","what is","define","describe",
#         "tell me about","meaning of","why","how does"
#     ]):
#         print("ROUTER DECISION: general_chat")
#         return "general_chat"

#     # DEFAULT → SQL
#     print("ROUTER DECISION: nl_to_sql (default)")
#     return "nl_to_sql"






from chat.chat_engine import ask_llm

def router_node(state):
    """LLM‑powered multi‑intent classifier for LangGraph routing."""
    
    user_q = state["question"]

    prompt = f"""
    You are an intent classification agent inside a LangGraph workflow.

    Your task:
    1. Carefully read the ENTIRE user message.
    2. Identify ALL user intents present in the message.
    3. Return ALL required actions as a SINGLE comma-separated list.

    VALID ACTIONS (return only these):
    chat
    name_handler
    get_history
    nl_to_sql
    generate_code
    unified_agent
    general_chat

    
    INTENT DEFINITIONS:
    1. chat  
    -> Greetings or small talk  
    Examples: "hi", "hello", "hey", "good morning"

    2. name_handler  
    -> User asking about name or identity  
    Examples: "what is my name?", "call me Likith", "my name is..."

    3. get_history  
    -> User asking about previous questions or past interactions  
    Examples: "what did I ask before?", "show my history"

    4. nl_to_sql  
    -> User wants to write or execute SQL  
    Examples:
    - "write a query"
    - "select * from employee"
    - "update table"
    - "insert into"
    - "delete"
    - "top 10 rows"
    - "find employees"

    5. generate_code  
    → User wants visualization or plotting  
    Examples:
    - "visualize"
    - "plot"
    - "chart"
    - "graph"
    - "line chart"
    - "bar chart"
    - "scatter"
    - "heatmap"

    6. unified_agent  
    -> User wants explanation, reasoning, analysis, or insight  
    Examples:
    - "why"
    - "analyze the result"
    - "explain using data"
    - "interpret the output"
    - "give insights"

    7. general_chat  
    -> General explanation that does NOT require SQL or visualization  
    Examples:
    - "what is attrition?"
    - "define job role"
    - "explain work life balance"

    MULTI-INTENT RULES (VERY IMPORTANT):

    If multiple intents appear in the same message,
    return ALL required actions in the correct order
    as a SINGLE comma-separated list.

    Examples:

    1. SQL + Visualization  
    ->nl_to_sql, generate_code

    2. SQL + Analysis  
    -> nl_to_sql, unified_agent

    3. SQL + History  
    -> get_history, nl_to_sql

    4. Visualization + Analysis  
    -> generate_code, unified_agent

    5. SQL + Visualization + Analysis  
    -> nl_to_sql, generate_code, unified_agent

    6. ANY intent + Name-related  
    -> name_handler

    7. ANY intent + Greeting  
    -> chat

    8. ANY intent + History request  
    -> get_history + other detected intents

    
    STRICT OUTPUT RULES:
    - Return ONLY the comma-separated action names.
    - Do NOT include explanations.
    - Do NOT include punctuation.
    - Do NOT include extra words.

    VALID OUTPUT EXAMPLES:
    chat
    nl_to_sql
    nl_to_sql, generate_code
    nl_to_sql, generate_code, unified_agent
    get_history, nl_to_sql

    User Question:
    {user_q}
    """

    actions = ask_llm(prompt).strip().lower()

    print(f"ROUTER DECISION: {actions}")    
    # Fallback protection: if model returns nothing
    if not actions:
        return "nl_to_sql"

    return actions