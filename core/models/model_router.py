"""
Model Router v6 — Jarvis
Ordem:
- Chat/simples  → Ollama (mistral) → Groq 8b
- Código médio  → Ollama (codellama) → Groq 70b
- Projeto PESADO → Groq 70b → Claude Sonnet 4.6
"""
import os, hashlib, requests
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
OLLAMA_URL       = os.getenv("OLLAMA_URL", "http://localhost:11434")
ANTHROPIC_KEY    = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL  = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
OPENROUTER_KEY   = os.getenv("OPENROUTER_API_KEY", "")

OLLAMA_TASK_MODEL = {
    "code":     os.getenv("OLLAMA_CODE_MODEL",  "codellama"),
    "chat":     os.getenv("OLLAMA_CHAT_MODEL",  "mistral"),
    "analysis": os.getenv("OLLAMA_ANALYSIS_MODEL", "llama3"),
    "heavy":    os.getenv("OLLAMA_HEAVY_MODEL", "llama3"),
    "plan":     os.getenv("OLLAMA_PLAN_MODEL",  "mistral"),
}

GROQ_TASK_MODEL = {
    "code":     "llama-3.3-70b-versatile",
    "chat":     "llama-3.1-8b-instant",
    "analysis": "llama-3.3-70b-versatile",
    "heavy":    "llama-3.3-70b-versatile",
    "plan":     "llama-3.1-8b-instant",
    "project":  "llama-3.3-70b-versatile",
}

_cache: dict = {}

def _key(p): return hashlib.md5(p[:400].encode()).hexdigest()
def _from_cache(p): return _cache.get(_key(p))
def _to_cache(p, r):
    if len(_cache) >= 300: del _cache[next(iter(_cache))]
    _cache[_key(p)] = r

def is_ollama_running() -> bool:
    try:
        requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return True
    except Exception:
        return False

def _available_ollama() -> list:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return [m["name"].split(":")[0] for m in r.json().get("models", [])]
    except Exception:
        return []

def _best_ollama(task: str) -> str:
    preferred = OLLAMA_TASK_MODEL.get(task, "mistral")
    available = _available_ollama()
    if not available: return preferred
    for m in [preferred, "llama3", "mistral", "codellama"]:
        if m in available: return m
    return available[0]

def _ollama(prompt: str, task: str = "chat", system: str = "") -> str:
    model = _best_ollama(task)
    full = f"{system}\n\n{prompt}" if system else prompt
    r = requests.post(f"{OLLAMA_URL}/api/generate",
        json={"model": model, "prompt": full, "stream": False,
              "options": {"temperature": 0.7, "num_predict": 2048}}, timeout=120)
    r.raise_for_status()
    resp = r.json().get("response", "").strip()
    if resp: print(f"[Ollama:{model}]")
    return resp

def _groq(prompt: str, task: str = "chat", system: str = "") -> str:
    if not GROQ_API_KEY: raise ValueError("GROQ_API_KEY não configurado")
    model = GROQ_TASK_MODEL.get(task, "llama-3.1-8b-instant")
    msgs = []
    if system: msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    try:
        from groq import Groq
        resp = Groq(api_key=GROQ_API_KEY).chat.completions.create(
            model=model, messages=msgs, max_tokens=2048, temperature=0.7)
        print(f"[Groq:{model}]")
        return resp.choices[0].message.content
    except ImportError:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}",
                     "Content-Type": "application/json"},
            json={"model": model, "messages": msgs, "max_tokens": 2048}, timeout=30)
        result = r.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        raise RuntimeError(str(result.get("error", result)))

def _claude(prompt: str, system: str = "") -> str:
    """Claude Sonnet 4.6 via Anthropic API — para projetos grandes e complexos."""
    if not ANTHROPIC_KEY:
        raise ValueError("ANTHROPIC_API_KEY não configurado no .env")
    msgs = [{"role": "user", "content": prompt}]
    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 4096,
        "messages": msgs,
    }
    if system:
        payload["system"] = system
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=payload,
        timeout=60
    )
    result = r.json()
    if "content" in result:
        print(f"[Claude:{ANTHROPIC_MODEL}]")
        return result["content"][0]["text"]
    raise RuntimeError(str(result.get("error", result)))

def _openrouter(prompt: str, system: str = "") -> str:
    if not OPENROUTER_KEY: raise ValueError("OPENROUTER_API_KEY não configurado")
    msgs = []
    if system: msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": prompt})
    r = requests.post("https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}",
                 "Content-Type": "application/json"},
        json={"model": "meta-llama/llama-3.2-3b-instruct:free",
              "messages": msgs, "max_tokens": 2048}, timeout=30)
    result = r.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    raise RuntimeError(str(result))

def generate_response(prompt: str, task_type: str = "chat",
                      system_prompt: str = "", use_cache: bool = True,
                      force_claude: bool = False) -> str:
    cached = _from_cache(prompt) if use_cache else None
    if cached:
        print("[Cache]")
        return cached

    result = None
    errors = []

    # Projetos grandes → Claude primeiro se tiver API key
    if force_claude or task_type == "project":
        if ANTHROPIC_KEY:
            try:
                result = _claude(prompt, system_prompt)
            except Exception as e:
                errors.append(f"Claude: {e}")
        if not result:
            try:
                result = _groq(prompt, task_type, system_prompt)
            except Exception as e:
                errors.append(f"Groq: {e}")
    else:
        # Ollama primeiro (sem gastar tokens)
        if is_ollama_running():
            try:
                result = _ollama(prompt, task_type, system_prompt)
            except Exception as e:
                errors.append(f"Ollama: {e}")
        # Groq fallback
        if not result and GROQ_API_KEY:
            try:
                result = _groq(prompt, task_type, system_prompt)
            except Exception as e:
                errors.append(f"Groq: {e}")
        # OpenRouter último recurso
        if not result and OPENROUTER_KEY:
            try:
                result = _openrouter(prompt, system_prompt)
            except Exception as e:
                errors.append(f"OpenRouter: {e}")

    if not result:
        return f"Todos os modelos falharam: {'; '.join(errors)}"

    if use_cache:
        _to_cache(prompt, result)
    return result
