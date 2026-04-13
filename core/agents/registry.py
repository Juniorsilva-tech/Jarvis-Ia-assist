from core.agents.chat_agent import ChatAgent
from core.agents.browser_agent import BrowserAgent
from core.agents.code_agent import CodeAgent
from core.agents.computer_agent import ComputerAgent
from core.agents.memory_agent import MemoryAgent
from core.agents.system_agent import SystemAgent
from core.agents.web_agent import WebAgent
from core.agents.web_learning_agent import WebLearningAgent
from core.agents.agent_creator_agent import AgentCreatorAgent
from core.agents.auto_learning_agent import AutoLearningAgent



def get_agents():


    agents = {}

    agents["auto_learn"] = AutoLearningAgent()
    
    try:
        agents["agent_creator"] = AgentCreatorAgent()
    except Exception as e:
        print("Erro ao carregar AgentCreatorAgent:", e)

    try:
        agents["chat"] = ChatAgent()
    except Exception as e:
        print("Erro ao carregar ChatAgent:", e)

    try:
        agents["browser"] = BrowserAgent()
    except Exception as e:
        print("Erro ao carregar BrowserAgent:", e)

    try:
        agents["code"] = CodeAgent()
    except Exception as e:
        print("Erro ao carregar CodeAgent:", e)

    try:
        agents["computer"] = ComputerAgent()
    except Exception as e:
        print("Erro ao carregar ComputerAgent:", e)

    try:
        agents["memory"] = MemoryAgent()
    except Exception as e:
        print("Erro ao carregar MemoryAgent:", e)

    try:
        agents["system"] = SystemAgent()
    except Exception as e:
        print("Erro ao carregar SystemAgent:", e)

    try:
        agents["web"] = WebAgent()
    except Exception as e:
        print("Erro ao carregar WebAgent:", e)

    try:
        agents["web_learning"] = WebLearningAgent()
    except Exception as e:
        print("Erro ao carregar WebLearningAgent:", e)

    return agents