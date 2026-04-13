"""
WebLearningAgent v5 — Jarvis
Aprende de: sites normais, MDN, DevDocs, Roadmap.sh, YouTube (transcrições).
Armazena o conhecimento na memória permanente.
"""
import requests
from bs4 import BeautifulSoup


LEARN_SOURCES = {
    "javascript": [
        "https://developer.mozilla.org/pt-BR/docs/Web/JavaScript/Guide",
        "https://roadmap.sh/javascript",
    ],
    "python": [
        "https://docs.python.org/pt-br/3/tutorial/index.html",
        "https://roadmap.sh/python",
    ],
    "react": [
        "https://react.dev/learn",
        "https://roadmap.sh/react",
    ],
    "node": [
        "https://nodejs.org/en/learn/getting-started/introduction-to-nodejs",
        "https://roadmap.sh/nodejs",
    ],
    "css": [
        "https://developer.mozilla.org/pt-BR/docs/Web/CSS",
        "https://roadmap.sh/frontend",
    ],
    "sql": [
        "https://roadmap.sh/sql",
    ],
    "devops": [
        "https://roadmap.sh/devops",
    ],
    "docker": [
        "https://roadmap.sh/docker",
    ],
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


class WebLearningAgent:
    name = "web_learning"

    def execute(self, steps: list, raw_input: str = "") -> str:
        results = []
        for step in steps:
            action = step.get("action", "learn")
            query = step.get("query", raw_input)

            if action in ("learn", "search"):
                results.append(self._learn(query))
            elif action == "youtube":
                results.append(self._youtube(query))
            elif action == "fetch_page":
                results.append(self._fetch(step.get("url", "")))

        return "\n".join(results) if results else "Aprendizado concluído."

    def run(self, step: dict) -> dict:
        result = self.execute([step], step.get("query", ""))
        return {"agent": "web_learning", "result": result}

    def _learn(self, query: str) -> str:
        """Aprende sobre um tópico: fontes fixas + busca web + YouTube."""
        topic = self._clean(query)
        if not topic:
            return "Não entendi o que devo aprender."

        knowledge_parts = []

        # 1. Fontes especializadas fixas
        sources = LEARN_SOURCES.get(topic.lower(), [])
        for url in sources[:2]:
            text = self._fetch_text(url)
            if text:
                knowledge_parts.append(f"[{url}]\n{text[:800]}")

        # 2. Busca DuckDuckGo
        ddg = self._ddg_search(topic)
        if ddg:
            knowledge_parts.append(f"[Busca web]\n{ddg}")

        # 3. YouTube (transcrição)
        yt = self._youtube(topic)
        if yt and "indisponível" not in yt:
            knowledge_parts.append(f"[YouTube]\n{yt[:600]}")

        if not knowledge_parts:
            return f"Não consegui aprender sobre '{topic}'. Verifique a conexão."

        knowledge = "\n\n".join(knowledge_parts)

        # Salva na memória
        self._save(f"Conhecimento sobre {topic}:\n{knowledge[:1500]}")

        # Resume com IA
        summary = self._summarize(topic, knowledge)
        return f"Aprendi sobre {topic}:\n\n{summary}"

    def _youtube(self, query: str) -> str:
        """Extrai transcrição de vídeos do YouTube sobre o tópico."""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            import re

            # Busca o vídeo
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            r = requests.get(search_url, headers=HEADERS, timeout=10)
            # Extrai IDs de vídeo da página
            ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', r.text)
            ids = list(dict.fromkeys(ids))[:5]  # Remove duplicados, pega primeiros 5

            for vid_id in ids:
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(
                        vid_id, languages=["pt", "pt-BR", "en"]
                    )
                    text = " ".join(t["text"] for t in transcript[:80])
                    if len(text) > 200:
                        return f"Transcrição YouTube ({vid_id}):\n{text[:1000]}"
                except Exception:
                    continue

            return "Nenhuma transcrição disponível para esse tópico no YouTube."

        except ImportError:
            return "youtube_transcript_api não instalado. Rode: pip install youtube-transcript-api"
        except Exception as e:
            return f"Erro YouTube: {e}"

    def _fetch_text(self, url: str) -> str:
        """Extrai texto limpo de uma URL."""
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            # Remove ruído
            for tag in soup(["script", "style", "nav", "footer", "header",
                              "aside", "form", "button", "iframe"]):
                tag.decompose()
            # Extrai texto dos parágrafos e headings
            parts = []
            for tag in soup.find_all(["h1", "h2", "h3", "p", "li", "code"]):
                t = tag.get_text(strip=True)
                if len(t) > 30:
                    parts.append(t)
            return " ".join(parts[:60])
        except Exception:
            return ""

    def _ddg_search(self, query: str) -> str:
        """Busca no DuckDuckGo e retorna os primeiros resultados."""
        try:
            r = requests.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers=HEADERS,
                timeout=8
            )
            soup = BeautifulSoup(r.text, "html.parser")
            results = soup.select(".result__snippet")[:4]
            texts = [r.get_text(strip=True) for r in results if len(r.get_text()) > 40]
            if texts:
                return "\n".join(texts)

            # Fallback: API JSON
            r2 = requests.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": "1"},
                headers=HEADERS,
                timeout=5
            )
            data = r2.json()
            abstract = data.get("AbstractText", "")
            if abstract:
                return abstract[:600]
        except Exception:
            pass
        return ""

    def _summarize(self, topic: str, knowledge: str) -> str:
        """Usa IA para resumir o conhecimento coletado."""
        try:
            from core.models.model_router import generate_response
            prompt = f"""Você aprendeu o seguinte sobre {topic}:

{knowledge[:2000]}

Faça um resumo técnico e prático em português, destacando:
1. O que é {topic}
2. Para que serve
3. Conceitos principais
4. Como começar

Máximo 300 palavras."""
            return generate_response(prompt, task_type="analysis")
        except Exception:
            return knowledge[:500]

    def _save(self, text: str):
        try:
            from core.memory.memory_manager import save_memory
            save_memory(text)
        except Exception:
            pass

    def _clean(self, text: str) -> str:
        text = text.lower()
        for w in ["jarvis", "aprenda", "aprender", "aprenda sobre", "aprender sobre",
                  "estude", "estudar", "estude sobre", "me ensine", "me explique",
                  "quero aprender", "quero saber"]:
            text = text.replace(w, "")
        return text.strip(" .,")
