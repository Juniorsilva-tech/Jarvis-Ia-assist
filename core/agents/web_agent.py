"""
WebAgent v5 — lê sites reais, abre URLs, clona sites.
Usa Playwright para sites com JavaScript pesado.
"""
import webbrowser
import requests
from typing import Optional


class WebAgent:
    name = "web"

    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    def execute(self, steps: list, raw_input: str = "") -> str:
        results = []
        for step in steps:
            action = step.get("action", "")
            if action in ("search", "search_web"):
                results.append(self._search(step.get("query", raw_input)))
            elif action == "clone_site":
                from core.automation.site_cloner import clone_site
                results.append(clone_site(step.get("url", raw_input)))
            elif action == "fetch_url":
                results.append(self._fetch(step.get("url", "")))
            elif action in ("open_url", "open_site", "open"):
                url = step.get("url", raw_input)
                if not url.startswith("http"):
                    url = "https://" + url
                webbrowser.open(url)
                results.append(f"Abrindo: {url}")
            else:
                url = step.get("url", raw_input)
                if url.startswith("http"):
                    webbrowser.open(url)
                    results.append(f"Abrindo: {url}")
                else:
                    results.append(self._search(raw_input))
        return "\n".join(results) if results else "Ação web concluída."

    def run(self, step: dict) -> dict:
        result = self.execute([step], step.get("query", step.get("url", "")))
        return {"agent": "web", "result": result}

    def _search(self, query: str) -> str:
        # 1. DuckDuckGo API
        result = self._ddg_api(query)
        if result:
            return result
        # 2. DuckDuckGo HTML scrape
        result = self._ddg_html(query)
        if result:
            return result
        # 3. Abre no navegador como fallback
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Pesquisando no Google: {query}"

    def _ddg_api(self, query: str) -> Optional[str]:
        try:
            r = requests.get("https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"},
                headers=self.HEADERS, timeout=5)
            data = r.json()
            abstract = data.get("AbstractText", "")
            if abstract:
                return f"Resultado para '{query}':\n{abstract[:500]}"
            topics = data.get("RelatedTopics", [])
            if topics and isinstance(topics[0], dict):
                text = topics[0].get("Text", "")
                if len(text) > 30:
                    return f"Sobre '{query}':\n{text[:400]}"
        except Exception:
            pass
        return None

    def _ddg_html(self, query: str) -> Optional[str]:
        try:
            from bs4 import BeautifulSoup
            r = requests.get("https://html.duckduckgo.com/html/",
                params={"q": query}, headers=self.HEADERS, timeout=8)
            soup = BeautifulSoup(r.text, "html.parser")
            snippets = soup.select(".result__snippet")[:3]
            texts = [s.get_text(strip=True) for s in snippets if len(s.get_text()) > 40]
            if texts:
                return f"Resultados para '{query}':\n" + "\n".join(texts)
        except Exception:
            pass
        return None

    def _fetch(self, url: str) -> str:
        """Lê o conteúdo real de uma URL."""
        if not url.startswith("http"):
            url = "https://" + url
        # Tenta com requests + BeautifulSoup
        result = self._fetch_requests(url)
        if result:
            return result
        # Tenta com Playwright (sites JS pesados)
        result = self._fetch_playwright(url)
        if result:
            return result
        return f"Não consegui ler o conteúdo de {url}"

    def _fetch_requests(self, url: str) -> Optional[str]:
        try:
            from bs4 import BeautifulSoup
            r = requests.get(url, headers=self.HEADERS, timeout=12)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer",
                              "header", "aside", "form", "button"]):
                tag.decompose()
            parts = []
            for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
                t = tag.get_text(strip=True)
                if len(t) > 20:
                    parts.append(t)
            text = " ".join(parts[:80])
            if len(text) > 100:
                return f"Conteúdo de {url}:\n{text[:800]}"
        except Exception:
            pass
        return None

    def _fetch_playwright(self, url: str) -> Optional[str]:
        """Para sites com JavaScript pesado (YouTube, SPAs, etc)."""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=15000)
                page.wait_for_timeout(2000)
                text = page.inner_text("body")
                browser.close()
                if text:
                    return f"Conteúdo (JS) de {url}:\n{text[:800]}"
        except ImportError:
            pass  # Playwright não instalado — não é crítico
        except Exception:
            pass
        return None
