# from langgraph.graph import StateGraph, END
# from graph.graph_state import AgentState

# # Core
# from graph.nodes.router_entry import router_entry
# from graph.nodes.router_node import router_node

# # SQL
# from graph.nodes.nl_to_sql_node import nl_to_sql_node
# from graph.nodes.execute_sql_node import execute_sql_node

# # Visualization
# from graph.nodes.generate_code_node import generate_code_node
# from graph.nodes.execute_code_node import execute_code_node

# # History / Chat / Other
# from graph.nodes.get_history_node import get_history_node
# from graph.nodes.chat_node import chat_node
# from graph.nodes.name_handler_node import name_handler_node
# from graph.nodes.general_chat_node import general_chat_node

# # Unified analysis agent
# from graph.nodes.unified_agent_node import unified_agent_node


# def build_graph():
#     graph = StateGraph(AgentState)

#     # ---------------------------------------
#     # REGISTER ALL NODES
#     # ---------------------------------------
#     graph.add_node("router", router_entry)

#     graph.add_node("nl_to_sql", nl_to_sql_node)
#     graph.add_node("execute_sql", execute_sql_node)

#     graph.add_node("generate_code", generate_code_node)
#     graph.add_node("execute_code", execute_code_node)

#     graph.add_node("unified_agent", unified_agent_node)

#     graph.add_node("get_history", get_history_node)
#     graph.add_node("general_chat", general_chat_node)
#     graph.add_node("name_handler", name_handler_node)
#     graph.add_node("chat", chat_node)

#     graph.set_entry_point("router")

#     # ---------------------------------------
#     # MULTI‑INTENT ROUTER FUNCTION
#     # ---------------------------------------
#     def multi_router(state):
#         actions_raw = state.get("router")

#         # Safety fallback
#         if not actions_raw or not isinstance(actions_raw, str):
#             print("⚠️ Router output missing → fallback to nl_to_sql")
#             return "nl_to_sql"

#         actions = [a.strip() for a in actions_raw.split(",") if a.strip()]

#         if len(actions) == 0:
#             return "nl_to_sql"

#         first_action = actions[0]
#         print(f"✅ ROUTER → Executing first intent: {first_action}")
#         return first_action

#     # ---------------------------------------
#     # CONDITIONAL ROUTING
#     # ---------------------------------------
#     graph.add_conditional_edges(
#         "router",
#         multi_router,
#         {
#             "nl_to_sql": "nl_to_sql",
#             "generate_code": "generate_code",
#             "unified_agent": "unified_agent",
#             "get_history": "get_history",
#             "general_chat": "general_chat",
#             "name_handler": "name_handler",
#             "chat": "chat"
#         }
#     )

#     # ---------------------------------------
#     # EXECUTION CHAIN (MULTI‑INTENT PIPELINE)
#     # ---------------------------------------

#     # SQL PIPELINE
#     graph.add_edge("nl_to_sql", "execute_sql")

#     # After SQL → if visualization requested → generate_code
#     graph.add_edge("execute_sql", "generate_code")

#     # VISUALIZATION PIPELINE
#     graph.add_edge("generate_code", "execute_code")

#     # After visualization → if analysis requested → unified_agent
#     graph.add_edge("execute_code", "unified_agent")

#     # END NODES
#     graph.add_edge("unified_agent", END)
#     graph.add_edge("general_chat", END)
#     graph.add_edge("name_handler", END)
#     graph.add_edge("chat", END)
#     graph.add_edge("get_history", END)

#     return graph.compile()

from langgraph.graph import StateGraph, END
from graph.graph_state import AgentState

# Core nodes
from graph.nodes.router_entry import router_entry
from graph.nodes.router_node import router_node

# SQL pipeline
from graph.nodes.nl_to_sql_node import nl_to_sql_node
from graph.nodes.execute_sql_node import execute_sql_node

# Visualization pipeline
from graph.nodes.generate_code_node import generate_code_node
from graph.nodes.execute_code_node import execute_code_node

# History
from graph.nodes.get_history_node import get_history_node

# Chat / small talk
from graph.nodes.chat_node import chat_node

# Name handling
from graph.nodes.name_handler_node import name_handler_node

# General AI chat fallback
from graph.nodes.general_chat_node import general_chat_node

#Analysis
from graph.nodes.unified_agent_node import unified_agent_node


def build_graph():
    graph = StateGraph(AgentState)

    # REGISTER ALL NODES
    graph.add_node("router", router_entry)

    graph.add_node("nl_to_sql", nl_to_sql_node)
    graph.add_node("execute_sql", execute_sql_node)

    graph.add_node("generate_code", generate_code_node)
    graph.add_node("execute_code", execute_code_node)

    graph.add_node("get_history", get_history_node)
    graph.add_node("chat", chat_node)
    graph.add_node("name_handler", name_handler_node)
    graph.add_node("general_chat", general_chat_node)
    graph.add_node("unified_agent", unified_agent_node)

    # ENTRY POINT
    graph.set_entry_point("router")

    # ROUTING LOGIC (DECISION NODE)
    graph.add_conditional_edges(
        "router",
        router_node,
        {
            "nl_to_sql": "nl_to_sql",
            "generate_code": "generate_code",
            "get_history": "get_history",
            "chat": "chat",
            "name_handler": "name_handler",
            "general_chat": "general_chat",
            "unified_agent": "unified_agent"
        }
    )

    # EXECUTION FLOW

    # SQL path
    graph.add_edge("nl_to_sql", "execute_sql")
    graph.add_edge("execute_sql", END)

    # Visualization path
    graph.add_edge("generate_code", "execute_code")
    graph.add_edge("execute_code", END)

    # Direct end paths
    graph.add_edge("get_history", END)
    graph.add_edge("chat", END)
    graph.add_edge("name_handler", END)
    graph.add_edge("general_chat", END)
    graph.add_edge("unified_agent", END)

    return graph.compile()