class AgentRouter:

    def __init__(self, agents: dict):
        self.agents = agents

    def execute_plan(self, plan: dict):

        agent_name = plan.get("agent")

        if agent_name not in self.agents:
            return {
                "error": f"Agent '{agent_name}' não encontrado"
            }

        agent = self.agents[agent_name]

        steps = plan.get("steps", [])

        result = None

        for step in steps:
            try:
                result = agent.run(step)
            except Exception as e:
                return {
                    "error": str(e)
                }

        return result