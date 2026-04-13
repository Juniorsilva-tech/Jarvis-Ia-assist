import json
from core.models.groq_client import generate_response


def clean_json(text):
    # remove markdown ```json ``` 
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]

    text = text.replace("json", "").strip()

    return text


def create_plan(user_input):
    prompt = f"""
Você é um sistema de planejamento de IA.

Transforme o comando do usuário em JSON estruturado.

Ações possíveis:
- open_app (target)
- search_web (query)
- create_file (name)
- run_code (code)

Retorne apenas JSON válido (SEM ``` e sem explicação).

Exemplo:
{{
  "steps": [
    {{"action": "open_app", "target": "chrome"}},
    {{"action": "search_web", "query": "treino de peito"}}
  ]
}}

Comando:
{user_input}
"""

    response = generate_response(prompt)

    print("🧠 RESPOSTA BRUTA:", response)

    try:
        clean = clean_json(response)
        plan = json.loads(clean)

        print("✅ PLANO:", plan)

        return plan

    except Exception as e:
        print("❌ ERRO AO PARSEAR JSON:", e)
        return {"steps": []}