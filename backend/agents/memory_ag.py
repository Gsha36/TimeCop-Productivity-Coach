from autogen import ConversableAgent
from backend.tools.vector_memory import store_summary, query_memory

class MemoryAgent(ConversableAgent):
    def __init__(self, name="MemoryAgent"):
        super().__init__(name=name)

    def remember(self, user_id: str, summary: str):
        store_summary(user_id, summary)

    def recall(self, user_id: str) -> str:
        return query_memory(user_id)
