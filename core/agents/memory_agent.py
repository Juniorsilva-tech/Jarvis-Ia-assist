class MemoryAgent:
    name = "memory"

    def execute(self, steps: list, raw_input: str = "") -> str:
        from core.memory.memory_manager import save_memory, search_memory, get_facts
        results = []
        for step in steps:
            action = step.get("action", "")
            if action in ("save_fact", "store"):
                text = step.get("text", raw_input)
                save_memory(text)
                results.append(f"Memorizado: {text[:80]}")
            elif action == "get_facts":
                facts = get_facts()
                if facts:
                    results.append("Memórias:\n" + "\n".join(f"- {f['text'][:80]}" for f in facts[-8:]))
                else:
                    results.append("Nenhuma memória ainda.")
            elif action in ("search_memory", "search"):
                query = step.get("query", raw_input)
                ctx = search_memory(query)
                results.append("Encontrado:\n" + "\n".join(ctx) if ctx else "Nada encontrado.")
        return "\n".join(results) if results else "Operação de memória concluída."

    def run(self, step: dict) -> dict:
        result = self.execute([step])
        return {"agent": "memory", "result": result}
