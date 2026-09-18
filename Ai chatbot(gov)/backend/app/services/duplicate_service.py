"""
Duplicate Detection Service using Sentence Transformers.
Uses cosine similarity on sentence embeddings to detect semantically similar complaints.
"""
from typing import Optional, List
from loguru import logger
import numpy as np


class DuplicateDetectionService:
    def __init__(self):
        self._model = None
        self._loaded = False

    def _load_model(self):
        if self._loaded:
            return
        try:
            from sentence_transformers import SentenceTransformer
            from app.core.config import settings
            model_name = settings.SENTENCE_TRANSFORMER_MODEL
            logger.info(f"Loading Sentence Transformer: {model_name}")
            self._model = SentenceTransformer(model_name)
            self._loaded = True
            logger.info("Sentence Transformer loaded successfully.")
        except ImportError:
            logger.warning("sentence-transformers not installed. Duplicate detection disabled.")
        except Exception as e:
            logger.error(f"Failed to load Sentence Transformer: {e}")

    def is_ready(self) -> bool:
        self._load_model()
        return self._loaded

    def encode(self, text: str) -> Optional[List[float]]:
        """Encode a complaint text into a sentence embedding vector."""
        if not self.is_ready():
            return None
        try:
            embedding = self._model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
            return embedding[0].tolist()
        except Exception as e:
            logger.error(f"Encoding error: {e}")
            return None

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two unit-normalized vectors."""
        a = np.array(vec1, dtype=float)
        b = np.array(vec2, dtype=float)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        # Since embeddings are normalized, dot product equals cosine similarity
        return float(np.dot(a, b) / (norm_a * norm_b))

    def check_duplicate(
        self,
        new_text: str,
        db,
        exclude_complaint_id: Optional[str] = None,
        location: Optional[str] = None,
    ) -> dict:
        """
        Check if a new complaint is a duplicate of an existing one.

        Algorithm:
        1. Encode new complaint text
        2. Load all stored embeddings from DB
        3. Compute cosine similarity with each
        4. If similarity >= threshold, flag as duplicate
        5. Return the most similar match

        Returns:
            {
                "is_duplicate": bool,
                "similarity": float,
                "matched_complaint_id": str | None,
                "matched_complaint_number": str | None,
                "matched_description": str | None,
                "matched_location": str | None,
                "matched_status": str | None
            }
        """
        from app.core.config import settings
        from app.models.prediction import ComplaintEmbedding
        from app.models.complaint import Complaint

        if not self.is_ready():
            # Fallback: lexical n-gram / keyword similarity against existing complaints
            try:
                from app.models.complaint import Complaint
                existing = db.query(Complaint).all()
                if not existing:
                    return {
                        "is_duplicate": False,
                        "similarity": 0.0,
                        "matched_complaint_id": None,
                        "matched_complaint_number": None,
                        "matched_description": None,
                        "matched_location": None,
                        "matched_status": None,
                    }

                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.metrics.pairwise import cosine_similarity as sk_cosine
                corpus = [c.description or "" for c in existing]
                tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=1).fit(corpus + [new_text])
                corpus_vec = tfidf.transform(corpus)
                new_vec = tfidf.transform([new_text])
                sims = sk_cosine(new_vec, corpus_vec)[0]

                best_idx = int(np.argmax(sims)) if len(sims) > 0 else -1
                best_sim = float(sims[best_idx]) if best_idx >= 0 else 0.0

                if best_idx >= 0 and best_sim >= 0.72:
                    matched = existing[best_idx]
                    return {
                        "is_duplicate": True,
                        "similarity": round(best_sim, 4),
                        "matched_complaint_id": matched.id,
                        "matched_complaint_number": matched.ticket_number,
                        "matched_description": matched.description,
                        "matched_location": matched.location,
                        "matched_status": matched.status,
                    }
            except Exception as e:
                logger.error(f"Fallback similarity check error: {e}")

            return {
                "is_duplicate": False,
                "similarity": 0.0,
                "matched_complaint_id": None,
                "matched_complaint_number": None,
                "matched_description": None,
                "matched_location": None,
                "matched_status": None,
            }

        new_embedding = self.encode(new_text)
        if new_embedding is None:
            return {
                "is_duplicate": False,
                "similarity": 0.0,
                "matched_complaint_id": None,
                "matched_complaint_number": None,
                "matched_description": None,
                "matched_location": None,
                "matched_status": None,
            }

        # Load stored embeddings
        stored_embeddings = db.query(ComplaintEmbedding).all()

        best_similarity = 0.0
        best_match = None

        for stored in stored_embeddings:
            if exclude_complaint_id and stored.complaint_id == exclude_complaint_id:
                continue
            if stored.embedding is None:
                continue

            similarity = self.cosine_similarity(new_embedding, stored.embedding)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = stored

        threshold = settings.DUPLICATE_THRESHOLD

        if best_match and best_similarity >= threshold:
            # Fetch the complaint details
            complaint = db.query(Complaint).filter(
                Complaint.id == best_match.complaint_id
            ).first()

            if complaint:
                return {
                    "is_duplicate": True,
                    "similarity": round(best_similarity, 4),
                    "matched_complaint_id": complaint.id,
                    "matched_complaint_number": complaint.complaint_number,
                    "matched_description": complaint.description[:200] if complaint.description else None,
                    "matched_location": complaint.location,
                    "matched_status": complaint.status,
                }

        return {
            "is_duplicate": False,
            "similarity": round(best_similarity, 4),
            "matched_complaint_id": None,
            "matched_complaint_number": None,
            "matched_description": None,
            "matched_location": None,
            "matched_status": None,
        }

    def store_embedding(self, complaint_id: str, text: str, db) -> bool:
        """
        Compute and store the embedding for a complaint in the database.
        Called after complaint creation to enable future duplicate detection.
        """
        from app.models.prediction import ComplaintEmbedding
        import uuid
        from datetime import datetime, timezone

        embedding = self.encode(text)
        if embedding is None:
            return False

        try:
            # Remove existing embedding if any
            db.query(ComplaintEmbedding).filter(
                ComplaintEmbedding.complaint_id == complaint_id
            ).delete()

            record = ComplaintEmbedding(
                id=str(uuid.uuid4()),
                complaint_id=complaint_id,
                embedding=embedding,
                model_name=self._model.get_sentence_embedding_dimension() and "all-MiniLM-L6-v2",
                created_at=datetime.now(timezone.utc),
            )
            db.add(record)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to store embedding: {e}")
            db.rollback()
            return False


# Singleton
duplicate_service = DuplicateDetectionService()
