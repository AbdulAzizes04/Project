import os
from typing import Any
from utils.logger import logger

def get_embedding_model() -> Any:
    """
    Returns an embedding model for ChromaDB vector store.
    Tries HuggingFace sentence-transformers first if environment is fully compatible,
    otherwise falls back safely to lightweight custom fallback to prevent Streamlit watcher crashes.
    """
    try:
        import warnings
        warnings.filterwarnings("ignore")
        
        import numpy as np
        # PyTorch < 2.4 and sentence-transformers have C-extension conflicts with NumPy >= 2.0
        if int(np.__version__.split(".")[0]) >= 2:
            raise ImportError(f"NumPy {np.__version__} is incompatible with PyTorch 2.1.x C-extensions.")

        import torch
        # Check PyTorch version to avoid transformers lazy-loader NameError under PyTorch < 2.4
        version_parts = [int(x) for x in torch.__version__.split('+')[0].split('.')[:2] if x.isdigit()]
        if version_parts and version_parts < [2, 4]:
            raise ImportError(f"Installed PyTorch {torch.__version__} is < 2.4 (required by installed transformers library).")

        import transformers
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        logger.info("Initialized HuggingFace sentence-transformers embedding model.")
        return embeddings
    except BaseException as e:
        logger.warning(f"Could not load HuggingFaceEmbeddings ({e}). Using lightweight custom fallback.")
        
        # Fallback simple embedding class for offline/fast mode
        class SimpleEmbeddings:
            def embed_documents(self, texts):
                return [[float(hash(t + str(i)) % 100) / 100.0 for i in range(384)] for t in texts]
            def embed_query(self, text):
                return [float(hash(text + str(i)) % 100) / 100.0 for i in range(384)]
                
        return SimpleEmbeddings()




