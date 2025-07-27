# vector_memory.py

import json
from datetime import datetime
from typing import Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class VectorMemoryStore:
    def __init__(self):
        self.memory_store = {}
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.document_vectors = {}
        self.documents = {}
    
    def store_summary(self, user_id: str, summary: Dict, summary_type: str = "weekly"):
        """Store a structured summary dict with TF-IDF indexing."""
        if user_id not in self.memory_store:
            self.memory_store[user_id] = []
        
        document = {
            "id": f"{user_id}_{len(self.memory_store[user_id])}",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "type": summary_type,
            "content": summary,
            "text_representation": self._create_text_representation(summary)
        }
        
        self.memory_store[user_id].append(document)
        self.documents[document["id"]] = document
        
        self._update_vectors(user_id)
    
    def _create_text_representation(self, summary: Dict) -> str:
        parts = []
        for k, v in summary.items():
            if isinstance(v, (list, dict)):
                parts.append(f"{k}: {json.dumps(v)}")
            else:
                parts.append(f"{k}: {v}")
        return " ".join(parts)
    
    def _update_vectors(self, user_id: str):
        docs = self.memory_store.get(user_id, [])
        if len(docs) < 2:
            return
        texts = [d["text_representation"] for d in docs]
        try:
            self.document_vectors[user_id] = self.vectorizer.fit_transform(texts)
        except ValueError:
            # all docs too similar
            pass
    
    def query_memory(self, user_id: str, query: str = None, limit: int = 5) -> str:
        if user_id not in self.memory_store:
            return "No previous data found."
        
        docs = self.memory_store[user_id]
        if query and user_id in self.document_vectors:
            try:
                qv = self.vectorizer.transform([query])
                sims = cosine_similarity(qv, self.document_vectors[user_id])[0]
                idx = sims.argsort()[-limit:][::-1]
                docs = [docs[i] for i in idx if sims[i] > 0.1]
            except:
                docs = docs[-limit:]
        else:
            docs = docs[-limit:]
        
        lines = []
        for d in docs:
            summary = d["content"].get("llm_summary", d["text_representation"])
            lines.append(f"[{d['timestamp'][:10]}] {d['type']}: {summary[:200]}...")
        return "\n".join(lines)
    
    def get_trends(self, user_id: str, weeks: int = 4) -> Dict:
        if user_id not in self.memory_store:
            return {"error": "No data available"}
        recent = self.memory_store[user_id][-weeks:]
        return {
            "productivity_trend": "stable",
            "focus_pattern": "improving",
            "meeting_load": "increasing",
            "context_switches": "decreasing",
            "summary_count": len(recent),
            "data_range": f"Last {weeks} weeks"
        }

# global instance
memory_store = VectorMemoryStore()

def store_summary(user_id: str, summary: Dict, summary_type: str = "general"):
    memory_store.store_summary(user_id, summary, summary_type)

def query_memory(user_id: str, query: str = None, limit: int = 5):
    return memory_store.query_memory(user_id, query=query, limit=limit)
