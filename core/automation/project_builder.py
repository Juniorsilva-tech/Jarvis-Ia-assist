"""
Project Builder v2 — Jarvis
Gera projetos web completos por voz.
Exemplos:
- "cria um site de roupas com carrinho e pagamento"
- "faz um site de mecânica com agendamento"
- "coloca backend no meu site que está em /caminho"
- "desenvolve um e-commerce estilo Mercado Livre"
Usa Claude Sonnet 4.6 para projetos grandes.
"""
import os
import json
import subprocess


SYSTEM_PROJECT = """Você é um arquiteto de software sênior especialista em desenvolvimento web full-stack.
Você desenvolve projetos completos, bem organizados e funcionais.
Sempre gera código real, sem placeholders, sem TODOs.
Pense como um CTO — organize o projeto, escolha as tecnologias certas, gere tudo necessário."""


def _ai(prompt: str, heavy: bool = False) -> str:
    from core.models.model_router import generate_response
    return generate_response(
        prompt,
        task_type="project" if heavy else "code",
        system_prompt=SYSTEM_PROJECT,
        use_cache=False,
        force_claude=heavy
    )


def _save(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _open_vscode(path: str):
    try:
        subprocess.Popen(f'code "{path}"', shell=True)
    except Exception:
        pass


def parse_project_request(user_input: str) -> dict:
    """Extrai informações do pedido de voz."""
    from core.models.model_router import generate_response
    prompt = f"""Analise este pedido de desenvolvimento de software e extraia as informações em JSON:

Pedido: "{user_input}"

Retorne APENAS um JSON com:
{{
  "tipo": "frontend" | "backend" | "fullstack" | "ecommerce" | "landing",
  "tema": "nome do negócio/tema (ex: loja de roupas, mecânica, igreja)",
  "features": ["lista de funcionalidades pedidas"],
  "tecnologias": {{
    "frontend": "react ou html/css/js",
    "backend": "node/express ou python/fastapi ou none",
    "banco": "postgresql ou mongodb ou sqlite ou none",
    "pagamento": true ou false
  }},
  "nome_projeto": "nome-do-projeto-em-kebab-case",
  "complexidade": "simples" | "media" | "complexa"
}}

Seja preciso. Se mencionar pagamento, Stripe, MercadoPago → pagamento: true."""
    try:
        resp = generate_response(prompt, task_type="plan", use_cache=False)
        if "```" in resp:
            resp = resp.split("```")[1]
            if resp.startswith("json\n"): resp = resp[5:]
        return json.loads(resp.strip())
    except Exception:
        return {
            "tipo": "fullstack",
            "tema": user_input,
            "features": ["página principal", "sobre", "contato"],
            "tecnologias": {"frontend": "html/css/js", "backend": "none",
                           "banco": "none", "pagamento": False},
            "nome_projeto": "meu-projeto",
            "complexidade": "media"
        }


def build_project(user_input: str) -> str:
    """Entry point principal — chamado pelo CodeAgent."""
    print(f"[ProjectBuilder] Analisando pedido: {user_input}")

    info = parse_project_request(user_input)
    nome = info.get("nome_projeto", "meu-projeto")
    tema = info.get("tema", "projeto")
    tipo = info.get("tipo", "fullstack")
    features = info.get("features", [])
    tech = info.get("tecnologias", {})
    complexo = info.get("complexidade") == "complexa" or info.get("tecnologias", {}).get("pagamento")

    base_dir = os.path.join(os.path.expanduser("~"), "Desktop", nome)
    os.makedirs(base_dir, exist_ok=True)

    partes_geradas = []

    # === FRONTEND ===
    if tipo in ("frontend", "fullstack", "ecommerce", "landing"):
        print("[ProjectBuilder] Gerando frontend...")

        fe_tech = tech.get("frontend", "html/css/js")
        fe_prompt = f"""Desenvolva o frontend COMPLETO para: {tema}

Tipo de site: {tipo}
Tecnologia: {fe_tech}
Features obrigatórias: {', '.join(features)}
{'Inclui carrinho de compras e checkout' if tech.get('pagamento') else ''}

GERE:
1. HTML completo e semântico
2. CSS moderno (responsivo, mobile-first, bonito)
3. JavaScript funcional (sem frameworks externos a menos que seja React)

O site deve parecer PROFISSIONAL, com:
- Header com logo e navegação
- Seções bem definidas
- Footer completo
- Design moderno (cores, tipografia, espaçamento)
- Totalmente responsivo

Retorne os arquivos no formato:
===FILE: index.html===
(conteúdo completo)
===FILE: style.css===
(conteúdo completo)
===FILE: script.js===
(conteúdo completo)"""

        fe_result = _ai(fe_prompt, heavy=complexo)
        _save_files(base_dir, fe_result)
        partes_geradas.append("Frontend")

    # === BACKEND ===
    if tipo in ("backend", "fullstack", "ecommerce") and tech.get("backend") != "none":
        print("[ProjectBuilder] Gerando backend...")

        be_tech = tech.get("backend", "node/express")
        db = tech.get("banco", "sqlite")
        pagamento = tech.get("pagamento", False)

        be_prompt = f"""Desenvolva o backend COMPLETO para: {tema}

Tecnologia: {be_tech}
Banco de dados: {db}
Features: {', '.join(features)}
{'Integração com pagamento (MercadoPago ou Stripe)' if pagamento else ''}

GERE código COMPLETO incluindo:
1. Servidor principal (app.js ou main.py)
2. Rotas/endpoints da API REST
3. Modelos do banco de dados
4. Autenticação JWT (login/registro)
5. {'Integração de pagamento com código real' if pagamento else 'CRUD completo'}
6. Middleware de segurança (CORS, validação)
7. Arquivo de configuração (.env.example)
8. package.json ou requirements.txt

Retorne os arquivos no formato:
===FILE: backend/server.js===
(conteúdo)
===FILE: backend/routes/api.js===
(conteúdo)
===FILE: backend/.env.example===
(conteúdo)"""

        be_result = _ai(be_prompt, heavy=True)
        _save_files(base_dir, be_result)
        partes_geradas.append("Backend")

    # === README ===
    readme = f"""# {tema}

Projeto gerado pelo Jarvis AI.

## Estrutura
{tipo.upper()} — {', '.join(features[:5])}

## Como rodar
"""
    if tech.get("backend") != "none":
        readme += """
### Backend
```bash
cd backend
npm install   # ou pip install -r requirements.txt
npm start     # ou python main.py
```
"""
    readme += """
### Frontend
Abra `index.html` no navegador ou use Live Server no VS Code.
"""
    _save(os.path.join(base_dir, "README.md"), readme)

    # Abre no VS Code
    _open_vscode(base_dir)

    return (f"Projeto '{tema}' criado com sucesso!\n"
            f"Partes: {', '.join(partes_geradas)}\n"
            f"Local: {base_dir}\n"
            f"Abrindo no VS Code...")


def _save_files(base_dir: str, content: str):
    """Salva arquivos a partir do formato ===FILE: caminho===."""
    import re
    parts = re.split(r'===FILE:\s*(.+?)===', content)
    # parts = [antes, nome1, conteudo1, nome2, conteudo2, ...]
    i = 1
    while i < len(parts) - 1:
        filename = parts[i].strip()
        file_content = parts[i + 1].strip()
        # Remove markdown se vier
        if file_content.startswith("```"):
            lines = file_content.split("\n")
            file_content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        full_path = os.path.join(base_dir, filename)
        _save(full_path, file_content)
        print(f"[ProjectBuilder] Salvo: {filename}")
        i += 2


def add_backend_to_existing(project_path: str, description: str = "") -> str:
    """Adiciona backend a um projeto frontend existente."""
    if not os.path.exists(project_path):
        return f"Caminho não encontrado: {project_path}"

    # Lê o frontend existente
    frontend_files = {}
    for f in ["index.html", "style.css", "script.js"]:
        fp = os.path.join(project_path, f)
        if os.path.exists(fp):
            with open(fp, encoding="utf-8", errors="ignore") as file:
                frontend_files[f] = file.read()[:500]

    prompt = f"""Analise este frontend existente e crie um backend Node.js/Express completo para ele.

{description}

Frontend existente (preview):
{json.dumps({k: v[:200] for k,v in frontend_files.items()}, ensure_ascii=False)}

Gere backend completo com:
1. server.js com Express
2. Rotas da API conectadas ao frontend
3. Banco de dados SQLite simples
4. package.json

Formato:
===FILE: backend/server.js===
(conteúdo)
===FILE: backend/package.json===
(conteúdo)"""

    result = _ai(prompt, heavy=True)
    _save_files(project_path, result)
    _open_vscode(project_path)
    return f"Backend adicionado em: {project_path}"
