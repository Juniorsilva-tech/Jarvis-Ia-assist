"""
Skill Learner - Jarvis
Jarvis aprende novas skills dinamicamente:
baixa documentação, processa e armazena como conhecimento interno.
"""

import json
import requests
from pathlib import Path
from datetime import datetime

SKILLS_FILE = "memory/skills.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Skills disponíveis para aprender
SKILL_SOURCES = {
    "react": "https://react.dev/learn",
    "tailwind": "https://tailwindcss.com/docs/utility-first",
    "node": "https://nodejs.org/en/learn/getting-started/introduction-to-nodejs",
    "fastapi": "https://fastapi.tiangolo.com/tutorial/",
    "python": "https://docs.python.org/3/tutorial/",
    "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
    "typescript": "https://www.typescriptlang.org/docs/handbook/intro.html",
    "git": "https://git-scm.com/docs",
    "docker": "https://docs.docker.com/get-started/",
    "sql": "https://www.w3schools.com/sql/sql_intro.asp",
}


def _load_skills() -> dict:
    if not Path(SKILLS_FILE).exists():
        return {"skills": {}, "last_updated": {}}
    try:
        return json.loads(Path(SKILLS_FILE).read_text(encoding="utf-8"))
    except Exception:
        return {"skills": {}, "last_updated": {}}


def _save_skills(data: dict):
    Path(SKILLS_FILE).parent.mkdir(parents=True, exist_ok=True)
    Path(SKILLS_FILE).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def learn_skill(skill_name: str) -> str:
    """
    Jarvis aprende uma skill nova:
    1. Acessa a documentação oficial
    2. Extrai o conteúdo essencial
    3. Processa com IA para criar um resumo de conhecimento
    4. Salva na memória de skills
    """
    from core.models.groq_client import generate_response

    skill_lower = skill_name.lower()
    url = SKILL_SOURCES.get(skill_lower)

    content = ""
    if url:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            # Extrai texto simples removendo HTML
            import re
            text = re.sub(r'<[^>]+>', ' ', resp.text)
            text = re.sub(r'\s+', ' ', text).strip()
            content = text[:3000]
        except Exception:
            content = ""

    # Cria conhecimento com IA
    prompt = f"""Você é um especialista em {skill_name}.
{f'Documentação oficial (trecho): {content}' if content else ''}

Crie um guia de referência rápida em português sobre {skill_name} com:
1. O que é e para que serve (2 linhas)
2. Comandos/sintaxe mais importantes (lista)
3. 3 exemplos práticos comentados
4. Dicas e boas práticas (lista)

Seja técnico e direto. Este guia será usado por Jarvis para responder perguntas."""

    knowledge = generate_response(prompt, task_type="analysis")

    # Salva
    data = _load_skills()
    data["skills"][skill_lower] = {
        "name": skill_name,
        "knowledge": knowledge,
        "source": url or "conhecimento interno",
        "learned_at": datetime.now().isoformat()
    }
    data["last_updated"][skill_lower] = datetime.now().isoformat()
    _save_skills(data)

    return f"✅ Skill aprendida: {skill_name}\n\n{knowledge[:500]}..."


def get_skill_knowledge(skill_name: str) -> str:
    """Retorna o conhecimento armazenado sobre uma skill."""
    data = _load_skills()
    skill = data["skills"].get(skill_name.lower())
    if not skill:
        return ""
    return skill["knowledge"]


def list_skills() -> str:
    """Lista todas as skills que Jarvis já aprendeu."""
    data = _load_skills()
    if not data["skills"]:
        return "Ainda não aprendi nenhuma skill. Peça para eu aprender algo!"
    lines = ["🧠 Skills que já aprendi:"]
    for name, info in data["skills"].items():
        date = info.get("learned_at", "")[:10]
        lines.append(f"  • {info['name']} (aprendido em {date})")
    return "\n".join(lines)


def auto_learn_from_question(question: str) -> str:
    """
    Detecta se uma pergunta envolve uma tecnologia e aprende sobre ela
    automaticamente se ainda não souber.
    """
    tech_keywords = {
        "react": ["react", "jsx", "useState", "useEffect", "componente react"],
        "tailwind": ["tailwind", "tw-", "className"],
        "node": ["node.js", "nodejs", "npm", "express"],
        "python": ["python", "pip", "django", "flask", "fastapi"],
        "javascript": ["javascript", "js", "async", "await", "promise"],
        "typescript": ["typescript", "ts", "interface", "type"],
        "git": ["git", "commit", "branch", "merge", "pull request"],
        "docker": ["docker", "container", "dockerfile", "image"],
        "sql": ["sql", "select", "insert", "database", "query"],
    }

    question_lower = question.lower()
    data = _load_skills()

    for skill, keywords in tech_keywords.items():
        if any(kw in question_lower for kw in keywords):
            if skill not in data["skills"]:
                # Aprende em background
                return learn_skill(skill)
            else:
                return get_skill_knowledge(skill)
    return ""
