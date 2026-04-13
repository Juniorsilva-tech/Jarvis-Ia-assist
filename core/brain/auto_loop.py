import time
from core.brain.orchestrator import execute_user_request


def run_auto_learning():

    topics = [
        "inteligência artificial",
        "python programação",
        "engenharia de software",
        "machine learning"
    ]

    while True:

        for topic in topics:

            print(f"Aprendendo: {topic}")

            execute_user_request(f"aprenda profundamente {topic}")

            time.sleep(10)

        time.sleep(3600)