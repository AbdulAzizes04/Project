import os
from typing import List
from langchain_community.vectorstores import Chroma
from rag.embeddings import get_embedding_model
from database.sqlite_db import db_manager
from utils.logger import logger

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

class SchemaRAGRetriever:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.vectorstore = None
        self.embeddings = get_embedding_model()
        self._build_index()

    def _build_index(self):
        """Indexes table columns and descriptions into ChromaDB vector database."""
        try:
            schema = db_manager.get_table_schema(self.table_name)
            if not schema:
                return

            documents = []
            metadatas = []

            for col in schema:
                doc_text = f"Table {self.table_name} column '{col['name']}' has data type {col['type']}. It stores information regarding {col['name']}."
                documents.append(doc_text)
                metadatas.append({"column": col["name"], "type": col["type"], "table": self.table_name})

            # Create Chroma vectorstore
            self.vectorstore = Chroma.from_texts(
                texts=documents,
                embedding=self.embeddings,
                metadatas=metadatas,
                persist_directory=os.path.join(CHROMA_DIR, self.table_name)
            )
            logger.info(f"ChromaDB schema vector index built for table '{self.table_name}' with {len(documents)} columns.")
        except Exception as e:
            logger.error(f"Error building ChromaDB schema vector index: {e}")

    def get_relevant_context(self, query: str, k: int = 3) -> str:
        """Retrieves top-k relevant column schema documents for a user question."""
        if not self.vectorstore:
            return ""

        try:
            results = self.vectorstore.similarity_search(query, k=k)
            retrieved_texts = [f"- {doc.page_content}" for doc in results]
            return "\n".join(retrieved_texts)
        except Exception as e:
            logger.error(f"Error retrieving from ChromaDB: {e}")
            return ""

def get_schema_retriever(table_name: str) -> SchemaRAGRetriever:
    return SchemaRAGRetriever(table_name)
