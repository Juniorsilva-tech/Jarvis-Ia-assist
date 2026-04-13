"""
Jarvis HUD Ultra v5 — Flask + Wake Word + TTS + polling
"""
import sys, os, threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from flask import Flask, request, jsonify, send_from_directory
from core.brain.orchestrator import execute_user_request
from core.memory.memory_manager import init_memory

init_memory()
app = Flask(__name__, static_folder=".")

_wake_queue = []
_lock = threading.Lock()

def _on_wake(text: str):
    print(f"[Wake] {text}")
    resp = execute_user_request(text)
    with _lock:
        _wake_queue.append({"user": text, "response": resp})
    try:
        from voice.tts import speak
        threading.Thread(target=speak, args=(resp,), daemon=True).start()
    except Exception:
        pass

def _start_wake():
    try:
        from voice.wake_word import start
        start(_on_wake)
    except Exception as e:
        print(f"Wake word indisponivel: {e}")

threading.Thread(target=_start_wake, daemon=True).start()

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/jarvis", methods=["POST"])
def jarvis():
    data = request.get_json()
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"response": "Mensagem vazia."})
    try:
        result = execute_user_request(message)
        try:
            from voice.tts import speak
            threading.Thread(target=speak, args=(result,), daemon=True).start()
        except Exception:
            pass
        return jsonify({"response": str(result)})
    except Exception as e:
        return jsonify({"response": f"Erro: {e}"})

@app.route("/time")
def get_time():
    from datetime import datetime
    n = datetime.now()
    return jsonify({"time": n.strftime("%H:%M"), "date": n.strftime("%d/%m/%Y")})

@app.route("/wake_poll")
def wake_poll():
    with _lock:
        msgs = list(_wake_queue)
        _wake_queue.clear()
    return jsonify({"messages": msgs})

@app.route("/status")
def status():
    from core.models.model_router import is_ollama_running
    return jsonify({"ollama": is_ollama_running()})

if __name__ == "__main__":
    print("Jarvis em http://localhost:5000")
    print("Diga 'Jarvis [comando]' a qualquer momento.")
    app.run(port=5000, debug=False, threaded=True)
