# entities.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ChatRequest:
    user_id: str
    session_id: str
    message_id: str
    project_id: str
    ruler_list: List[Dict[str, str]]
    is_stream: bool
    user_query: str
