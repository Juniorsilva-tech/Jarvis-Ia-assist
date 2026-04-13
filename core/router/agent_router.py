class AgentRouter:

    def __init__(self, agents: dict):
        self.agents = agents

    def execute_plan(self, plan: dict):
        agent_name = plan.get("agent")

        if agent_name not in self.agents:
            return {"agent": agent_name, "result": f"Agente '{agent_name}' não encontrado."}

        agent = self.agents[agent_name]
        steps = plan.get("steps", [])
        raw_input = plan.get("raw_input", "")

        try:
            # Suporta tanto execute(steps, raw_input) quanto run(step)
            if hasattr(agent, "execute"):
                return agent.execute(steps, raw_input)
            elif hasattr(agent, "run") and steps:
                results = []
                for step in steps:
                    r = agent.run(step)
                    if isinstance(r, dict):
                        results.append(r.get("result", str(r)))
                    else:
                        results.append(str(r))
                return {"agent": agent_name, "result": "\n".join(results)}
            else:
                return {"agent": agent_name, "result": "Agente sem método de execução."}
        except Exception as e:
            return {"agent": agent_name, "result": f"Erro no agente {agent_name}: {e}"}
