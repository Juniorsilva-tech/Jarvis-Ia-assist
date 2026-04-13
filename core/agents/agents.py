"""
Agentes especializados do Jarvis v3
5 agentes originais + PCAgent + CodeAgent turbinado + SkillAgent
"""

import os
import webbrowser
import subprocess
from typing import Optional


# ─── Base ─────────────────────────────────────────────────────────────────────

class BaseAgent:
    name = "base"
    def execute(self, steps: list, raw_input: str = "") -> str:
        raise NotImplementedError


# ─── System Agent ─────────────────────────────────────────────────────────────

class SystemAgent(BaseAgent):
    name = "system"

    APP_MAP = {
        "chrome": "start chrome",
        "edge": "start msedge",
        "firefox": "start firefox",
        "notepad": "notepad",
        "bloco": "notepad",
        "calc": "calc",
        "calculadora": "calc",
        "explorer": "explorer",
        "word": "start winword",
        "excel": "start excel",
        "vscode": "code .",
        "code": "code .",
        "terminal": "start cmd",
        "cmd": "start cmd",
        "powershell": "start powershell",
        "spotify": "start spotify",
        "discord": "start discord",
        "whatsapp": "start whatsapp",
    }

    def execute(self, steps: list, raw_input: str = "") -> str:
        results = []
        for step in steps:
            results.append(self._handle(step.get("action", ""), step))
        return "\n".join(results) if results else "Executado."

    def _handle(self, action: str, step: dict) -> str:
        if action == "open_app":
            return self._open_app(step.get("target", ""))
        elif action == "search_web":
            q = step.get("query", "")
            webbrowser.open(f"https://www.google.com/search?q={q}")
            return f"🔍 Pesquisando: {q}"
        elif action == "run_command":
            return self._run_cmd(step.get("command", ""))
        elif action == "open_file":
            path = step.get("path", "")
            try:
                os.startfile(path)
                return f"📁 Abrindo: {path}"
            except Exception as e:
                return f"❌ {e}"
        elif action == "get_time":
            from core.pc.pc_controller import get_time
            return get_time()
        elif action == "screenshot":
            from core.pc.pc_controller import take_screenshot
            return take_screenshot()
        elif action == "system_info":
            from core.pc.pc_controller import get_system_info
            return get_system_info()
        elif action == "set_volume":
            from core.pc.pc_controller import set_volume
            return set_volume(int(step.get("level", 50)))
        elif action == "spotify":
            from core.pc.pc_controller import control_spotify
            return control_spotify(step.get("spotify_action", "play"), step.get("query", ""))
        elif action == "list_files":
            from core.pc.pc_controller import list_files
            return list_files(step.get("path", "."))
        elif action == "kill_process":
            from core.pc.pc_controller import kill_process
            return kill_process(step.get("target", ""))
        return f"⚠️ Ação não reconhecida: {action}"

    def _open_app(self, target: str) -> str:
        t = target.lower()
        for key, cmd in self.APP_MAP.items():
            if key in t:
                os.system(cmd)
                return f"✅ Abrindo {target}"
        os.system(f"start {target}")
        return f"✅ Tentando abrir: {target}"

    def _run_cmd(self, cmd: str) -> str:
        if not cmd:
            return "❌ Comando vazio"
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            return r.stdout or r.stderr or "Executado."
        except subprocess.TimeoutExpired:
            return "⚠️ Timeout"
        except Exception as e:
            return f"❌ {e}"


# ─── Web Agent ────────────────────────────────────────────────────────────────

