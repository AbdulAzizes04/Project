"""
RAG Vector Store for storing building codes and architectural standards.
"""

class ConstructionVectorStore:
    def __init__(self):
        self.docs = [
            "National Building Code 2026: Minimum bedroom dimensions 9ft x 9ft.",
            "Structural Code: Concrete slab curing time minimum 14 days.",
            "Electrical Safety: Minimum conduit depth 2 inches in plaster walls."
        ]
        
    def query(self, text: str):
        return [d for d in self.docs if any(w in d.lower() for w in text.lower().split())] or [self.docs[0]]
