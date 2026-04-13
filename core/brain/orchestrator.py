"""
Orchestrator v7 — detecta projetos complexos por voz.
"""
from core.agents.registry import get_agents
from core.router.agent_router import AgentRouter
import re

APPS = ["spotify","chrome","firefox","edge","discord","whatsapp","telegram",
        "vscode","code","notepad","bloco de notas","calculadora","calc",
        "steam","vlc","obs","word","excel","powershell","terminal","cmd","explorer"]

PROJECT_TRIGGERS = [
    "site de", "site para", "sistema de", "plataforma de",
    "e-commerce", "ecommerce", "loja virtual", "loja online",
    "coloca backend", "adiciona backend", "faz um site",
    "cria um site", "desenvolve um site", "desenvolva um site",
    "cria um sistema", "fullstack", "com pagamento", "com carrinho",
    "com agendamento", "mercado livre", "tipo mercado"
]


class Orchestrator:
    def __init__(self):
        self.agents = get_agents()
        self.router = AgentRouter(self.agents)
        self._last_agent = "chat"

    def get_last_agent(self): return self._last_agent

    def detect_intent(self, text: str) -> str:
        t = text.lower()

        # Projetos completos — prioridade máxima
        if any(kw in t for kw in PROJECT_TRIGGERS):
            return "code"

        # Apps — sempre system
        if any(app in t for app in APPS):
            if any(w in t for w in ["abrir","abre","abra","iniciar","inicia",
                                     "fechar","fecha","toca","coloca","pause"]):
                return "system"

        # Música/mídia
        if any(w in t for w in ["spotify","música","musica","playlist",
                                  "volume","pausar","próxima música"]):
            return "system"

        # Sistema
        if any(w in t for w in ["screenshot","hora","horas","que horas",
                                  "que dia","data","cpu","ram"]):
            return "system"
        if any(w in t for w in ["abrir","abre","abra","iniciar","fechar",
                                  "fecha","execute","rodar"]):
            return "system"

        # Busca explícita
        if any(w in t for w in ["pesquise","pesquisar","busque","buscar",
                                  "pesquisa sobre","google"]):
            return "browser"

        # Aprendizado
        if any(w in t for w in ["aprenda","aprender","estude","estudar"]):
            return "web_learning"

        # Código simples
        if any(w in t for w in ["codigo","código","programa","script","função",
                                  "javascript","react","node","html","css","python",
                                  "gera","cria","clone","clonar"]):
            return "code"

        if any(w in t for w in ["mouse","teclado","clica","digita"]):
            return "computer"

        if any(w in t for w in ["lembre","memorize","salva isso","guarda",
                                  "não esqueça","minhas memórias"]):
            return "memory"

        if re.search(r'https?://', t) or ".com" in t or ".br" in t:
            return "web"

        return "chat"

    def create_plan(self, intent: str, user_input: str) -> dict:
        plan = {"agent": intent, "steps": [], "raw_input": user_input}
        t = user_input.lower()

        if intent == "browser":
            q = user_input
            for w in ["pesquise","pesquisar","busque","buscar","google","jarvis"]:
                q = q.lower().replace(w, "").strip()
            plan["steps"].append({"action": "search", "query": q or user_input})

        elif intent == "web_learning":
            plan["steps"].append({"action": "learn", "query": user_input})

        elif intent == "code":
            if "coloca backend" in t or "adiciona backend" in t:
                path = re.search(r'[A-Za-z]:\\[^\s]+|/[^\s]+', user_input)
                plan["steps"].append({
                    "action": "add_backend",
                    "path": path.group() if path else "",
                    "description": user_input
                })
            elif any(kw in t for kw in PROJECT_TRIGGERS):
                plan["steps"].append({
                    "action": "create_project",
                    "description": user_input
                })
            elif "clone" in t or "clonar" in t:
                url = re.search(r'https?://\S+', user_input)
                plan["steps"].append({"action": "clone_site",
                                      "url": url.group() if url else ""})
            else:
                lang = "python"
                for l in ["javascript","js","react","html","css","java","typescript"]:
                    if l in t: lang = l; break
                plan["steps"].append({"action": "generate_code",
                                      "description": user_input, "language": lang})

        elif intent == "system":
            if any(w in t for w in ["hora","horas","que horas","que dia","data"]):
                plan["steps"].append({"action": "get_time"})
            elif any(w in t for w in ["screenshot","print","tira foto"]):
                plan["steps"].append({"action": "screenshot"})
            elif any(w in t for w in ["info","cpu","ram"]):
                plan["steps"].append({"action": "system_info"})
            elif "volume" in t:
                n = re.search(r'\d+', user_input)
                plan["steps"].append({"action": "set_volume",
                                      "level": int(n.group()) if n else 50})
            elif any(w in t for w in ["spotify","música","musica","playlist",
                                       "toca","pause","pausar"]):
                act = "open"
                if "pause" in t or "pausar" in t: act = "pause"
                elif any(w in t for w in ["próxima","proxima","next"]): act = "next"
                elif "anterior" in t: act = "prev"
                query = user_input
                for w in ["jarvis","toca","coloca","bota","spotify","música",
                           "musica","playlist","abre","abrir"]:
                    query = query.lower().replace(w, "").strip()
                plan["steps"].append({"action": "spotify",
                                      "spotify_action": act, "query": query})
            elif any(w in t for w in ["fechar","fecha","encerrar"]):
                target = user_input
                for w in ["fechar","fecha","encerrar","jarvis"]:
                    target = target.lower().replace(w, "").strip()
                plan["steps"].append({"action": "kill_process", "target": target})
            elif any(w in t for w in ["abrir","abre","abra","iniciar","inicia"]):
                target = user_input
                for w in ["abrir","abre","abra","iniciar","inicia","jarvis","por favor"]:
                    target = target.lower().replace(w, "").strip()
                plan["steps"].append({"action": "open_app", "target": target})
            else:
                plan["steps"].append({"action": "execute_command", "command": user_input})

        elif intent == "computer":
            plan["steps"].append({"action": "control", "command": user_input})

        elif intent == "memory":
            if any(w in t for w in ["minhas memórias","o que você sabe","o que lembra"]):
                plan["steps"].append({"action": "get_facts"})
            else:
                plan["steps"].append({"action": "save_fact", "text": user_input})

        elif intent == "web":
            url = re.search(r'https?://\S+', user_input)
            if url:
                plan["steps"].append({"action": "open_url", "url": url.group()})
            else:
                plan["steps"].append({"action": "open_site", "url": user_input})

        else:
            plan["steps"].append({"action": "chat", "message": user_input})

        return plan

    def run(self, user_input: str) -> str:
        return self.execute(user_input)

    def execute(self, user_input: str) -> str:
        try:
            intent = self.detect_intent(user_input)
            self._last_agent = intent
            plan = self.create_plan(intent, user_input)
            result = self.router.execute_plan(plan)
            if isinstance(result, dict):
                return result.get("result", str(result))
            return str(result) if result else "Concluído."
        except Exception as e:
            return f"Erro: {e}"

_inst = None
def _get():
    global _inst
    if _inst is None: _inst = Orchestrator()
    return _inst

def execute_user_request(text: str) -> str: return _get().execute(text)
def create_plan(intent: str, text: str) -> dict: return _get().create_plan(intent, text)