class WebAgent(BaseAgent):
    name = "web"

    def execute(self, steps: list, raw_input: str = "") -> str:
        results = []
        for step in steps:
            action = step.get("action", "")
            if action == "search_web":
                results.append(self._search(step.get("query", raw_input)))
            elif action == "clone_site":
                from core.automation.site_cloner import clone_site
                results.append(clone_site(step.get("url", raw_input)))
            elif action == "fetch_url":
                results.append(self._fetch(step.get("url", "")))
            elif action == "open_url":
                webbrowser.open(step.get("url", ""))
                results.append(f"🌐 Abrindo URL")
        return "\n".join(results) if results else "Busca realizada."

    def _search(self, query: str) -> str:
        result = self._ddg(query)
        if result:
            return result
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"🔍 Pesquisando: {query}"

    def _ddg(self, query: str) -> Optional[str]:
        try:
            import requests
            r = requests.get(
                f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1",
                timeout=5, headers={"User-Agent": "Jarvis/3.0"}
            )
            data = r.json()
            abstract = data.get("AbstractText", "")
            if abstract:
                return f"🔍 {query}:\n{abstract[:400]}"
            related = data.get("RelatedTopics", [])
            if related and isinstance(related[0], dict):
                text = related[0].get("Text", "")
                if text:
                    return f"🔍 {query}:\n{text[:300]}"
        except Exception:
            pass
        return None

    def _fetch(self, url: str) -> str:
        try:
            import requests
            from bs4 import BeautifulSoup
            r = requests.get(url, timeout=10, headers={"User-Agent": "Jarvis/3.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style"]): tag.decompose()
            return f"🌐 {url}:\n{soup.get_text(separator=' ', strip=True)[:600]}"
        except Exception as e:
            return f"❌ {e}"


# ─── Code Agent ───────────────────────────────────────────────────────────────

class CodeAgent(BaseAgent):
    name = "code"

    def execute(self, steps: list, raw_input: str = "") -> str:
        results = []
        for step in steps:
            action = step.get("action", "")
            if action == "generate_code":
                results.append(self._generate(
                    step.get("description", raw_input),
                    step.get("language", "python")
                ))
            elif action == "run_code":
                results.append(self._run(step.get("code", "")))
            elif action == "fix_code":
                from core.automation.bug_fixer import analyze_and_fix
                r = analyze_and_fix(step.get("code", raw_input),
                                    step.get("language", "python"),
                                    step.get("error", ""))
                status = "✅ Testes passaram" if r["passed"] else "⚠️ Testes falharam"
                results.append(f"{status}\n{r['explanation']}\n\n```python\n{r['fixed_code'][:400]}\n```")
            elif action == "fix_file":
                from core.automation.bug_fixer import fix_file
                results.append(fix_file(step.get("path", "")))
            elif action == "create_project":
                results.append(self._create_project(step, raw_input))
            elif action == "clone_site":
                from core.automation.site_cloner import clone_site
                results.append(clone_site(step.get("url", raw_input)))
        return "\n".join(results) if results else "Tarefa concluída."

    def _generate(self, desc: str, lang: str = "python") -> str:
        from core.models.groq_client import generate_response
        prompt = f"""Especialista em {lang}. Gere código limpo e funcional.
Retorne APENAS o código, sem markdown.
Tarefa: {desc}"""
        code = generate_response(prompt, task_type="code")
        if "```" in code:
            parts = code.split("```")
            if len(parts) >= 2:
                code = parts[1]
                if "\n" in code:
                    first = code[:code.index("\n")]
                    if first.strip() in ("python","javascript","js","ts","jsx","html","css"):
                        code = code[code.index("\n")+1:]
        ext = {"python":"py","javascript":"js","typescript":"ts","html":"html",
               "css":"css","jsx":"jsx","java":"java"}.get(lang,"txt")
        safe = desc[:20].replace(" ","_").replace("/","_")
        fname = f"generated_{lang}_{safe}.{ext}"
        os.makedirs("generated", exist_ok=True)
        fpath = os.path.join("generated", fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(code.strip())
        preview = code.strip()[:300]
        return f"✅ Código gerado: {fpath}\n\n```{lang}\n{preview}\n```"

    def _run(self, code: str) -> str:
        if not code.strip():
            return "❌ Código vazio"
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".py",mode="w",delete=False,encoding="utf-8") as f:
                f.write(code); tmp=f.name
            r = subprocess.run(["python",tmp],capture_output=True,text=True,timeout=15)
            os.unlink(tmp)
            return f"▶️ {r.stdout or r.stderr or '(sem saída)'}".strip()[:500]
        except subprocess.TimeoutExpired:
            return "⚠️ Timeout"
        except Exception as e:
            return f"❌ {e}"

    def _create_project(self, step: dict, raw_input: str) -> str:
        from core.automation.project_generator import (
            generate_react_project, generate_node_project, generate_python_project
        )
        ptype = step.get("type", "python").lower()
        name  = step.get("name", "meu_projeto")
        desc  = step.get("description", raw_input)
        if "react" in ptype:
            return generate_react_project(name, desc)
        elif "node" in ptype or "express" in ptype:
            return generate_node_project(name, desc)
        else:
            return generate_python_project(name, desc)


