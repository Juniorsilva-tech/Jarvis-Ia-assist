"""
VectorStore — usa sentence_transformers se disponível, fallback simples caso contrário.
"""
import os
import json

class VectorStore:

    def __init__(self, path="memory_db.json"):
        self.path = path
        self._model = None

        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = []
        else:
            self.data = []

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
            except ImportError:
                self._model = False  # marca como indisponível
        return self._model if self._model else None

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add(self, text: str):
        entry = {"text": text}
        model = self._get_model()
        if model:
            try:
                entry["embedding"] = model.encode(text).tolist()
            except Exception:
                pass
        self.data.append(entry)
        self.save()

    def search(self, query: str, top_k: int = 3) -> list:
        if not self.data:
            return []
        model = self._get_model()
        if model and self.data[0].get("embedding"):
            try:
                import numpy as np
                q_vec = model.encode(query)
                scored = []
                for item in self.data:
                    if "embedding" in item:
                        v = __import__("numpy").array(item["embedding"])
                        score = float(__import__("numpy").dot(q_vec, v) / (
                            __import__("numpy").linalg.norm(q_vec) * __import__("numpy").linalg.norm(v) + 1e-9
                        ))
                        scored.append((score, item["text"]))
                scored.sort(reverse=True)
                return [t for _, t in scored[:top_k]]
            except Exception:
                pass
        # Fallback simples
        q = query.lower()
        scored = []
        for item in self.data:
            t = item.get("text", "").lower()
            score = sum(1 for w in q.split() if w in t and len(w) > 2)
            if score > 0:
                scored.append((score, item["text"]))
        scored.sort(reverse=True)
        return [t for _, t in scored[:top_k]]
