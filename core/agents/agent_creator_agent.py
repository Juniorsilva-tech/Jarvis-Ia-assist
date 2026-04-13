import os


class AgentCreatorAgent:

    name = "agent_creator"

    def run(self, step):

        agent_name = step.get("name")
        description = step.get("description")

        if not agent_name:
            return {
                "agent": "agent_creator",
                "result": "Nome do agente não fornecido."
            }

        class_name = agent_name.capitalize() + "Agent"

        code = f'''
class {class_name}:

    name = "{agent_name}"

    def run(self, step):

        query = step.get("query", "")

        return {{
            "agent": "{agent_name}",
            "result": "Agente {agent_name} executou com query: " + str(query)
        }}
'''

        path = f"core/agents/{agent_name}_agent.py"

        try:

            with open(path, "w", encoding="utf-8") as f:
                f.write(code)

            return {
                "agent": "agent_creator",
                "result": f"Novo agente criado em {path}"
            }

        except Exception as e:

            return {
                "agent": "agent_creator",
                "result": f"Erro ao criar agente: {str(e)}"
            }