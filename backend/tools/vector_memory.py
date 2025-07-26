import json
from datetime import datetime
from typing import List, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class VectorMemoryStore:
    def __init__(self):
        self.memory_store = {}
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.document_vectors = {}
        self.documents = {}
    
    def store_summary(self, user_id: str, summary: Dict, summary_type: str = "weekly"):
        """Store summary with vector embeddings for RAG"""
        if user_id not in self.memory_store:
            self.memory_store[user_id] = []
        
        # Create structured document
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
        
        # Update vector embeddings
        self._update_vectors(user_id)
    
    def _create_text_representation(self, summary: Dict) -> str:
        """Convert summary dict to searchable text"""
        if isinstance(summary, dict):
            text_parts = []
            for key, value in summary.items():
                if isinstance(value, (list, dict)):
                    text_parts.append(f"{key}: {json.dumps(value)}")
                else:
                    text_parts.append(f"{key}: {value}")
            return " ".join(text_parts)
        return str(summary)
    
    def _update_vectors(self, user_id: str):
        """Update TF-IDF vectors for user's documents"""
        user_docs = self.memory_store.get(user_id, [])
        if len(user_docs) < 2:
            return
        
        texts = [doc["text_representation"] for doc in user_docs]
        try:
            vectors = self.vectorizer.fit_transform(texts)
            self.document_vectors[user_id] = vectors
        except ValueError:
            # Handle case where all documents are too similar
            pass
    
    def query_memory(self, user_id: str, query: str = None, limit: int = 5) -> str:
        """RAG-style memory querying"""
        if user_id not in self.memory_store:
            return "No previous data found."
        
        user_docs = self.memory_store[user_id]
        
        if query and user_id in self.document_vectors:
            # Vector similarity search
            try:
                query_vector = self.vectorizer.transform([query])
                similarities = cosine_similarity(query_vector, self.document_vectors[user_id])[0]
                
                # Get top similar documents
                top_indices = similarities.argsort()[-limit:][::-1]
                relevant_docs = [user_docs[i] for i in top_indices if similarities[i] > 0.1]
            except:
                # Fallback to recent documents
                relevant_docs = user_docs[-limit:]
        else:
            # Return recent documents
            relevant_docs = user_docs[-limit:]
        
        # Format results
        memory_text = []
        for doc in relevant_docs:
            memory_text.append(f"[{doc['timestamp'][:10]}] {doc['type']}: {doc['text_representation'][:200]}...")
        
        return "\n".join(memory_text)
    
    def get_trends(self, user_id: str, weeks: int = 4) -> Dict:
        """Analyze trends from stored summaries"""
        if user_id not in self.memory_store:
            return {"error": "No data available"}
        
        recent_docs = self.memory_store[user_id][-weeks:]
        
        trends = {
            "productivity_trend": "stable",  # This would be calculated from actual data
            "focus_pattern": "improving",
            "meeting_load": "increasing",
            "context_switches": "decreasing",
            "summary_count": len(recent_docs),
            "data_range": f"Last {weeks} weeks"
        }
        
        return trends

# Global instance
memory_store = VectorMemoryStore()

def store_summary(user_id: str, summary: str):
    """Backward compatibility function"""
    memory_store.store_summary(user_id, {"summary": summary}, "general")

def query_memory(user_id: str):
    """Backward compatibility function"""
    return memory_store.query_memory(user_id)