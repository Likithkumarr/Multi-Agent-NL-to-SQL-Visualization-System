from typing import Any, TypedDict, Optional
import pandas as pd

class AgentState(TypedDict):
    question: str
    session_id: str
    username: str
    con:Any
    sql: Optional[str]
    code: Optional[str]
    table: Optional[pd.DataFrame]
    visual: Optional[str]
    error: Optional[str]
    response: Optional[str]
    analysis_text: Optional[str]
    history: Optional[list]
    display_name: Optional[str]