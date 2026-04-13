"""
Memory Manager — armazenamento simples em JSON.
Sem dependências pesadas. Funciona sempre.
"""
import os
import json
from datetime import datetime

MEMORY_FILE = "memory_db.json"
_data = []
_initialized = False


def init_memory():
    global _data, _initialized
    if _initialized:
        return
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                _data = json.load(f)
        except Exception:
            _data = []
    _initialized = True


def _save():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def save_memory(text: str):
    init_memory()
    _data.append({"text": text, "time": datetime.now().isoformat()})
    _save()


def save_fact(text: str):
    save_memory(text)


def search_memory(query: str, top_k: int = 3) -> list:
    init_memory()
    if not _data:
        return []
    q = query.lower()
    scored = []
    for item in _data:
        t = item.get("text", "").lower()
        # Score simples: quantidade de palavras em comum
        score = sum(1 for w in q.split() if w in t and len(w) > 2)
        if score > 0:
            scored.append((score, item["text"]))
    scored.sort(reverse=True)
    return [t for _, t in scored[:top_k]]


def get_facts() -> list:
    init_memory()
    return _data


def get_relevant_context(query: str) -> str:
    results = search_memory(query)
    return "\n".join(results) if results else ""