# ─── Memory Agent ─────────────────────────────────────────────────────────────

class MemoryAgent(BaseAgent):
    name = "memory"

    def __init__(self, memory_manager=None):
        self.memory = memory_manager

    def execute(self, steps: list, raw_input: str = "") -> str:
        results = []
        for step in steps:
            action = step.get("action", "")
            if action == "save_fact":
                text = step.get("text", raw_input)
                if self.memory: self.memory.save_fact(text)
                results.append(f"🧠 Memorizado: {text}")
            elif action == "get_facts":
                if self.memory:
                    facts = self.memory.get_facts()
                    if facts:
                        results.append("📌 Memórias:\n" + "\n".join(f"- {f['text']}" for f in facts[-10:]))
                    else:
                        results.append("📌 Nenhuma memória ainda.")
            elif action == "search_memory":
                query = step.get("query", raw_input)
                if self.memory:
                    ctx = self.memory.get_relevant_context(query)
                    results.append(f"🔎 Memória:\n{ctx[:500]}" if ctx else "🔎 Nada encontrado.")
            elif action == "get_routine":
                from core.learning.routine_learner import get_routine_summary
                results.append(get_routine_summary())
            elif action == "list_skills":
                from core.skills.skill_learner import list_skills
                results.append(list_skills())
        return "\n".join(results) if results else "Operação de memória concluída."


# ─── Chat Agent ───────────────────────────────────────────────────────────────

class ChatAgent(BaseAgent):
    name = "chat"

    SYSTEM = """Você é Jarvis, assistente IA pessoal altamente inteligente e prestativo.
Responda sempre em português brasileiro.
Seja direto, claro e útil. Máximo 3 parágrafos.
Nunca diga que não pode ajudar — sempre tente contribuir."""

    def execute(self, steps: list, raw_input: str = "") -> str:
        from core.models.groq_client import generate_response
        message = raw_input
        context = ""
        for step in steps:
            if step.get("action") == "chat":
                message = step.get("message", raw_input)
            if step.get("context"):
                context = step["context"]

        # Injeta conhecimento de skill se relevante
        from core.skills.skill_learner import auto_learn_from_question
        skill_knowledge = auto_learn_from_question(message)

        prompt = ""
        if context:
            prompt += f"Contexto da memória:\n{context}\n\n"
        if skill_knowledge:
            prompt += f"Conhecimento técnico relevante:\n{skill_knowledge[:500]}\n\n"
        prompt += f"Pergunta: {message}"

        return generate_response(prompt, task_type="chat", system_prompt=self.SYSTEM)


# ─── Skill Agent ──────────────────────────────────────────────────────────────

class SkillAgent(BaseAgent):
    """Jarvis aprende novas skills dinamicamente."""
    name = "skill"

    def execute(self, steps: list, raw_input: str = "") -> str:
        from core.skills.skill_learner import learn_skill, list_skills
        results = []
        for step in steps:
            action = step.get("action", "")
            if action == "learn":
                skill = step.get("skill", raw_input)
                results.append(learn_skill(skill))
            elif action == "list":
                results.append(list_skills())
        return "\n".join(results) if results else "Skill Agent pronto."
