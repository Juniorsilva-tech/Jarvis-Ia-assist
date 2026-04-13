from core.memory.memory_manager import save_memory


def learn_from_feedback(user_input, response):

    save_memory({
        "type": "feedback",
        "user": user_input,
        "response": response
    })

    return "Aprendi com esse feedback."