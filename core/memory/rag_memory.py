"""
RAG Memory Manager - Jarvis v2
Memória híbrida: ChromaDB (vetorial) + JSON (fatos/histórico)
"""

import json
import os
from datetime import datetime
from typing import Optional

# ─── ChromaDB (pip install chromadb) ────────────────────────────────────────
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️  ChromaDB não instalado. Execute: pip install chromadb")

MEMORY_FILE = "memory/memory.json"
CHROMA_PATH = "memory/chroma_db"


class RagMemoryManager:
    """
    Memória híbrida com busca vetorial + fatos persistentes.
    
    Uso:
        mem = RagMemoryManager()
        mem.save_interaction("abrir chrome", "Abrindo navegador")
        contexto = mem.get_relevant_context("abrir navegador")
    """

    def __init__(self):
        self._init_json_memory()
        self._init_chroma()

    # ── JSON Store (fatos + histórico) ────────────────────────────────────────

    def _init_json_memory(self):
        os.makedirs("memory", exist_ok=True)
        if not os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump({"facts": [], "history": [], "patterns": {}}, f)

    def _load(self) -> dict:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_fact(self, text: str):
        """Salva um fato importante (ex: nome do usuário, preferências)."""
        data = self._load()
        data["facts"].append({
            "text": text,
            "timestamp": str(datetime.now())
        })
        # Mantém só os últimos 100 fatos
        data["facts"] = data["facts"][-100:]
        self._save(data)

    def save_history(self, user_input: str, jarvis_response: str):
        """Salva uma interação no histórico."""
        data = self._load()
        data["history"].append({
            "user": user_input,
            "jarvis": jarvis_response,
            "timestamp": str(datetime.now())
        })
        data["history"] = data["history"][-200:]
        self._save(data)

    def get_facts(self) -> list[dict]:
        return self._load()["facts"]

    def get_recent_history(self, n: int = 5) -> list[dict]:
        return self._load()["history"][-n:]

    # ── ChromaDB (memória vetorial) ────────────────────────────────────────────

    def _init_chroma(self):
        if not CHROMA_AVAILABLE:
            self.collection = None
            return
        try:
            os.makedirs(CHROMA_PATH, exist_ok=True)
            client = chromadb.PersistentClient(path=CHROMA_PATH)
            
            # Usa embeddings locais (sem API externa)
            ef = embedding_functions.DefaultEmbeddingFunction()
            
            self.collection = client.get_or_create_collection(
                name="jarvis_memory",
                embedding_function=ef,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"✅ ChromaDB iniciado — {self.collection.count()} memórias salvas")
        except Exception as e:
            print(f"⚠️  Erro ao iniciar ChromaDB: {e}")
            self.collection = None

    def save_interaction(self, user_input: str, jarvis_response: str):
        """Salva interação no vetor + histórico JSON."""
        self.save_history(user_input, jarvis_response)

        if not self.collection:
            return

        try:
            doc_id = f"interaction_{datetime.now().timestamp()}"
            self.collection.add(
                documents=[f"Usuário: {user_input}\nJarvis: {jarvis_response}"],
                ids=[doc_id],
                metadatas=[{
                    "user_input": user_input,
                    "jarvis_response": jarvis_response[:200],
                    "timestamp": str(datetime.now())
                }]
            )
        except Exception as e:
            print(f"⚠️  Erro ao salvar no ChromaDB: {e}")

    def get_relevant_context(self, query: str, n_results: int = 3) -> str:
        """
        Busca memórias relevantes para o contexto atual (RAG).
        Retorna string formatada para injetar no prompt.
        """
        parts = []

        # 1. Fatos importantes
        facts = self.get_facts()
        if facts:
            fact_texts = [f["text"] for f in facts[-10:]]
            parts.append("📌 Fatos sobre o usuário:\n" + "\n".join(f"- {t}" for t in fact_texts))

        # 2. Histórico recente
        recent = self.get_recent_history(3)
        if recent:
            hist_lines = [f"[{h['timestamp'][:16]}] Usuário: {h['user']} → Jarvis: {h['jarvis'][:100]}"
                         for h in recent]
            parts.append("🕐 Histórico recente:\n" + "\n".join(hist_lines))

        # 3. Memórias vetoriais relevantes (RAG)
        if self.collection and self.collection.count() > 0:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=min(n_results, self.collection.count())
                )
                if results and results["documents"] and results["documents"][0]:
                    similar = results["documents"][0]
                    parts.append("🧠 Contexto similar encontrado:\n" +
                                 "\n".join(f"- {doc[:120]}..." for doc in similar))
            except Exception as e:
                print(f"⚠️  Erro na busca vetorial: {e}")

        return "\n\n".join(parts) if parts else ""

    def learn_pattern(self, intent: str, success: bool):
        """Registra se um padrão de ação funcionou (aprendizado contínuo)."""
        data = self._load()
        patterns = data.get("patterns", {})
        if intent not in patterns:
            patterns[intent] = {"success": 0, "failure": 0}
        if success:
            patterns[intent]["success"] += 1
        else:
            patterns[intent]["failure"] += 1
        data["patterns"] = patterns
        self._save(data)


# Instância global (singleton)
_memory = None

def get_memory() -> RagMemoryManager:
    global _memory
    if _memory is None:
        _memory = RagMemoryManager()
    return _memory