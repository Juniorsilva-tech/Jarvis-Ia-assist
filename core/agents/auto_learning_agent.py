from core.memory.memory_manager import save_memory
from core.agents.web_learning_agent import WebLearningAgent


class AutoLearningAgent:

    name = "auto_learn"

    def __init__(self):
        self.web = WebLearningAgent()

    def run(self, step):

        query = step.get("query")

        result = self.web.run({"query": query})

        content = result.get("result", "")

        save_memory(content)

        return {
            "agent": "auto_learn",
            "result": "Aprendi e salvei conhecimento com sucesso."
        }