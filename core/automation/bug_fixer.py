"""
Bug Fixer v2 — ciclo completo: gera → testa → corrige → re-testa.
Máximo 3 tentativas de correção automática.
"""
import subprocess
import tempfile
import os


def run_code(code: str, language: str = "python") -> dict:
    """Executa código e retorna resultado + se passou."""
    if language != "python":
        return {"passed": True, "output": "Execução apenas para Python.", "error": ""}
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w",
                                         delete=False, encoding="utf-8") as f:
            f.write(code)
            tmp = f.name
        r = subprocess.run(["python", tmp], capture_output=True,
                           text=True, timeout=15, encoding="utf-8", errors="ignore")
        os.unlink(tmp)
        passed = r.returncode == 0
        return {"passed": passed, "output": r.stdout.strip(), "error": r.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"passed": False, "output": "", "error": "Timeout — código demorou mais de 15s."}
    except Exception as e:
        return {"passed": False, "output": "", "error": str(e)}


def fix_code(code: str, error: str, description: str = "") -> str:
    """Usa IA para corrigir o código com base no erro."""
    from core.models.model_router import generate_response
    prompt = f"""Corrija este código Python. O erro é:
{error}

Código com erro:
{code[:2000]}

{"Objetivo original: " + description if description else ""}

REGRAS:
1. Retorne APENAS o código corrigido, sem markdown
2. Implemente tudo completamente, sem placeholders
3. O código deve rodar sem erros"""
    return generate_response(prompt, task_type="code")


def analyze_and_fix(code: str, language: str = "python",
                    error: str = "", description: str = "",
                    max_attempts: int = 3) -> dict:
    """
    Ciclo completo:
    1. Testa o código
    2. Se falhar, corrige com IA
    3. Re-testa
    4. Repete até passar ou atingir max_attempts
    """
    current_code = code
    attempts = []

    for i in range(max_attempts + 1):
        result = run_code(current_code, language)

        if result["passed"]:
            return {
                "passed": True,
                "code": current_code,
                "attempts": i,
                "output": result["output"],
                "explanation": f"Passou na tentativa {i}." if i > 0 else "Código funcionou de primeira."
            }

        err = result["error"] or error
        attempts.append({"attempt": i, "error": err})

        if i < max_attempts:
            print(f"[BugFixer] Tentativa {i+1}/{max_attempts} — corrigindo...")
            fixed = fix_code(current_code, err, description)
            # Limpa markdown se vier
            if "```" in fixed:
                parts = fixed.split("```")
                if len(parts) >= 3:
                    fixed = parts[1]
                    lines = fixed.split("\n")
                    if lines and lines[0].strip() in ("python","py",""):
                        fixed = "\n".join(lines[1:])
            current_code = fixed.strip()

    return {
        "passed": False,
        "code": current_code,
        "attempts": max_attempts,
        "output": "",
        "explanation": f"Não conseguiu corrigir após {max_attempts} tentativas."
    }


def fix_file(path: str) -> str:
    """Lê um arquivo Python, testa e corrige automaticamente."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        return f"Erro ao ler arquivo: {e}"

    result = analyze_and_fix(code, description=f"Arquivo: {path}")

    if result["passed"]:
        with open(path, "w", encoding="utf-8") as f:
            f.write(result["code"])
        return f"Arquivo corrigido e salvo: {path} ({result['attempts']} tentativas)"
    else:
        return f"Não conseguiu corrigir {path}: {result['explanation']}"
