"""
Groq Client — Jarvis
Interface direta com a API Groq. Sem imports circulares.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def generate_response(prompt: str, system_prompt: str = "", **kwargs) -> str:
    """
    Gera resposta via API Groq.
    Tenta SDK oficial primeiro, fallback para requests.
    """
    if not GROQ_API_KEY:
        return "❌ GROQ_API_KEY não configurado. Adicione ao arquivo .env"

    # Tenta via SDK oficial (mais estável)
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content

    except ImportError:
        pass  # SDK não instalado, usa requests
    except Exception as e:
        return f"❌ Erro Groq SDK: {e}"

    # Fallback via requests
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": GROQ_MODEL,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.7,
        }
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        result = resp.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        if "error" in result:
            return f"❌ Erro da API Groq: {result['error'].get('message', result['error'])}"
        return "❌ Resposta inesperada da API Groq"

    except requests.Timeout:
        return "❌ Timeout na conexão com Groq"
    except Exception as e:
        return f"❌ Erro na conexão: {e}"
