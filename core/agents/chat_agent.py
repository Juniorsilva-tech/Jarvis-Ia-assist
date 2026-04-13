"""
ChatAgent v5 — memória conversacional, personalidade consistente.
"""

class ChatAgent:
    name = "chat"
    _history = []  # histórico da sessão

    SYSTEM = """Você é Jarvis, assistente IA pessoal avançado e inteligente.
Responda sempre em português brasileiro.
Seja direto, preciso e útil. Máximo 3 parágrafos.
Você tem acesso ao PC do usuário, pode abrir apps, gerar código, buscar na web e controlar o sistema.
Lembre do contexto da conversa."""

    def execute(self, steps: list, raw_input: str = "") -> str:
        from core.models.model_router import generate_response
        message = raw_input
        for step in steps:
            if step.get("action") == "chat":
                message = step.get("message", raw_input)

        # Memória relevante
        context = ""
        try:
            from core.memory.memory_manager import search_memory
            mems = search_memory(message)
            if mems:
                context = "Memória relevante:\n" + "\n".join(mems[:2]) + "\n\n"
        except Exception:
            pass

        # Histórico conversacional (últimas 4 trocas)
        hist = ""
        if self._history:
            hist = "Histórico recente:\n"
            for h in self._history[-4:]:
                hist += f"Usuário: {h['u']}\nJarvis: {h['a'][:100]}\n"
            hist += "\n"

        prompt = hist + context + f"Usuário: {message}"
        response = generate_response(prompt, task_type="chat", system_prompt=self.SYSTEM)

        # Salva no histórico
        self._history.append({"u": message, "a": response})
        if len(self._history) > 20:
            self._history.pop(0)

        # Aprende hábitos
        try:
            from core.learning.routine_learner import record_action
            record_action(message)
        except Exception:
            pass

        return response

    def run(self, step: dict) -> dict:
        return {"agent": "chat", "result": self.execute([step], step.get("message", ""))}
