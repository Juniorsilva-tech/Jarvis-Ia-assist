"""
CodeAgent v6 — projetos completos por voz + auto-correção.
"""
import os
import subprocess
import tempfile
import re


PROJECT_KEYWORDS = [
    "site de", "site para", "sistema de", "plataforma de",
    "e-commerce", "ecommerce", "loja virtual", "loja online",
    "coloca backend", "adiciona backend", "faz um site",
    "cria um site", "desenvolve um site", "desenvolva um site",
    "cria um sistema", "faz um sistema", "mercado livre",
    "com pagamento", "com carrinho", "com agendamento",
    "fullstack", "full stack", "front end completo", "backend completo"
]


class CodeAgent:
    name = "code"

    SYSTEM = """Você é um engenheiro de software sênior especialista.
Gere código COMPLETO e FUNCIONAL. NUNCA use placeholders ou TODOs.
Implemente TODAS as funções completamente.
Retorne APENAS o código, sem markdown, sem explicações."""

    def execute(self, steps: list, raw_input: str = "") -> str:
        results = []
        for step in steps:
            action = step.get("action", "")

            if action == "generate_code":
                desc = step.get("description", raw_input)
                lang = step.get("language", self._detect_lang(desc))

                # Detecta se é pedido de projeto completo
                if self._is_project_request(desc):
                    results.append(self._build_project(desc))
                else:
                    results.append(self._generate(desc, lang))

            elif action == "create_project":
                results.append(self._build_project(
                    step.get("description", raw_input)))

            elif action == "add_backend":
                from core.automation.project_builder import add_backend_to_existing
                results.append(add_backend_to_existing(
                    step.get("path", ""), step.get("description", raw_input)))

            elif action == "run_code":
                results.append(self._run(step.get("code", "")))

            elif action in ("fix_code", "fix_file"):
                from core.automation.bug_fixer import analyze_and_fix, fix_file
                if action == "fix_file":
                    results.append(fix_file(step.get("path", "")))
                else:
                    r = analyze_and_fix(step.get("code", raw_input),
                                        error=step.get("error", ""),
                                        description=raw_input)
                    st = "Aprovado" if r["passed"] else "Falhou"
                    results.append(f"{st} ({r['attempts']} tentativas)\n```python\n{r['code'][:400]}\n```")

            elif action == "clone_site":
                from core.automation.site_cloner import clone_site
                results.append(clone_site(step.get("url", raw_input)))

            else:
                if self._is_project_request(raw_input):
                    results.append(self._build_project(raw_input))
                else:
                    results.append(self._generate(raw_input))

        return "\n".join(results) if results else "Concluído."

    def run(self, step: dict) -> dict:
        result = self.execute([step], step.get("description", step.get("query", "")))
        return {"agent": "code", "result": result}

    def _is_project_request(self, text: str) -> bool:
        t = text.lower()
        return any(kw in t for kw in PROJECT_KEYWORDS)

    def _build_project(self, description: str) -> str:
        from core.automation.project_builder import build_project
        return build_project(description)

    def _detect_lang(self, text: str) -> str:
        t = text.lower()
        for lang in ["javascript", "typescript", "react", "html", "css",
                     "java", "bash", "sql"]:
            if lang in t: return lang
        return "python"

    def _generate(self, desc: str, lang: str = "python") -> str:
        from core.models.model_router import generate_response
        from core.automation.bug_fixer import analyze_and_fix

        # Projetos grandes usam Claude
        heavy = any(w in desc.lower() for w in
                    ["completo", "sistema", "api", "autenticação", "banco de dados"])

        prompt = f"""Gere código {lang} COMPLETO e FUNCIONAL para: {desc}

OBRIGATÓRIO:
1. Código 100% funcional — sem placeholders, sem TODOs
2. Implemente TODAS as funções
3. Inclua todos os imports necessários
4. Retorne APENAS o código"""

        code = generate_response(prompt, task_type="code",
                                 system_prompt=self.SYSTEM,
                                 force_claude=heavy)

        # Limpa markdown
        if "```" in code:
            parts = code.split("```")
            if len(parts) >= 3:
                code = parts[1]
                lines = code.split("\n")
                if lines and lines[0].strip() in ("python","py","javascript",
                    "js","html","css","jsx","ts","bash","sh",""):
                    code = "\n".join(lines[1:])
        code = code.strip()

        # Auto-testa se Python
        status = ""
        if lang == "python":
            result = analyze_and_fix(code, description=desc, max_attempts=2)
            if result["passed"]:
                code = result["code"]
                status = " (testado)" if result["attempts"] > 0 else " (passou)"
            else:
                status = " (não testado)"

        # Salva
        ext_map = {"python":"py","javascript":"js","js":"js","typescript":"ts",
                   "react":"jsx","html":"html","css":"css","java":"java","bash":"sh"}
        ext = ext_map.get(lang.lower(), "txt")
        safe = re.sub(r'[^a-zA-Z0-9_-]', '_', desc[:25])
        os.makedirs("generated", exist_ok=True)
        fpath = os.path.join("generated", f"{lang}_{safe}.{ext}")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(code)

        preview = code[:400]
        return f"Código{status}: {fpath}\n\n```{lang}\n{preview}{'...' if len(code)>400 else ''}\n```"

    def _run(self, code: str) -> str:
        if not code.strip(): return "Código vazio."
        try:
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                             delete=False, encoding="utf-8") as f:
                f.write(code); tmp = f.name
            r = subprocess.run(["python", tmp], capture_output=True,
                               text=True, timeout=15, encoding="utf-8", errors="ignore")
            os.unlink(tmp)
            out = r.stdout.strip() or r.stderr.strip()
            return f"Resultado:\n{out[:500]}" if out else "Executado sem saída."
        except subprocess.TimeoutExpired:
            return "Timeout."
        except Exception as e:
            return f"Erro: {e}"
